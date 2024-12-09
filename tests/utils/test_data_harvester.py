import os
import shutil
import random
import cv2


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
    Saves files to the destination directory with modified names (slashes replaced by underscores).
    
    Args:
        file_paths (list[str]): Relative paths of the files to be saved.
        destination_dir (str): The directory where the files will be saved.
    """
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    
    for src_path in file_paths:
        # Create the new filename
        new_name = src_path.replace(os.sep, "|")
        dest_path = os.path.join(destination_dir, new_name)
        
        # Copy the file to the destination directory with the new name
        shutil.copy(src_path, dest_path)
        print(f"Copied: {src_path} -> {dest_path}")

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


src_folder = "/app/db/fifa/session_stats"
staging_folder = "/app/db/fifa/raw_images"
dest_folder = "/app/db/fifa/raw_images_processed"

jpg_files = find_jpg_files(src_folder)

sample_size = 500
# jpg_files = random.sample(jpg_files, sample_size)

save_files_with_new_names(jpg_files, staging_folder)

preprocess_directory(staging_folder, dest_folder)

 
