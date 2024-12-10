from datetime import datetime, timedelta
import json
import os
import shutil
from PIL import Image
from easyocr import Reader


import cv2
import pandas as pd

from constants import JOB_CONFIG, OUTPUT_PATH, PAGE_ID_LABEL, SESSION_STATS_JSON_FILENAME


def extract_stats_from_sliced_images(images_dir: str, reader: Reader) -> dict:
    """Extracts stats from a single match and match type (i.e. SHOOTING)"""
    stats = {}
    for filename in os.listdir(images_dir):
        if filename.endswith(".jpg") and not filename.startswith("EA SPORTS FC"):
            if filename == "PAGE_ID.jpg":
                pass
            else:
                allowlist = get_allowed_chars_by_filename(filename)

                # Load the image
                img_path = os.path.join(images_dir, filename)
                img = cv2.imread(img_path)

                extracted_text = extract_text(reader, img, allowlist)
                print(f"File: {filename}, Text: {extracted_text}")
                stats[filename.replace(".jpg", "")] = extracted_text
    return stats


def extract_stat_dict():
    final_stats = {}
    for match_folder in os.listdir(OUTPUT_PATH):
        final_stats[match_folder] = {}
        for page_folder in os.listdir(os.path.join(OUTPUT_PATH, match_folder)):
            stat_dir = os.path.join(OUTPUT_PATH, match_folder, page_folder)
            if os.path.isdir(stat_dir):
                stats_file_path = os.path.join(stat_dir, "_stats.json")

                with open(stats_file_path, "r") as file:
                    data = json.load(file)
                final_stats[match_folder][page_folder] = data
    return final_stats


def extract_text(
    reader: Reader,
    img: cv2.typing.MatLike,
    allowed_chars,
):

    # extract numerical values (stats)
    # img = Image.open(img_path)

    # # # Preprocess the image to maximize contrast
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    # enhanced_img = clahe.apply(gray)
    # Convert to grayscale
    # gray_image = ImageOps.grayscale(img)

    # # Enhance contrast
    # enhancer = ImageEnhance.Contrast(gray_image)
    # contrast_image = enhancer.enhance(2)  # Increase contrast by a factor of 2

    # # Convert to OpenCV format for further processing
    # opencv_image = np.array(contrast_image)

    # # Apply thresholding to make the text stand out
    # _, thresh_image = cv2.threshold(opencv_image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # # Display the processed image to check the preprocessing result
    # plt.figure(figsize=(6,6))
    # plt.imshow(thresh_image, cmap='gray')
    # plt.axis('off')
    # plt.show()
    # print(thresh_image)
    # Perform OCR using EasyOCR, restricting characters to numbers, ".", and ":"
    result = reader.readtext(
        img,
        allowlist=allowed_chars,
        text_threshold=0.01,
        low_text=0.1,
    )

    # Extract and join the recognized text
    extracted_text = "".join([detection[1] for detection in result])

    return extracted_text


def slice_image_and_save(
    image_path: str, bounding_boxes_df: pd.DataFrame, dest_dir: str
):
    image = Image.open(image_path)

    # Iterate over the dataframe and extract images
    for _, row in bounding_boxes_df.iterrows():
        label_name = row["label_name"]
        bbox_x = int(row["bbox_x"])
        bbox_y = int(row["bbox_y"])
        bbox_width = int(row["bbox_width"])
        bbox_height = int(row["bbox_height"])

        # Crop the image
        cropped_image = image.crop(
            (bbox_x, bbox_y, bbox_x + bbox_width, bbox_y + bbox_height)
        )

        # Save the cropped image
        cropped_image.save(os.path.join(dest_dir, f"{label_name}.jpg"))
        print(f"Saved {label_name}.jpg")

    print("All images extracted and saved.")


def determine_page_type_by_image(image_path: str, reader: Reader) -> dict:
    # get summary page
    dummy_config = determine_page_type_by_page_id_label_text("DRIBBLE SUCCESS RATE")[
        "bb_file"
    ]
    df = pd.read_csv(dummy_config)
    label_df = df[df["label_name"] == PAGE_ID_LABEL]
    for index, row in label_df.iterrows():  # only 1 row
        label_name = row["label_name"]
        bbox_x = int(row["bbox_x"])
        bbox_y = int(row["bbox_y"])
        bbox_width = int(row["bbox_width"])
        bbox_height = int(row["bbox_height"])
    image = Image.open(image_path)
    cropped_image = image.crop(
        (bbox_x, bbox_y, bbox_x + bbox_width, bbox_y + bbox_height)
    )

    # Save the cropped image
    img_path = "/tmp/page_type.jpg"
    cropped_image.save(img_path)
    img = cv2.imread(img_path)
    result = reader.readtext(
        img,
        allowlist=set("DRIBBLE TACKLE SUCCESS RATE SHOT ACCURACY PASS "),
        text_threshold=0.01,
        low_text=0.1,
    )

    # Extract and join the recognized text
    extracted_text = "".join([detection[1] for detection in result])
    page_type = determine_page_type_by_page_id_label_text(extracted_text)
    os.remove(img_path)

    print(f"we're currently parsing '{page_type['type_name']}' page type")
    return page_type

def get_allowed_chars_by_filename(filename: str): 
    # DEFENDING
    defending_ints = ['STANDING_TACKLES_AWAY',
        'INTERCEPTIONS_AWAY',
        'AERIAL_DUELS_WON_AWAY',
        'DEFENSIVE_DUELS_WON_HOME',
        'STANDING_TACKLES_WON_HOME',
        'BEATEN_BY_OPPONENT_HOME',
        'FOULS_COMMITTED_AWAY',
        'BLOCKS_HOME',
        'STANDING_TACKLES_WON_AWAY',
        'PENALTIES_COMMITTED_AWAY',
        'OFFENSIVE_DUELS_WON_HOME',
        'SLIDING_TACKLES_AWAY',
        'RED_CARDS_HOME',
        'SLIDING_TACKLES_HOME',
        'PENALTIES_COMMITTED_HOME',
        'OFFENSIVE_DUELS_WON_AWAY',
        'BLOCKS_AWAY',
        'BEATEN_BY_OPPONENT_AWAY',
        'STANDING_TACKLES_HOME',
        'CLEARANCES_HOME',
        'CLEARANCES_AWAY',
        'DEFENSIVE_DUELS_WON_AWAY',
        'RED_CARDS_AWAY',
        'SAVES_AWAY',
        'YELLOW_CARDS_HOME',
        'SLIDING_TACKLES_WON_AWAY',
        'INTERCEPTIONS_HOME',
        'YELLOW_CARDS_AWAY',
        'SAVES_HOME',
        'SLIDING_TACKLES_WON_HOME',
        'AERIAL_DUELS_WON_HOME',
        'FOULS_COMMITTED_HOME'
    ] 
    defending_floats =  []
    defending_percentage = ['TACKLE_SUCCESS_RATE_HOME', 'TACKLE_SUCCESS_RATE_AWAY']
    defending_text = []
    defending_timespan = []
    
    # PASSING 
    passing_ints = ['PASS_AND_GO_HOME', 'CROSS_HOME', 'LOBBED_THROUGH_AWAY', 'KEY_PASS_HOME', 'BREAKAWAY_HOME', 'GROUND_HOME', 'KEY_PASS_AWAY', 'BREAKAWAY_AWAY', 'DOWN_WING_AWAY', 'OFFSIDE_AWAY', 'TOTAL_PASSES_AWAY', 'THROUGH_HOME', 'SET_PIECES_HOME', 'COMPLETED_HOME', 'OTHER_HOME', 'FIRST_TIME_HOME', 'FIRST_TIME_AWAY', 'LOB_AWAY', 'THROUGH_AWAY', 'OTHER_AWAY', 'OFFSIDE_HOME', 'DOWN_WING_HOME', 'INTERCEPTED_AWAY', 'CROSS_AWAY', 'GROUND_AWAY', 'SET_PIECES_AWAY', 'COMPLETED_AWAY', 'PASS_AND_GO_AWAY', 'TOTAL_PASSES_HOME', 'LOBBED_THROUGH_HOME', 'LOB_HOME', 'INTERCEPTED_HOME'] 
    passing_floats =  []
    passing_percentage = []
    passing_text = []
    passing_timespan = []
    
    # SHOOTING 
    shooting_ints = ['POWER_AWAY', 'CHIP_AWAY', 'FINESSE_HOME', 'BLOCKED_AWAY', 'NORMAL_HOME', 'INSIDE_THE_BOX_AWAY', 'CHIP_HOME', 'HEADER_AWAY', 'OFF_TARGET_HOME', 'FINESSE_AWAY', 'HEADER_HOME', 'FAR_SIDE_HOME', 'SET_PIECES_HOME', 'VOLLEY_HOME', 'ON_TARGET_HOME', 'NEAR_SIDE_HOME', 'FAR_SIDE_AWAY', 'TOTAL_SHOTS_AWAY', 'SET_PIECES_AWAY', 'POWER_HOME', 'OFF_TARGET_AWAY', 'INSIDE_THE_BOX_HOME', 'OUTSIDE_THE_BOX_AWAY', 'ON_TARGET_AWAY', 'TOTAL_SHOTS_HOME', 'VOLLEY_AWAY', 'BLOCKED_HOME', 'OUTSIDE_THE_BOX_HOME', 'NORMAL_AWAY', 'NEAR_SIDE_AWAY']
    shooting_ints_with_blank_possibility = ['INSIDE_THE_BOX_GOALS_HOME', 'FAR_SIDE_GOALS_HOME', 'INSIDE_THE_BOX_GOALS_AWAY', 'FINESSE_GOALS_AWAY', 'CHIP_GOALS_HOME', 'VOLLEY_GOALS_HOME', 'NORMAL_GOALS_HOME', 'SET_PIECES_GOALS_AWAY', 'OUTSIDE_THE_BOX_GOALS_HOME', 'OUTSIDE_THE_BOX_GOALS_AWAY', 'NORMAL_GOALS_AWAY', 'SET_PIECES_GOALS_HOME', 'CHIP_GOALS_AWAY', 'FINESSE_GOALS_HOME', 'POWER_GOALS_HOME', 'POWER_GOALS_AWAY', 'HEADER_GOALS_HOME', 'HEADER_GOALS_AWAY', 'FAR_SIDE_GOALS_AWAY', 'NEAR_SIDE_GOALS_AWAY', 'NEAR_SIDE_GOALS_HOME', 'VOLLEY_GOALS_AWAY']
    shooting_floats =  []
    shooting_percentage = []
    shooting_text = []
    shooting_timespan = []
    
    # SUMMARY 
    summary_ints = ['PASSES_HOME', 'INTERCEPTIONS_AWAY', 'YELLOW_CARDS_AWAY', 'PENALTY_KICKS_HOME', 'SAVES_HOME', 'SHOTS_HOME', 'SCORE_AWAY', 'POSSESSION_AWAY', 'CORNERS_HOME', 'FOULS_COMMITTED_AWAY', 'TACKLES_HOME', 'CORNERS_AWAY', 'SCORE_HOME', 'TACKLES_WON_HOME', 'PENALTY_KICKS_AWAY', 'TACKLES_AWAY', 'OFFSIDES_HOME', 'FOULS_COMMITTED_HOME', 'FREE_KICKS_HOME', 'SHOTS_AWAY', 'TACKLES_WON_AWAY', 'BALL_RECOVERY_TIME_HOME', 'BALL_RECOVERY_TIME_AWAY', 'OFFSIDES_AWAY', 'SAVES_AWAY', 'POSSESSION_HOME', 'YELLOW_CARDS_HOME', 'PASSES_AWAY', 'INTERCEPTIONS_HOME', 'FREE_KICKS_AWAY']
    summary_floats =  ['EXPECTED_GOALS_AWAY', 'EXPECTED_GOALS_HOME']
    summary_percentage = ['PASS_ACCURACY_HOME', 'DRIBBLE_SUCCESS_RATE_HOME', 'PASS_ACCURACY_AWAY', 'SHOT_ACCURACY_AWAY', 'SHOT_ACCURACY_HOME', 'DRIBBLE_SUCCESS_RATE_AWAY']
    summary_text = ['TEAM_HOME', 'TEAM_AWAY', "PAGE_ID"]
    summary_timespan = ['TOTAL_MATCH_TIME']

    ints = defending_ints + passing_ints + shooting_ints + summary_ints
    floats = defending_floats + passing_floats + shooting_floats + summary_floats
    percentages = defending_percentage + passing_percentage + shooting_percentage + summary_percentage
    texts = defending_text + passing_text + shooting_text + summary_text
    timespans = defending_timespan + passing_timespan + shooting_timespan + summary_timespan
    if any(substring in filename for substring in shooting_ints_with_blank_possibility): # edge case: goals can be empty
        return "0123456789 "
    elif any(substring in filename for substring in ints): # int
        return "0123456789"
    elif any(substring in filename for substring in floats): # float
        return "0123456789."
    elif any(substring in filename for substring in texts): # text
        return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    elif any(substring in filename for substring in percentages): # percentages
        return "0123456789%"
    elif any(substring in filename for substring in timespans): # timespans
        return "0123456789:"
    else:
        raise ValueError(f"UNKNOWN FILE TYPE: {filename}")
    # return (
    #     "0123456789.:%" if filename not in ["TEAM_HOME.jpg", "TEAM_AWAY.jpg", "PAGE_ID.jpg"] else None
    # )


def get_datetime_from_filename(filename: str):
    filename_no_ext = filename.replace(".jpg", "")
    # Extract the datetime portion from the string (the last 14 characters)
    datetime_str = filename_no_ext[-14:]

    # Parse the datetime string into a Python datetime object
    dt = datetime.strptime(datetime_str, "%Y%m%d%H%M%S")

    return dt

def check_next_index(session_date, folder_index, job_config):
    # Base case: if the next index is not in the missed_match_indices, return the current offset
    if session_date not in job_config or folder_index not in job_config[session_date]["missed_match_indices"]:
        return folder_index
    
    # If the current index is found, increment the folder_index and offset, then check recursively
    print(f"No match stats are available for match on index {folder_index} on {session_date}. Setting i={folder_index+1}...")
    folder_index += 1
    return check_next_index(session_date, folder_index + 1, job_config)


def partition_by_game(source_path: str, staging_path: str):
    files_in_directory = os.listdir(source_path)
    # Filter only .jpg files
    jpg_files = [f for f in files_in_directory if f.endswith(".jpg")]

    # Step 1: Check if the number of .jpg files is divisible by 4
    if len(jpg_files) % 4 != 0:
        raise ValueError(
            f"The number of .jpg files ({len(jpg_files)}) is not divisible by 4."
        )

    # List to store tuples of (datetime, filename)
    files_with_datetime = []

    # Step 1: Extract and sort files by datetime
    for filename in jpg_files:
        dt = get_datetime_from_filename(filename)
        # Append tuple of (datetime, filename) to the list
        files_with_datetime.append((dt, filename))
    
    # Load job config if file exists
    job_config = {}
    if os.path.exists(JOB_CONFIG):
        with open(JOB_CONFIG, 'r') as file:
            job_config = json.load(file)

    # Step 2: Sort the files by datetime
    files_with_datetime.sort(key=lambda x: x[0])

    # Step 3: Group files into folders of 4 files each
    folder_index = 0
    batch = []
    prev_session_date = None

    for idx, (dt, filename) in enumerate(files_with_datetime):
        batch.append(filename)

        # Once we have 4 files or if it's the last file in the list
        if len(batch) == 4 or idx == len(files_with_datetime) - 1:
                
            session_date = (dt - timedelta(hours=10)).strftime("%Y-%m-%d")
            if session_date != prev_session_date:
                folder_index = 0
            # Check if the date is in the dictionary and if the integer is in the missed_match_indices list
            if session_date in job_config and folder_index in job_config[session_date]["missed_match_indices"]:
                print(f"No match stats are available for match on index {folder_index} on {session_date}. setting i={folder_index+1}...")
                folder_index = check_next_index(session_date, folder_index, job_config)

            # Create a folder name using the first file's date in the batch and the folder index
            folder_name = dt.strftime(f"{session_date}-{folder_index}")
            folder_path = os.path.join(staging_path, folder_name)

            # Create the folder
            os.makedirs(folder_path, exist_ok=True)

            # Move the 4 files into this folder
            for file in batch:
                source_file = os.path.join(source_path, file)
                destination_file = os.path.join(folder_path, file)
                shutil.copy(source_file, destination_file)

            print(f"Moved files to folder: {folder_name}")

            # Clear the batch and increment the folder index
            batch = []
            folder_index += 1
            prev_session_date = session_date


def determine_page_type_by_page_id_label_text(label_value: str):
    if label_value == "DRIBBLE SUCCESS RATE":
        return {
            "type_name": "SUMMARY",
            "bb_file": "annotation-export/ps5-fc24-3840x2160/summary/labels_my-project-name_2024-08-20-09-56-41.csv",
        }
    if label_value == "TACKLE SUCCESS RATE":
        return {
            "type_name": "DEFENDING",
            "bb_file": "annotation-export/ps5-fc24-3840x2160/defending/labels_my-project-name_2024-08-20-09-54-24.csv",
        }
    elif label_value == "SHOT ACCURACY":
        return {
            "type_name": "SHOOTING",
            "bb_file": "annotation-export/ps5-fc24-3840x2160/shooting/labels_my-project-name_2024-08-20-10-02-32.csv",
        }
    elif label_value == "PASS ACCURACY" or label_value == "PASSACCURACY" or label_value == "UPASSACCURACY":
        return {
            "type_name": "PASSING",
            "bb_file": "annotation-export/ps5-fc24-3840x2160/passing/labels_my-project-name_2024-08-20-09-28-47.csv",
        }
    else:
        raise ValueError(f"Unknown page type: {label_value}")

def add_session_details(df: pd.DataFrame):
    df['DATE'] = pd.to_datetime(df['DATE'])
    # Subtract 10 hours and extract the date
    df['Session_Adjusted_Date'] = (df['DATE'] - pd.Timedelta(hours=10)).dt.date
    return df

def parse_session_stats(directory):
    # Define the file path for the JSON file
    json_file = os.path.join(directory, SESSION_STATS_JSON_FILENAME)

    # Load the JSON file
    with open(json_file, "r") as f:
        data = json.load(f)

    # Initialize dictionaries to hold the parsed data for each section
    summary_data = []
    defending_data = []
    passing_data = []
    shooting_data = []

    # Iterate through the JSON data
    for match_id_key, match_data in data.items():
        # Extract MATCH_ID by splitting on "-" and taking the last element
        match_id = match_id_key.split("-")[-1]

        # Add SESSION_ID and MATCH_ID to each section and append to respective lists
        if "SUMMARY" in match_data:
            summary_row = match_data["SUMMARY"]
            summary_row["MATCH_ID"] = match_id
            summary_data.append(summary_row)

        if "DEFENDING" in match_data:
            defending_row = match_data["DEFENDING"]
            defending_row["MATCH_ID"] = match_id
            defending_data.append(defending_row)

        if "PASSING" in match_data:
            passing_row = match_data["PASSING"]
            passing_row["MATCH_ID"] = match_id
            passing_data.append(passing_row)

        if "SHOOTING" in match_data:
            shooting_row = match_data["SHOOTING"]
            shooting_row["MATCH_ID"] = match_id
            shooting_data.append(shooting_row)

    # Convert each list of data to a pandas DataFrame
    df_summary = pd.DataFrame(summary_data)
    df_summary = add_session_details(df_summary)
    df_defending = pd.DataFrame(defending_data)
    df_defending = add_session_details(df_defending)
    df_passing = pd.DataFrame(passing_data)
    df_passing = add_session_details(df_passing)
    df_shooting = pd.DataFrame(shooting_data)
    df_shooting = add_session_details(df_shooting)

    return df_summary, df_defending, df_passing, df_shooting
