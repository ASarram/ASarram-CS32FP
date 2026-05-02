'''
To collect data (i.e. download audios) for dance types from Youtube and save them into the /data folder

'''
import os
import subprocess
import sys

DATA_ROOT = "data"
DANCE_STYLES = ["cha cha", "samba", "rumba", "paso", "jive"]

def check_folders():
    # to create the folders within /data if they don't already exist
    for style in DANCE_STYLES:
        folder = os.path.join(DATA_ROOT, style)
        os.makedirs(folder, exist_ok = True)

def download_audio(url, style): # to download audio from URL into the correct folder as mp3
    folder = os.path.join(DATA_ROOT, style)
    os.makedirs(folder, exist_ok = True)

    print(f"Downloading file into '{folder}'")

     # yt-dlp output template: data/<style>/<title>.mp3
    output_template = os.path.join(folder, "%(title)s.%(ext)s")

    command = [
    "yt-dlp",
    "-x",
    "--audio-format", "mp3",
    "--audio-quality", "0",
    "--cookies", "cookies.txt",
    "--no-playlist",
    "-o", output_template,
    url]

    result = subprocess.run(command, capture_output=False)

    if result.returncode == 0:
        print(f"Saved to '{folder}'")
    else:
        print("Download failed - check the URL and try again")

def check_yt_dlp(): # To check that yt-dlp is installed (avoid crashing in the middle of download)
    result = subprocess.run(["yt-dlp", "--version"], capture_output=True)
    if result.returncode != 0:
        print("yt-dlp is not installed. Run:  pip install yt-dlp")
        sys.exit(1)


def choose_style():
    print(f"\nDance Styles")
    for i, style in enumerate(DANCE_STYLES, 1):
        print(f"    {i}: {style.title()}")

    while True:
        choice = input(f"\nEnter number:").strip()
        if choice.isdigit() and 1<= int(choice) <= len(DANCE_STYLES):
            return DANCE_STYLES[int(choice) - 1]
        print(f"Please enter a valid number between 1 and {len(DANCE_STYLES)}")


if __name__ == "__main__":
    check_yt_dlp()
    check_folders()

    print("=" * 40)
    print("Dance Audio Downloader (For Use in Database)")
    print("=" * 40)

    while True:
        url = input(f"\nPaste a YouTube URL (or q to quit):").strip()
        if url.lower() == "q":
            break

        if not url.startswith("http"):
            print("Must paste a valid URL")
            continue

        style = choose_style()
        download_audio(url, style)

        print("\nPress Enter to download another (or 'q' to quit)")
        check_end = input().strip().lower()
        if check_end == "q":
            break




