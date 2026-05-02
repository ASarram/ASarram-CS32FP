'''
Program does the following:
    1. Compares input audio file against reference data base
    2. Determines best-matching dance style
    3. Outputs best-matching dance style with confidence score and explanation


Scoring chosen to be based off stdev of features in database (lower stdev = more reliable = more weight), and distance of input song from the database features
'''

import math
from build_database import load_database

def score_song(features, database):
    # Comparing extracted features against profile of each style in the database
    style_scores = {}

    for style, profile in database.items():
        means = profile["mean"]
        stdevs = profile["stdev"]

        total_weighted_distance = 0.0
        total_weight = 0.0
        feature_details = {}

        for feature, song_value in features.items():
            mean = means[feature]
            stdev = stdevs[feature]

            if stdev == 0:
                stdev = 1e-6  # avoid divide-by-zero if feature is perfectly consistent

            # AI assistance: capping z-score (prevent single outlying features from dominating results)
            z = min(abs(song_value - mean) / stdev, 3.0)  # standard deviations away from style mean; capped 
            weight = 1.0 / stdev                # more reliable features get higher weight
            weighted_distance = weight * z

            total_weighted_distance += weighted_distance
            total_weight += weight

            feature_details[feature] = {"song_value": song_value, "style_mean": mean, "style_stdev": stdev, "z_score": z, "weight": weight}

        #average distance (to determine how far input song is from the style overall)
        avg_distance = total_weighted_distance / total_weight if total_weight > 0 else float("inf")

        # normalize weights so no single tight-stdev feature dominates
        # AI Support for use of weight normalization: was having trouble with super high weights drowning out other features (when features had very tight standard deviation)
        max_weight = max(d["weight"] for d in feature_details.values())
        for detail in feature_details.values():
            detail["weight"] = detail["weight"] / max_weight  # scale all weights to [0, 1]

        style_scores[style] = {"distance": avg_distance, "feature_details": feature_details}

    # AI Support: initially was using relative normalization, but that meant that poor matches would come out as incorrectly high
    #with this approach of absolute confidence via exponential decay, means a poor match scores low regardless of how the other styles do
    results = []
    for style, data in style_scores.items():
        raw_confidence = math.exp(-0.5 * data["distance"])
        results.append((style, round(raw_confidence * 100, 1), data["feature_details"], data["distance"]))

    results.sort(key=lambda x: x[1], reverse=True) # sorting by confidence score, with highest confidence first
    return results


def explain_match(style, confidence, feature_details, results):
    lines = []
    lines.append(f"Best match: {style.title()} ({confidence}% confidence)")

    # Warn if confidence is low (song may not fit any style in the database well)
    top_confidence = confidence 
    confidence_diff = top_confidence - results[1][1] if len(results) > 1 else 100

    if top_confidence < 40.0: # if top match is less than 40% confident
        lines.append("Low confidence: this song may not match any known dance style well")
    elif top_confidence < 60.0 and confidence_diff < 15.0: 
        lines.append("Match uncertain: low confidence and top match is not significantly better than the second-best match")
    elif confidence_diff < 15.0: 
        lines.append(f"Match uncertain: consider also checking {results[1][0].title()}")

    lines.append("")
    lines.append("Why:")

    # Sort features by weight descending (most reliable first)
    ranked = sorted(feature_details.items(), key=lambda x: x[1]["weight"], reverse=True)
    median_weight = sorted([d["weight"] for d in feature_details.values()])[len(feature_details) // 2]

    for feature, detail in ranked:
        song_val = detail["song_value"]
        mean = detail["style_mean"]
        stdev = detail["style_stdev"]
        z = detail["z_score"]

        # How close match is for this feature
        if z < 0.5:
            closeness = "closely matches"
        elif 0.5 <= z < 1.0:
            closeness = "is within range of"
        elif 1.0 <= z < 2.0:
            closeness = "is somewhat outside"
        else:
            closeness = "is relatively far from"

        # How reliable feature is as signal
        reliability = "strong signal" if detail["weight"] > median_weight else "weaker signal"

        if feature == "bpm":
            lines.append(f"  * BPM: your song is {song_val:.1f}, which {closeness} "
                         f"{style.title()}'s typical {mean:.1f} ± {stdev:.1f} BPM  [{reliability}]")
        elif feature == "regularity":
            lines.append(f"  * Beat regularity: {song_val:.4f} {closeness} "
                         f"the expected {mean:.4f} ± {stdev:.4f}  [{reliability}]")
        elif feature == "energy":
            lines.append(f"  * Energy: {song_val:.4f} {closeness} "
                         f"the expected {mean:.4f} ± {stdev:.4f}  [{reliability}]")
        elif feature == "beat_strength":
            lines.append(f"  * Beat strength: {song_val:.4f} {closeness} "
                         f"the expected {mean:.4f} ± {stdev:.4f}  [{reliability}]")
        elif feature == "brightness":
            lines.append(f"  * Brightness: {song_val:.1f} Hz {closeness} "
                         f"the expected {mean:.1f} ± {stdev:.1f} Hz  [{reliability}]")
        elif feature == "rolloff":
            lines.append(f"  * Spectral rolloff: {song_val:.1f} Hz {closeness} "
                 f"the expected {mean:.1f} ± {stdev:.1f} Hz  [{reliability}]")
    return "\n".join(lines)
