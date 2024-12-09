import cv2
import easyocr
import os
import random

import pandas as pd

from utils import get_allowed_chars_by_filename

# Step 1: Run EasyOCR on all images and collect predictions and confidence scores
import os
import shutil
import cv2
import easyocr

def run_ocr_on_images(image_folder, label_folder):
    reader = easyocr.Reader(
        ['en'],
        # user_network_directory="/root/.EasyOCR/user_network/",
        recog_network='model'
    )  # Specify the language
    image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg') or f.endswith('.png')][:1000]
    results = {}

    # Create the 'unlabelled' folder if it doesn't exist
    unlabelled_folder = os.path.join(label_folder, 'unlabelled')
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
                text_threshold=0.00,
                low_text=0.1,                
                # decoder='beamsearch'
            )
        except Exception as e:
            cv2.imwrite(f"debug_{img_file}", img)
            print(f"Error processing {img_file}: {e}")
            # If there's an error, move the image to 'unlabelled'
            shutil.copy(img_path, unlabelled_folder)
            continue

        if result:
            text = result[0][1]  # Extract predicted text
            confidence = result[0][2]  # Extract confidence (if available)
            results[img_file] = {'text': text, 'confidence': confidence}

            # Create destination directory based on predicted text
            text_folder = os.path.join(label_folder, text)
            os.makedirs(text_folder, exist_ok=True)

            # Copy the image to the corresponding text folder
            shutil.copy(img_path, text_folder)
        else:
            # If no result is found, move the image to 'unlabelled'
            shutil.copy(img_path, unlabelled_folder)

    return results


# Step 2: Bin images based on confidence scores
def bin_images(results, bins=[0, 0.3, 0.6, 0.9, 1.0]):
    binned_images = {i: [] for i in range(len(bins))}
    for img, data in results.items():
        confidence = data['confidence']
        for i in range(len(bins)-1):
            if bins[i] <= confidence < bins[i+1]:
                binned_images[i].append(img)
                break
    return binned_images

# Step 3: Sample images from each bin for manual checking
def sample_images(binned_images, sample_sizes):
    sampled_images = {}
    for bin_index, size in sample_sizes.items():
        images_in_bin = binned_images[bin_index]
        sampled_images[bin_index] = random.sample(images_in_bin, min(size, len(images_in_bin)))
    return sampled_images

# Step 4: Manually check the sampled images and record correctness
# Assume manual_check_results is a dictionary with img_file as key and boolean correctness as value
manual_check_results = {
    # 'image1.jpg': True,
    # 'image2.jpg': False,
    # ...
}

# Step 5: Calculate error rates for each bin
def calculate_error_rates(sampled_images, manual_check_results):
    bin_error_rates = {}
    for bin_index, images in sampled_images.items():
        total = len(images)
        incorrect = sum(1 for img in images if not manual_check_results[img])
        error_rate = incorrect / total if total > 0 else 0
        bin_error_rates[bin_index] = error_rate
    return bin_error_rates

# Step 6: Compute weighted overall error rate
def compute_weighted_error_rate(binned_images, bin_error_rates, total_images):
    overall_error_rate = 0
    for bin_index, images in binned_images.items():
        proportion = len(images) / total_images
        error_rate = bin_error_rates.get(bin_index, 0)
        overall_error_rate += proportion * error_rate
    return overall_error_rate

# Example usage
image_folder = "/app/db/fifa/raw_images"
label_folder = "/app/db/fifa/labelled_images"
results = run_ocr_on_images(image_folder, label_folder)
binned_images = bin_images(results)
s = 0
for i in binned_images:
    l = len(binned_images[i])
    s = s + l
    print(i, l, s)
print(s)
sample_sizes = {0: 20, 1: 20, 2: 20, 3: 20, 4: 20}  # Define sample sizes for each bin
sampled_images = sample_images(binned_images, sample_sizes)
# Manually check the sampled images and populate manual_check_results
# bin_error_rates = calculate_error_rates(sampled_images, manual_check_results)
# total_images = sum(len(images) for images in binned_images.values())
# overall_error_rate = compute_weighted_error_rate(binned_images, bin_error_rates, total_images)
# print(f'Estimated Overall Error Rate: {overall_error_rate:.2%}')
print('sad')

# Convert dictionary to DataFrame
df1 = pd.DataFrame.from_dict(results, orient='index').reset_index()
df1.columns = ['filename', 'words_prediction', 'confidence']

df2 = pd.read_csv('/app/db/fifa/labelled_images/labels.csv')

# Merge on 'filename', keeping only rows that match
merged_df = pd.merge(df1, df2[['filename', 'words']], on='filename', how='inner')
merged_df["correct"] = merged_df["words"] == merged_df["words_prediction"]

merged_df.to_csv('preds.csv', index=False)