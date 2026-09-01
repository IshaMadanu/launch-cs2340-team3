import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
import joblib

from scipy.interpolate import interp1d


use_saved = True  #False = calibrating

image_path = "images/prototypeImages/Mercury3.jpg"
imgOG = cv2.imread(image_path)
height = np.size(imgOG, 0)
width = np.size(imgOG, 1)

img = imgOG[450:800, 400:600]
cv2.imwrite("cropImg.jpg", img)
img_copy = img.copy()

# print(img.shape)
# print(img.dtype)

# bayer = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE) 
# rgb = cv2.cvtColor(bayer, cv2.COLOR_BAYER_BG2BGR)

# cv2.imshow("img", rgb)

# nonBayer = cv2.demosaicing(img, cv2.COLOR_BayerBG2BGR, img_copy, 0)
# cv2.imshow("nonBayer", img_copy)

# #COLOR_BAYER_RG2BGR 


b, g, r = cv2.split(img)

intensity_b = np.mean(b, axis=0)
intensity_g = np.mean(g, axis=0)
intensity_r = np.mean(r, axis=0)

# # single row calculation
# mid_row = img.shape[0] // 2
# intensity_b = b[mid_row, :]
# intensity_g = g[mid_row, :]
# intensity_r = r[mid_row, :]

# plt.figure(figsize=(10, 5))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

ax1.plot(intensity_r, color="red", label="Red")
ax1.plot(intensity_g, color="green", label="Green")
ax1.plot(intensity_b, color="blue", label="Blue")

intensity_total = (intensity_r + intensity_g + intensity_b) / 3

ax1.plot(intensity_total, color="black", label="Total Intensity")

ax1.set_title("Intensity vs Pixel Position")
ax1.set_xlabel("Pixel Position)")
ax1.set_ylabel("Intensity")
ax1.legend()
ax1.grid(True, alpha=0.3)

#part 2 = calibration:


# indicies of peaks
# peaks, _ = find_peaks(intensity_total, distance=40)
# peaks = peaks[:2]
peaks, properties = find_peaks(intensity_total, height=100, distance=20)
print(f"Peak pixel, positions: {peaks}")

if use_saved:
    slope = np.load("slope.npy")
    intercept = np.load("intercept.npy")
    print("slope")
else:
    known = np.array([667.8, 587.7])  # helium lines
    slope, intercept = np.polyfit(peaks, known, 1)#calc slope and intercept of linear[1] betwn points
    np.save("slope.npy", slope)
    np.save("intercept.npy", intercept)
    print("slope")

pixels = np.arange(len(intensity_total))
cali = slope * pixels + intercept
print(slope)

ax2.plot(cali, intensity_total, color="black", label="Total Intensity")
peak_wave = cali[peaks] #converts peak pixels into wavelengths
ax2.scatter(peak_wave, intensity_total[peaks], color='purple', marker='v', label="Calibrated Peaks")

ax2.set_title("Intensity vs Wavelength")
ax2.set_xlabel("Wavelength")
ax2.set_ylabel("Intensity")
ax2.legend()
ax2.grid(True, alpha=0.3)

np.savez("live_data.npz", w=cali, i=intensity_total)
print("saved to live data")

# prepare data

def normalize(spectrum):
    peak = np.max(spectrum)
    if peak <= 0:
        return spectrum
    return spectrum / peak

def predict(file_path="live_data.npz"):
    model = joblib.load('rf_model.joblib')
    scaler = joblib.load('scaler.joblib')
 
    data = np.load(file_path)
    w_live, i_live = data['w'], data['i']
    uniform_grid = np.linspace(400, 750, 8000)
    grid_mapping = interp1d(w_live, i_live, kind='linear', bounds_error=False, fill_value=0.0)
    raw_vector = grid_mapping(uniform_grid)

    normalized_vector = normalize(raw_vector).reshape(1, -1)
 
    scaled_input = scaler.transform(normalized_vector)
    prediction = model.predict(scaled_input)
    probs = model.predict_proba(scaled_input)[0]
    for cls, p in sorted(zip(model.classes_, probs), key=lambda t: -t[1]):
        print(f"  {cls}: {p*100:.1f}%")
    print(f"\nPrediction: {prediction[0]}")

# def predict(modelName, spectrum_w, spectrum_i):
#     model = joblib.load(modelName)
#     uniform_grid = np.linspace(400, 750, 8000)
#     grid_mapping = interp1d(spectrum_w, spectrum_i, bounds_error=False, fill_value=0.0)
#     processed = grid_mapping(uniform_grid).reshape(1, -1)
#     prediction = model.predict(processed)
#     return prediction[0]

predict()
plt.tight_layout()
plt.show()

# import matplotlib.pyplot as plt

# plt.scatter(peak_wave, intensity_total[peaks], s=4)
# plt.plot(peak_wave, intensity_total[peaks], alpha=0.5)
# plt.xlabel("Wavelength (nm)")
# plt.ylabel("Intensity")
# plt.show()

# N = 50  # number of stacks
# stacked = (I * N) / N