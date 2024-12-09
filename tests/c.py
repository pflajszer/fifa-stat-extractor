import os
import csv

def create_label_csv(directory, output_csv):
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

# Example usage
create_label_csv('/app/db/fifa/labelled_images', '/app/db/fifa/labelled_images/labels.csv')
