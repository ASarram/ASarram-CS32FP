import sys
import os
import subprocess
from helpers import extract_features_multisegment
from matching import score_song, explain_match
from build_database import load_database


def download_from_youtube(url):
    os.makedirs("temp", exist_ok=True)

    #AI Support to help with the command, especially since errors were arising with Cookies
    output_template = "temp/%(title)s.%(ext)s"
    command = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--cookies", "cookies.txt",
        "-o", output_template,
        "--print", "after_move:filepath", # AI assistance for this to capture output path
        url
    ]
    print("Downloading audio from YouTube...")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Download failed:\n{result.stderr}")
        return None
    filepath = result.stdout.strip().splitlines()[-1]
    print(f"Downloaded: {filepath}\n")
    return filepath


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <youtube_url>")
        sys.exit(1)

    url = sys.argv[1]

    filepath = download_from_youtube(url)
    if filepath is None:
        sys.exit(1)

    features = extract_features_multisegment(filepath)
    if features is None:
        print("Could not extract features.")
        sys.exit(1)

    try:
        database = load_database()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    results = score_song(features, database)

    print("\n" + "─" * 50)
    best_style, best_confidence, best_details, _ = results[0]    
    print(explain_match(best_style, best_confidence, best_details, results))

    print("\nFull ranking:")
    for i, (style, confidence, _, __) in enumerate(results, 1):
        bar = "-" * int(confidence / 5)
        print(f"  {i}. {style.title():<12} {confidence:>5.1f}%  {bar}")

    print("─" * 50)
