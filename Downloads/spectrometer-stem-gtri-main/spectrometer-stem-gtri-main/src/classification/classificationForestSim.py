import os
import collections
import numpy as np
from scipy.interpolate import interp1d
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MaxAbsScaler
from sklearn.metrics import classification_report, accuracy_score
from simLIBS import SimulatedLIBS
import joblib

LOW_W, UPPER_W, NUM_FEATURES = 400, 750, 8000


def addNoise(intensities):
    scaled = intensities * 1000
    noisy = np.random.poisson(scaled) / 1000
    drift = np.random.normal(0, 0.005, size=intensities.shape)
    return np.maximum(noisy + drift, 0)


def createLIBS():
    Te_range = np.linspace(0.5, 1.0, 5)
    Ne_range = [10**16, 10**17]
    elements = ['He', 'Xe', 'Hg']

    X, y, Te_meta = [], [], []

    for element in elements:
        for Te in Te_range:
            for Ne in Ne_range:
                try:
                    libs = SimulatedLIBS(Te=Te, Ne=Ne, elements=[element],
                                          percentages=[100], resolution=1000,
                                          low_w=LOW_W, upper_w=UPPER_W, webscraping='static')

                    df = libs.get_interpolated_spectrum()
                    raw_intensities = df.iloc[:, 1].values
                    w_sim = df.iloc[:, 0].values

                    grid_map = interp1d(w_sim, raw_intensities, kind='linear',
                                         bounds_error=False, fill_value=0.0)
                    full_spectrum = grid_map(np.linspace(LOW_W, UPPER_W, NUM_FEATURES))
                    clean_intensities = addNoise(full_spectrum)

                    X.append(clean_intensities)
                    y.append(element)
                    Te_meta.append(Te)
                except Exception as e:
                    print(f"Skipping {element}")

    return np.array(X), np.array(y), np.array(Te_meta)


def trainModel(X, y, Te_meta, train_threshold=0.75):

    train_mask = Te_meta <= train_threshold

    X_train, X_test = X[train_mask], X[~train_mask]
    y_train, y_test = y[train_mask], y[~train_mask]

    scaler = MaxAbsScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    print(f"Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")
    print(classification_report(y_test, y_pred))




    return model, scaler


if __name__ == "__main__":
    X, y, Te_meta = createLIBS()
    model, scaler = trainModel(X, y, Te_meta, train_threshold=0.75)
    joblib.dump(model, 'rf_model.joblib')
    joblib.dump(scaler, 'scaler.joblib')
    print("Model and Scaler saved.")