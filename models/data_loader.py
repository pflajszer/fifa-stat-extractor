from datetime import datetime
import os
import re
import shutil
import random
import cv2
import easyocr
import csv
import pandas as pd

from utils import get_allowed_chars_by_filename

def generate_job_id():
    # Get the current date and time in format yyyy-mm-dd-hh-mm-ss
    job_id = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    
    # Replace any invalid characters with underscores
    job_id = re.sub('[^a-zA-Z0-9_-]', '_', job_id)
    
    return job_id

def find_jpg_files(base_directory):
    """
    Recursively finds .jpg files in a directory that do not start with "EA SPORTS FC".
    
    Args:
        base_directory (str): The directory to search.
    
    Returns:
        list[str]: Relative paths of .jpg files that do not start with "EA SPORTS FC".
    """
    matching_files = []

    for root, _, files in os.walk(base_directory):
        for file in files:
            if file.endswith(".jpg") and not file.startswith("EA SPORTS FC"):
                relative_path = os.path.join(root, file)
                matching_files.append(relative_path)

    return matching_files

def save_files_with_new_names(file_paths, destination_dir):
    """
    Saves files to the destination directory with modified names (slashes replaced by pipes).
    
    Args:
        file_paths (list[str]): Relative paths of the files to be saved.
        destination_dir (str): The directory where the files will be saved.
    """
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    
    for src_path in file_paths:
        # Create the new filename
        new_name = src_path.replace(os.sep, "^")
        dest_path = os.path.join(destination_dir, new_name)
        
        # Copy the file to the destination directory with the new name
        shutil.copy(src_path, dest_path)
        # print(f"Copied: {src_path} -> {dest_path}")

def preprocess_image(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Maximize contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_img = clahe.apply(gray)
    
    # Reduce noise
    blurred_img = cv2.GaussianBlur(enhanced_img, (5, 5), 0)
    
    # Apply adaptive thresholding
    binary_img = cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
    
    # Perform morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morphed_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)
    
    # Deskew the image
    # deskewed_img = deskew(morphed_img)
    
    return morphed_img

def preprocess_directory(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Process all .jpg and .png files in the input directory
    image_files = [f for f in os.listdir(input_directory) if f.endswith('.jpg') or f.endswith('.png')]
    
    for img_file in image_files:
        input_img_path = os.path.join(input_directory, img_file)
        output_img_path = os.path.join(output_directory, img_file)
        
        # Read the image
        img = cv2.imread(input_img_path)
        if img is None:
            print(f"Could not read image: {input_img_path}")
            continue
        
        # Preprocess the image
        preprocessed_img = preprocess_image(img)
        
        # Save the preprocessed image in the output directory
        cv2.imwrite(output_img_path, preprocessed_img)
        print(f"Processed and saved: {output_img_path}")

def prelabel_images(image_folder, label_folder, reader: easyocr.Reader, min_confidence: int = 0.9):
    image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg') or f.endswith('.png')]
    results = {}

    # Create the 'unlabelled' folder if it doesn't exist
    err_folder = os.path.join(label_folder, '_ERROR')
    os.makedirs(err_folder, exist_ok=True)
    
    unlabelled_folder = os.path.join(label_folder, '_UNLABELLED')
    os.makedirs(unlabelled_folder, exist_ok=True)

    for img_file in image_files:
        raw_img_filename = str(img_file).split("|")[-1]
        allowlist = get_allowed_chars_by_filename(raw_img_filename)
        img_path = os.path.join(image_folder, img_file)
        # Read the image
        img = cv2.imread(img_path)
        # Preprocess the image
        # preprocessed_img = preprocess_image(img)
        try:
            result = reader.readtext(
                img,
                detail=1,
                paragraph=False,
                allowlist=allowlist,
                text_threshold=min_confidence,
                # low_text=0.1,                
                # decoder='beamsearch'
            )
        except Exception as e:
            cv2.imwrite(f"debug_{img_file}", img)
            print(f"Error processing {img_file}: {e}")
            # If there's an error, move the image to 'unlabelled'
            shutil.copy(img_path, err_folder)
            # print(f"1. saved '{img_file}' to '{err_folder}'")
            continue

        if result:
            text = result[0][1]  # Extract predicted text
            confidence = result[0][2]  # Extract confidence (if available)
            results[img_file] = {'text': text, 'confidence': confidence}
            
            if text.isspace() or len(text) == 0:
                text = "_EMPTY"

            # Create destination directory based on predicted text
            text_folder = os.path.join(label_folder, text)
            os.makedirs(text_folder, exist_ok=True)

            # Copy the image to the corresponding text folder
            shutil.copy(img_path, text_folder)
            # print(f"2. saved '{img_file}' to '{text_folder}' (text: '{text}')")
        else:
            # If no result is found, move the image to 'unlabelled'
            shutil.copy(img_path, unlabelled_folder)
            # print(f"3. saved '{img_file}' to '{unlabelled_folder}'")

    return results

def create_true_label_csv(directory, output_csv):
    """
    Creates a CSV with filenames and their corresponding labels based on the directory structure.
    
    Args:
        directory (str): Path to the root directory.
        output_csv (str): Path to the output CSV file.
    """
    # Ensure the directory exists
    if not os.path.isdir(directory):
        raise ValueError(f"Provided directory '{directory}' does not exist or is not a directory.")
    
    # Initialize data collection
    data = []

    # Walk through the directory recursively
    for root, _, files in os.walk(directory):
        # Extract label (subdirectory name)
        label = os.path.basename(root)
        if label == "_ERROR" or label == "_UNLABELLED":
            continue
        if label == "_EMPTY":
            label = " "
        
        # Iterate over files in the current directory
        for file in files:
            # Build the relative path to the image
            # relative_path = os.path.relpath(os.path.join(root, file), directory)
            
            # Add to data if it's an image (based on extension)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                data.append([file, label])
    
    # Write data to CSV
    with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['filename', 'words'])  # Write header
        writer.writerows(data)  # Write rows
    
    print(f"CSV file created successfully at '{output_csv}'")

def unpack_images_to_flat_folder(directory, flat_folder):
    """
    Unpacks all images from a nested directory structure into a single flat folder.

    Args:
        directory (str): Path to the root directory with nested subdirectories.
        flat_folder (str): Path to the flat folder where images will be copied to.
    """
    # Ensure the root directory exists
    if not os.path.isdir(directory):
        raise ValueError(f"Provided directory '{directory}' does not exist or is not a directory.")
    
    # Create the flat folder if it does not exist
    os.makedirs(flat_folder, exist_ok=True)

    # Walk through the directory recursively
    for root, dirs, files in os.walk(directory, topdown=False):  # topdown=False processes child folders first
        for file in files:
            # Check if the file is an image
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                # Move the image to the flat folder
                src_path = os.path.join(root, file)
                dst_path = os.path.join(flat_folder, file)
                
                # Handle duplicate filenames by appending a counter
                counter = 1
                while os.path.exists(dst_path):
                    name, ext = os.path.splitext(file)
                    dst_path = os.path.join(flat_folder, f"{name}_{counter}{ext}")
                    counter += 1
                
                shutil.copy(src_path, dst_path)
        
    #     # Remove the empty directory
    #     for dir in dirs:
    #         dir_path = os.path.join(root, dir)
    #         if not os.listdir(dir_path):  # If the directory is empty
    #             os.rmdir(dir_path)

    # # Remove the original root directory if it is empty
    # if not os.listdir(directory):
    #     os.rmdir(directory)

    print(f"All images have been copied to a flat folder: '{flat_folder}'.")

def join_y_with_yhat_csv(y_filepath: str, yhat_filepath: str) -> None:
    df1 = pd.read_csv(yhat_filepath)
    df2 = pd.read_csv(y_filepath)
    # Merge on 'filename', keeping only rows that match
    merged_df = pd.merge(df1, df2[['filename', 'words']], on='filename', how='inner')
    merged_df["correct"] = merged_df["words"] == merged_df["words_prediction"]
    merged_df.to_csv(yhat_filepath, index=False)

def run_prelabeleing_job(base_folder: str, sample_size: int, preprocess: bool):
    """
    This functions purpose is specific to the current structure of the existing fifa-stat-extractor output structure.
    It iterates over folders to find JPG files but omitting the source files (starting with EA SPORTS FC) and only grabs the already extracted bounding boxes.
    It then creates folders staging, processed and prelabelled.
    The real value lies in the prelabelled folder which then is subject to a manual review and categorization. 
    The folders starting with "_" require extra-attention, as they are the ones the model failed to recognize. The current treshhold for the image to fall under unlabelled category is 90% confidence, so quite a tight one.
    Current model places around 50% of images in that folder.
    
    Ones the folders are correctly identified, you can run prep_for_training() function
    """
    job_id = generate_job_id()
    src_folder = "/app/db/fifa/session_stats"
    staging_folder = f"{base_folder}/{job_id}/1.staging"
    processed_folder = f"{base_folder}/{job_id}/2.processed"
    prelabelled_folder = f"{base_folder}/{job_id}/3.prelabelled"

    yhat_filepath = f"{base_folder}/{job_id}/6.yhat.csv"

    jpg_files = find_jpg_files(src_folder)
    if sample_size:
        jpg_files = random.sample(jpg_files, sample_size)

    save_files_with_new_names(jpg_files, staging_folder)

    if preprocess:
        preprocess_directory(staging_folder, processed_folder)
    else:
        processed_folder = staging_folder

    reader = easyocr.Reader(['en'])
    prelabel_images(processed_folder, prelabelled_folder, reader)

def prep_for_training(base_folder: str, job_id: str):
    """
        This functions purpose is to first create a csv file labels.csv categorizing each image based on the folder its in.
        Then it flattens the folder itself.
        It does not remove/amend any data. Instead, it creates a 'flattened' folder containing flat JPGs and labels.csv
        This format can then be passed to EasyOCR training
        
    """
    flat_folder = f"{base_folder}/{job_id}/4.flattened"
    y_filepath = f"{flat_folder}/labels.csv"
    prelabelled_folder = f"{base_folder}/{job_id}/3.prelabelled"
    unpack_images_to_flat_folder(prelabelled_folder, flat_folder)
    create_true_label_csv(prelabelled_folder, y_filepath)

# reader = easyocr.Reader(['en'], recog_network='model')

# join_y_with_yhat_csv(y_filepath, yhat_filepath)

if __name__ == "__main__":
    base_folder = f"/app/db/fifa/stat-extractor/data"
    # job_type = "prelabel"
    job_type = "train_prep"
    
    if job_type == "prelabel":
        run_prelabeleing_job(base_folder, None, False)
    elif job_type == "train_prep":
        prep_for_training(base_folder, "V1")