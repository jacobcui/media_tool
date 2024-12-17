"""
Tool to batch rename photos, convert heic to jpeg, and add date to filename.
"""
import curses
from tqdm import tqdm

import os
import datetime
from typing import Optional

import typer

import media_lib
from progressbar import ProgressBar

app = typer.Typer()


@app.command()
def process_media(
    directory: str = typer.Option(
        None, "--directory", "-d", help="Directory containing media files to process"
    ),
    video_file: Optional[str] = typer.Option(
        None, "--file", "-f", help="Single MP4 file to process"
    ),
    reduce_size: bool = typer.Option(
        False, "--reduce-size", "-r", help="Reduce video size while maintaining quality"
    ),
) -> None:
    """Process media files - either batch rename photos/videos or compress a single video."""
    if reduce_size and video_file:
        if not video_file.lower().endswith(".mp4"):
            typer.echo("Error: Input file must be an MP4 video")
            raise typer.Exit(1)

        if not os.path.exists(video_file):
            typer.echo(f"Error: File {video_file} does not exist")
            raise typer.Exit(1)

        output_file = video_file.rsplit(".", 1)[0] + "_compressed.mp4"
        try:
            # Use ffmpeg with h264 codec and crf=23 for good quality/size balance
            os.system(f'ffmpeg -i "{video_file}" -c:v libx264 -crf 23 "{output_file}"')
            typer.echo(f"Successfully compressed video to: {output_file}")
        except Exception as e:
            typer.echo(f"Error compressing video: {str(e)}")
            raise typer.Exit(1)
    elif directory:
        curses.wrapper(batch_rename_media_files, directory)
    else:
        typer.echo(
            "Error: Must provide either --directory or --file with --reduce-size"
        )
        raise typer.Exit(1)


@app.command()
def shrink_video(
    video_file: Optional[str] = typer.Option(
        None, "--file", "-f", help="Single MP4 file to process"
    ),
) -> None:
    """Process media files - either batch rename photos/videos or compress a single video."""
    if not video_file:
        typer.echo("Error: Please provide a video file using --file <video_file>")
        raise typer.Exit(1)

    if not video_file.lower().endswith(".mp4"):
        typer.echo("Error: Input file must be an MP4 video")
        raise typer.Exit(1)

    if not os.path.exists(video_file):
        typer.echo(f"Error: File {video_file} does not exist")
        raise typer.Exit(1)

    output_file = video_file.rsplit(".", 1)[0] + "_compressed.mp4"
    try:
        # Use ffmpeg with h264 codec and crf=23 for good quality/size balance
        os.system(f'ffmpeg -i "{video_file}" -c:v libx264 -crf 23 "{output_file}"')
        typer.echo(f"Successfully compressed video to: {output_file}")
    except Exception as e:
        typer.echo(f"Error compressing video: {str(e)}")
        raise typer.Exit(1)


@app.command()
def generate_subtitle(
    media_file: Optional[str] = typer.Option(
        None, "--file", "-f", help="Single MP4 or WAVfile to process"
    )
) -> None:
    """Generate subtitles from speech in video file using OpenAI Whisper.

    Example:
    media_tool generate_subtitle --file video.mp4
    """

    if not media_file:
        typer.echo("Error: Please provide a video file using --file <video_file>")
        raise typer.Exit(1)

    media_file_is_wav = media_file.lower().endswith(".wav")

    if not media_file.lower().endswith((".mp4", ".wav")):
        typer.echo("Error: Input file must be an MP4 video or WAV file")
        raise typer.Exit(1)

    if not os.path.exists(media_file):
        typer.echo(f"Error: File {media_file} does not exist")
        raise typer.Exit(1)

    try:
        # Extract audio from video
        audio_file = media_file.rsplit(".", 1)[0] + ".wav" if not media_file_is_wav else media_file
        if not media_file_is_wav:
            os.system(
                f'ffmpeg -i "{media_file}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "{audio_file}"'
            )

        # Use OpenAI Whisper for speech recognition
        # Whisper supports multilingual transcription including Chinese
        import whisper_timestamped as whisper

        model = whisper.load_model("base")
        # Set language to Chinese. If None, Whisper will auto-detect the language
        from datetime import timedelta
        result = model.transcribe(audio_file, language="zh")

        # Generate subtitle file
        subtitle_file = media_file.rsplit(".", 1)[0] + ".srt"
        with open(subtitle_file, "w", encoding="utf-8") as f:

            for i, segment in enumerate(tqdm(result["segments"], desc="Generating subtitles"), 1):
                start = str(datetime.timedelta(seconds=int(segment["start"])))
                end = str(datetime.timedelta(seconds=int(segment["end"])))
                text = segment["text"].strip()
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

        typer.echo(f"Successfully generated subtitles: {subtitle_file}")

    except Exception as e:
        typer.echo(f"Error generating subtitles: {str(e)}")
        raise typer.Exit(1)

@app.command()
def merge_video_and_subtitle(video_file: str = typer.Option(
        None, "--file", "-f", help="Single MP4 to process"
    ), subtitle_file: str = typer.Option(
        None, "--subtitle", "-s", help="Single SRT subtitle file"
    )
) -> None:
    """Merge a video file and a subtitle file."""

    if not video_file.lower().endswith(".mp4"):
        typer.echo("Error: Input file must be an MP4 video")
        raise typer.Exit(1)

    if not os.path.exists(video_file):
        typer.echo(f"Error: File {video_file} does not exist")
        raise typer.Exit(1)

    if not subtitle_file.lower().endswith(".srt"):
        typer.echo("Error: Input file must be an SRT subtitle file")
        raise typer.Exit(1)

    if not os.path.exists(subtitle_file):
        typer.echo(f"Error: File {subtitle_file} does not exist")
        raise typer.Exit(1)

    output_file = video_file.rsplit(".", 1)[0] + "_with_subtitle.mp4"

    try:
        cmd = (
            f'HandBrakeCLI -i "{video_file}" -o "{output_file}" '
            f'--srt-file "{subtitle_file}" '
            f'--srt-codeset UTF-8 '
            f'--srt-lang chi '
            f'--srt-default=1 '
            f'--srt-burn '
        )
        print(f"Executing command: {cmd}")
        os.system(cmd)

    except Exception as e:
        print(f"Error: {str(e)}")
        raise typer.Exit(1)


def datetime_to_yyyy_mm_dd(datetime_obj: datetime) -> str:
    """Convert datetime to YYYY_MM_DD format."""

    return datetime_obj.strftime("%Y_%m_%d")


def count_files(directory: str) -> int:
    """Count the number of files in a directory."""

    total_files = 0
    for _, _, files in os.walk(directory):
        total_files += len(files)
    return total_files


@app.command()
def batch_rename_media_files(directory: str) -> None:
    """Batch rename photos and movies."""

    if not directory:
        print("Error: Please provide directory using --directory <directory>.")
        raise typer.Exit(1)

    if not os.path.exists(directory):
        print(f"Error: Directory {directory} does not exist.")
        raise typer.Exit(1)

    totle_file_count = count_files(directory)
    stdscr = curses.initscr()
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

@app.command()
def cut_video(video_file: str = typer.Option(
        None, "--file", "-f", help="Single MP4 to process"
    ),
    start_time: str = typer.Option(
        None, "--start", "-s", help="Start time of the video to cut in format HH:MM:SS"
    ),
    end_time: str = typer.Option(
        None, "--end", "-e", help="End time of the video to cut in format HH:MM:SS"
    )
) -> None:
    """Cut a video file.

    Example:
    media_tool cut_video --file video.mp4 --start 00:00:00 --end 00:01:00
    """

    if not video_file:
        typer.echo("Error: Please provide a video file using --file <video_file>")
        raise typer.Exit(1)

    os.system(f'ffmpeg -i "{video_file}" -ss {start_time} -to {end_time} -c copy "{video_file.rsplit(".", 1)[0]}_cut.mp4"')


if __name__ == "__main__":
    app()
