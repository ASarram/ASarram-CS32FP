'''
Helper functions: extract_features, extract_features_multisegment, and average_features
'''
import numpy as np
import librosa


def extract_features(y, sr):
    try:
        # tightness lowered from default (100) to allow for more flexiibility
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, start_bpm=100, tightness=80)

        # Correcting for half/double harmonic errors
        if tempo < 65:
            tempo *= 2
        elif tempo > 200:
            tempo /= 2

        energy = np.mean(librosa.feature.rms(y=y))
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        beat_strength = np.mean(onset_env)
        centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))

        beat_times = librosa.frames_to_time(beats, sr=sr)
        regularity = np.std(np.diff(beat_times)) if len(beat_times) > 1 else 0

        # update: additional features 
        rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)) 
        return {"bpm": float(tempo.item()), "energy": float(energy.item()), "beat_strength": float(beat_strength.item()), "brightness": float(centroid.item()), "regularity": float(regularity.item()), "rolloff": float(rolloff.item())}

    except Exception as e:
        print(f"Error extracting features: {e}")
        return None



def extract_features_multisegment(filepath: str, segment_duration: float = 45.0):
    # to improve detection - avoid relying on a single segment of the song (more representative)
    # segments chosen to skip first 20s (in case of intro) and last 20 seconds, then evenly space across what's left

    try:
        total_duration = librosa.get_duration(path = filepath)
    except Exception as e:
        print(f"Could not read duration: {e}")
        return None

    # skipping first and last 20s
    usable_start = 20.0
    usable_end = max(usable_start + segment_duration, total_duration - 20)
    usable_length = usable_end - usable_start

    # defining goal number of segments (3 if possible, but accounting for possibility that song is too short)
    num_segments = 3
    if usable_length < segment_duration * 2: # to check whether song is long enough
        num_segments = 1

    # spacing start points across the usable range
    if num_segments == 1:
        start_points = [usable_start]
    else:
        step = (usable_length - segment_duration) / (num_segments - 1)
        start_points = []
        for i in range(num_segments):
            start_point = usable_start + i*step
            start_points.append(start_point)


    # extracting features
    print(f"Extracting features from {num_segments} segment(s)")

    features_list = []
    for offset in start_points:
        # checking to make sure not to load past eof
        actual_duration = min(segment_duration, total_duration - offset)
        if actual_duration < 10.0:
            print(f"    Skipping segment at {offset:.0f} ({actual_duration:.0f}s, too short)")
            continue

        # extract features using defined extract_features function
        try:
            y, sr = librosa.load(filepath, sr = None, offset = offset, duration = actual_duration)
            print(f"    Segment {offset:.0f}s-{offset+actual_duration:.0f}s ", end="")
            features = extract_features(y, sr)

            if features:
                features_list.append(features)
                print(f"BPM = {features['bpm']}")
            else:
                print("Feature extraction failed; skipping")

        except Exception as e:
            print(f"    Could not load segment at {offset:.0f}s: {e}")


    if not features_list:
        print("No segments able to be extracted")
        return None

    # averaging across all the segments
    averaged_features = {}
    for key in features_list[0].keys():
        values = [f[key] for f in features_list]
        averaged_features[key] = float(np.mean(values))

    print(f"Averaged features across {len(features_list)} segment(s): {averaged_features}")
    return averaged_features




# to get 'average' features for each style
def average_features(feature_list):
    avg = {}
    stdev = {}
    for key in feature_list[0].keys():
        values = [f[key] for f in feature_list]
        avg[key] = float(np.mean(values))
        stdev[key] = float(np.std(values))
    return {"mean": avg, "stdev": stdev, "sample_count": len(feature_list)}
