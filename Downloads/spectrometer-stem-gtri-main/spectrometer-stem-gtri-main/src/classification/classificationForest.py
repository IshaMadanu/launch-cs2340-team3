import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
from scipy.signal import find_peaks
from sklearn.metrics import accuracy_score, classification_report


PEAKS = 5

nistData = pd.read_csv("ml/cleaned_lines.csv")

nistData['label'] = nistData['species'].str.split('_').str[0]
label_col = 'label'

def get_peak(species_lines, n_peaks=PEAKS): #get top N peaks from data
   peaks = (
       species_lines.sort_values("intens", ascending=False)
       [["obs_wl_air(nm)", "intens"]].values[:n_peaks]
   )

   max_Inten = species_lines["intens"].max()

   feature = np.zeros(n_peaks * 2) #array w 0s
   for i, (wl, inten) in enumerate(peaks): #(waveln, intensity)
       feature[2*i] = wl
       feature[2*i+1] = inten/max_Inten

   return feature

def augment(base, n_peaks=PEAKS):
    augmented_feature = base.copy()
    for i in range(n_peaks):
        wl_idx = 2 * i
        int_indx = 2*i + 1

        if augmented_feature[wl_idx] > 0:
            # adding noise to peaks wavelen
            augmented_feature[wl_idx] += np.random.normal(0,0.05)
        #    augmented_feature[2] += np.random.normal(0,0.05)
    #noise to peaks inten
    #    augmented_feature[1] *= np.random.uniform(0.95, 1.05)
            augmented_feature[int_indx] *= np.random.uniform(0.95, 1.05)
    
    augmented_feature[1::2] = np.clip(augmented_feature[1::2], 0, 1)

    return augmented_feature
    #    augmented_feature[3] = np.clip(augmented_feature[3], 0, 1)


np.random.seed(42)
X_train_list, y_train_list = [], []

X_test_list, y_test_list = [], []


for species in nistData["species"].unique():
   sdf = nistData[nistData["species"] == species]
   base = get_peak(sdf)
   for _ in range(400):
        X_train_list.append(augment(base))
        y_train_list.append(species)
   for _ in range(100) :
       X_test_list.append(augment(base))
       y_test_list.append(species)

X_train = np.array(X_train_list)
y_train = np.array(y_train_list)
X_test = np.array(X_test_list)
y_test = np.array(y_test_list)  

# X_train.reshape(-1, 1)
# X_test.reshape(-1, 1)
# y_train.reshape(-1, 1)
# y_test.reshape(-1, 1)

# y_series = pd.Series(y)
# strat = y_series if y_series.value_counts().min() >= 2 else None

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42, stratify=y)

rf = RandomForestClassifier(
    n_estimators=500,
    max_depth=5,
    min_samples_split=2,
    class_weight='balanced',
    random_state=42
)

rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

classification_rep = classification_report(y_test, y_pred)

print(f"Accuracy: {accuracy:.2f}")
print("\nClassification Report:\n", classification_rep)


joblib.dump(rf, "ml/spectra_rf_model.joblib")
print("Saved spectra_rf_model.joblib")

# y_pred = rf.predict(X_test)
# # print(confusion_matrix(y_test, y_pred))

# data = np.load("live_data.npz")
# raw_wavelengths = data['w']
# raw_intensities = data['i']

# rf = joblib.load("ml/spectra_rf_model.joblib")
# model_wavelengths = np.linspace(min(raw_wavelengths), max(raw_wavelengths), 4) #array btwn min /max increment of 4
# unknown_array = np.interp(model_wavelengths, raw_wavelengths, raw_intensities)
# # unknown_array = unknown_array / np.max(unknown_array)

# pred = rf.predict(unknown_array.reshape(1, -1))
# print("Prediction:", pred[0])


def get_live_peaks(wavelengths, intensities, n_peaks=PEAKS):
    if intensities is None or len(intensities) == 0:
        return np.zeros(n_peaks * 2)
    max_val = np.max(intensities) if np.max(intensities) > 0 else 1.0
    norm_intensities = intensities / max_val
    peaks_idx, _ = find_peaks(norm_intensities, distance=10, prominence=0.03)
    
    sorted_peak_idxs = peaks_idx[np.argsort(norm_intensities[peaks_idx])[::-1]]
    top_peaks = sorted_peak_idxs[:n_peaks]
    
    feature = np.zeros(n_peaks * 2)
    for i, idx in enumerate(top_peaks):
        feature[2*i] = wavelengths[idx]
        feature[2*i+1] = norm_intensities[idx]
        
    return feature

def predict_element(wavelengths, intensities, model, n_peaks=PEAKS):
    feature_vec = get_live_peaks(wavelengths, intensities, n_peaks=n_peaks)
    feature_vec = feature_vec.reshape(1, -1)

    prediction = model.predict(feature_vec)[0]
    proba = model.predict_proba(feature_vec)[0]
    proba_dict = dict(zip(model.classes_, proba.round(3)))

    return prediction, proba_dict

# def predict_element(wavelengths, intensities, model, n_peaks=2):
#     read = pd.DataFrame({
#         "obs_wl_air(nm)": wavelengths,
#         "intens":         intensities
#     })

#     feature_vec = get_peak(read, n_peaks=n_peaks)
#     feature_vec = feature_vec.reshape(1, -1)

#     prediction = model.predict(feature_vec)[0]
#     proba = model.predict_proba(feature_vec)[0]
#     proba_dict = dict(zip(model.classes_, proba.round(3)))

#     return prediction, proba_dict
    

data = np.load("live_data.npz")
raw_wavelengths = data['w']
raw_intensities = data['i']

element, probabilities = predict_element(raw_wavelengths, raw_intensities, rf)
print(f"Predicted: {element}")

