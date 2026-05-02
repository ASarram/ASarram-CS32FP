'''
Build reference database of dance style feature profiles

Expecting folders to be in following structure:
    data/
        {dance style 1}/
        {dance style 2}/
        .
        .
        .
'''

import os
import json
import librosa
from helpers import extract_features, average_features

DANCE_STYLES = ["cha cha", "samba", "rumba", "paso", "jive"]
DATA_ROOT = "data"
OUTPUT_FILE = "database.json"


def build_database(styles = DANCE_STYLES, data_root = DATA_ROOT, output_file = OUTPUT_FILE):
    style_profiles = {}

    for style in styles:
        folder = os.path.join(data_root, style)

        # make sure that the folder exists
        if not os.path.isdir(folder):
            print(f"'{folder}' not found. Add audio files and re-run")
            continue

        # check to make sure the folder contains audio files
        audio_files = [f for f in os.listdir(folder) if f.lower().endswith((".wav", ".mp3"))] # picking out the audio files
        if not audio_files:
            print(f"'{folder}' has no .wav or .mp3 files")
            continue

        print(f"\n'{style.upper()}': Processing {len(audio_files)} file(s)...")
        features_list = [] # to hold features

        for filename in audio_files:
            path = os.path.join(folder, filename)
            print(f"    Loading: {filename}")
            try:
                y, sr = librosa.load(path, sr = None, offset = 30, duration = 60)
                features = extract_features(y, sr)
                if features:
                    features_list.append(features)
                    print(f'    {features}')

            except Exception as e:
                print(f'    Could not load {filename}: {e}')

        if not features_list:
            print(f"    No valid features extracted for '{style}'; moving on")
            continue

        style_profiles[style] = average_features(features_list)
        print(f"    Profile built from {len(features_list)} samples")


    if style_profiles:
        with open(output_file, "w") as f:
            json.dump(style_profiles, f, indent = 4)
            print(f"Extraction complete: database saved to {output_file}")
    else:
        print("\nNo profiles built; database not saved")
        return style_profiles



def load_database(filepath = OUTPUT_FILE):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"'{filepath} not found")
        with open(filepath) as f:
            return json.load(f)


if __name__ == "__main__":
    build_database()

