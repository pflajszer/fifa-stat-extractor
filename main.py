import json
import shutil
import pandas as pd
from easyocr import Reader
import os

from constants import OUTPUT_PATH, SESSION_STATS_JSON_FILENAME, SOURCE_PATH
from utils import (
    determine_page_type_by_image,
    extract_stat_dict,
    extract_stats_from_sliced_images,
    get_datetime_from_filename,
    parse_session_stats,
    partition_by_game,
    slice_image_and_save,
)


if __name__ == "__main__":

    partition_by_game(SOURCE_PATH, OUTPUT_PATH)

    reader = Reader(["en"])  # this needs to run only once to load the model into memory

    match_folders = os.listdir(OUTPUT_PATH)
    for page_folder in match_folders:
        files_in_match_folder = os.listdir(os.path.join(OUTPUT_PATH, page_folder))
        match_stat_screenshots = [
            f for f in files_in_match_folder if f.endswith(".jpg")
        ]
        for match_stat_screenshot in match_stat_screenshots:

            page_type = determine_page_type_by_image(
                os.path.join(OUTPUT_PATH, page_folder, match_stat_screenshot), reader
            )

            dest_dir = os.path.join(
                OUTPUT_PATH, page_folder, page_type["type_name"]
            ).replace(".jpg", "")
            os.makedirs(dest_dir, exist_ok=True)

            df = pd.read_csv(page_type["bb_file"])

            # Load the image
            fp = os.path.join(OUTPUT_PATH, page_folder, match_stat_screenshot)

            slice_image_and_save(fp, df, dest_dir)

            stats = extract_stats_from_sliced_images(dest_dir, reader)
            stats["DATE"] = get_datetime_from_filename(fp).isoformat()

            # stats into json file
            with open(os.path.join(dest_dir, "_stats.json"), "w") as json_file:
                json.dump(stats, json_file, indent=4)

            shutil.copy(
                os.path.join(OUTPUT_PATH, page_folder, match_stat_screenshot),
                os.path.join(dest_dir, match_stat_screenshot),
            )

    # save json stats
    final_stats = extract_stat_dict()
    with open(os.path.join(OUTPUT_PATH, SESSION_STATS_JSON_FILENAME), "w") as json_file:
        json.dump(final_stats, json_file, indent=4)

    # save csv stats
    df_summary, df_defending, df_passing, df_shooting = parse_session_stats(OUTPUT_PATH)
    df_summary.to_csv(os.path.join(OUTPUT_PATH, "SUMMARY.csv"), index=False)
    df_defending.to_csv(os.path.join(OUTPUT_PATH, "DEFENDING.csv"), index=False)
    df_passing.to_csv(os.path.join(OUTPUT_PATH, "PASSING.csv"), index=False)
    df_shooting.to_csv(os.path.join(OUTPUT_PATH, "SHOOTING.csv"), index=False)
