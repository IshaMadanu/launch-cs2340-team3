from scipy.signal import find_peaks
import numpy as np

NIST_LIBRARY = {
    "Xenon": [462.43, 467.12, 473.42, 823.16, 828.01, 881.94],
    "Neon": [585.25, 614.31, 633.44, 640.22, 650.65, 703.24],
    "Argon": [696.54, 706.72, 738.40, 750.39, 763.51, 811.53],
    "Helium": [388, 400.96, 448.48, 588.86, 667.76, 703.32],
    "Mercury": [253.89, 312.82, 365.52, 435.8, 544.76, 576.38]
}
# def classify(wavelengths, intensities, tolerance_nm=2.0):
#     peak_indices, _ = find_peaks(intensities, prominence=0.1, distance=10)
#     detected_peaks = wavelengths[peak_indices]
    
#     scores = {}
#     for element, ref_lines in NIST_LIBRARY.items():
#         matched_peaks = 0
#         for peak in detected_peaks:
#             distances = np.abs(np.array(ref_lines) - peak)
#             if np.any(distances <= tolerance_nm):
#                 matched_peaks += 1

#         scores[element] = matched_peaks / len(detected_peaks) if len(detected_peaks) > 0 else 0.0
    
#     best_match = max(scores, key=scores.get)
#     return best_match, scores

def classify(wavelengths, intensities, tolerance_nm=3):
    peak_indices, _ = find_peaks(intensities, prominence=0.1, distance=10)
    if len(peak_indices) < 2:
        return "Insufficient Data", {}

    peak_intensities = intensities[peak_indices]
    # Get top 2 peaks
    top_2_indices = peak_indices[np.argsort(peak_intensities)[-2:]]
    detected_peaks = wavelengths[top_2_indices]
    
    scores = {}
    for element, ref_lines in NIST_LIBRARY.items():
        matched_peaks = 0
        total_intensity_match = 0
        
        for i, peak in enumerate(detected_peaks):
            distances = np.abs(np.array(ref_lines) - peak)
            if np.any(distances <= tolerance_nm):
                matched_peaks += 1
                total_intensity_match += (peak_intensities[i] / np.max(intensities))
        
        count_score = matched_peaks / 2.0
        intensity_score = total_intensity_match / 2.0
        scores[element] = (count_score + intensity_score) / 2
    
    best_match = max(scores, key=scores.get)
    return best_match, scores

spectData = np.load("live_data.npz")
raw_wavelengths = spectData['w']
raw_intensities = spectData['i']

print(classify(raw_wavelengths, raw_intensities))
