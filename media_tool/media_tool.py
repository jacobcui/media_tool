"""
Tool to batch rename photos, convert heic to jpeg, and add date to filename.
"""
import argparse
import curses
import os
from datetime import datetime

import media_lib
from progressbar import ProgressBar


def datetime_to_yyyy_mm_dd(datetime_obj: datetime) -> str:
    """Convert datetime to YYYY_MM_DD format."""

    return datetime_obj.strftime("%Y_%m_%d")


def count_files(directory: str) -> int:
    """Count the number of files in a directory."""

    total_files = 0
    for _, _, files in os.walk(directory):
        total_files += len(files)
    return total_files


def batch_rename_media_files(stdscr: curses.window, directory: str) -> None:
    """Batch rename photos and movies."""

    totle_file_count = count_files(directory)
    progress_obj = ProgressBar(stdscr)

    for counter, filename in enumerate(os.listdir(directory)):
        counter = counter + 1
        progress_obj.print_progress_bar(
            counter,
            totle_file_count,
            prefix="Progress:",
            length=50,
            suffix=f"{counter}/{totle_file_count}",
        )

        if filename.startswith(("19", "20")):
            progress_obj.refresh()
            continue

        media_file_path = os.path.join(directory, filename)

        taken_date = None
        if filename.lower().endswith(".heic"):
            taken_date = media_lib.get_photo_taken_date(media_file_path)
            try:
                converted_jpeg_file = media_lib.convert_heic_to_jpeg(
                    media_file_path, remove_original=True
                )
                progress_obj.print_other_info(
                    f"Conversion successful: {media_file_path} -> {converted_jpeg_file}"
                )
                media_file_path = converted_jpeg_file
                filename = filename.replace(".HEIC", ".JPG")
            except media_lib.ConvertionError as e:
                progress_obj.print_other_info(
                    f"Conversion failed for {media_file_path}: {str(e)}"
                )

        elif filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
            taken_date = media_lib.get_photo_taken_date(media_file_path)
        elif filename.lower().endswith((".mov", ".mp4")):
            taken_date = media_lib.get_movie_taken_date(media_file_path)
        else:
            taken_date = None

        if taken_date:
            yyyy_mm_dd = datetime_to_yyyy_mm_dd(taken_date)

            new_filename = f"{yyyy_mm_dd}_{filename}"
            new_path = os.path.join(directory, new_filename)

            try:
                os.rename(media_file_path, new_path)
                progress_obj.print_other_info(f"Renamed: {filename} -> {new_filename}")
            except PermissionError as e:
                progress_obj.print_other_info(f"(error): {e}")

        else:
            progress_obj.print_other_info(f"No change: {media_file_path}")

        stdscr.refresh()

    progress_obj.before_exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", help="Full path.")
    args = parser.parse_args()

    if not args.directory:
        print("Error: Please provide directory using --directory <directory>.")
    elif args.directory and os.path.exists(args.directory):
        curses.wrapper(batch_rename_media_files, args.directory)
    else:
        print(f"Error: Directory {args.directory} does not exist.")
