import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.signal import find_peaks

#Format: (x-start, y-start, width, height)
#FIXED_ROI = (460, 220, 150, 160)
FIXED_ROI = (515, 230, 85, 160)
rx, ry, rw, rh = FIXED_ROI
r=[rx, ry, rw, rh]


use_saved = True  # set False when calibrating
Helium_Reference_Lines = np.array([667.8, 587.6])

cap = cv2.VideoCapture(0)

cv2.startWindowThread()
cv2.namedWindow("Live Spectrometer Feed")

print("Program Started!")
print("-> Align your spetrum inside the green box.")
print("-> Press 's' to capture data and open the plots.")
print("-> Press 'q' to safely exit.")

while(True):
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame from camera")
        break

    display_frame = frame.copy()

    #Green Tracking Rectangle
    #Top Left Corner: (rx,ry) | Bottom-right corner: (rx+rw, ry+rh)
    cv2.rectangle(display_frame, (rx, ry), (rx+rw, ry+rh), (0, 255, 0), 2)

    #Show the LIVE Feed
    cv2.imshow("Live Spectrometer Feed", display_frame)

    k = cv2.waitKey(1) & 0xFF

    #Quit application 
    if k == ord('q'):
        break
    
    if k == ord('s'): # and roi_selected == True:
        
        cropped = frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        #Fast NumPy Math: calculates means for all columns istantly
        #cropped = cv2.flip (cropped,1)
        column_means = np.mean(cropped, axis=0)
        
        b_dist = column_means[:, 0]
        g_dist = column_means[:, 1]
        r_dist = column_means[:, 2]
        i_dist = (b_dist + g_dist + r_dist) / 3

        rgb_crop = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)

        plt.figure(figsize=(8,6))

        plt.subplot(2, 1, 1)
        plt.title("Selected ROI Box")
        plt.imshow(rgb_crop)

        plt.subplot(2, 1, 2)
        plt.title("Color Distribution")
        plt.plot(r_dist, color = 'r', label = 'Red')
        plt.plot(g_dist, color = 'g', label='Green')
        plt.plot(b_dist, color = 'b', label = 'Blue')
        plt.plot(i_dist, color= 'k', label='Mean Intensity')
        plt.legend(loc="upper left")
        plt.show()

        # #Peak Analysis
        # peaks, properties = find_peaks(i_dist, height=2, distance=15)
        # peak_heights = properties["peak_heights"]
        # peak_distances = np.diff(peaks)

        # print("--- Peak Results ---")
        # for i in range(len(peaks)):
        #     print(f"Peak {i+1}: Located at X = {peaks[i]}, Height = {peak_heights[i]:.2f}")

        # print("\n--- Distances Between Consecutive Peaks ---")
        # for i in range(len(peak_distances)):
        #     print(f"Distance from Peak {i+1} to Peak {i+2}: {peak_distances[i]} pixels")

        #Updated Peak Analysis
        all_peaks, _ = find_peaks(i_dist)


        if len(all_peaks) < 2:
            print(f"[ERROR] Only found {len(all_peaks)} total peak(s) in the image. Light source might be completely dark.")
            
        else:

            all_peak_heights = i_dist[all_peaks]

            highest_indices = np.argsort(all_peak_heights)[-2:]
            highest_indices_sorted = np.sort(highest_indices)

            peaks_to_use = all_peaks[highest_indices_sorted]
            heights_to_use = all_peak_heights[highest_indices_sorted]

            if use_saved:
                slope = np.load("slope.npy")
                intercept = np.load("intercept.npy")
            else:
                slope, intercept = np.polyfit(peaks_to_use, Helium_Reference_Lines, 1)
                np.save("slope.npy", slope)
                np.save("intercept.npy", intercept) 

        print(f"Isolated Peak 1: Pixel X = {peaks_to_use[0]} (Height = {heights_to_use[0]:.2f}) ---> {Helium_Reference_Lines[0]} nm")
        print(f"Isolated Peak 2: Pixel X = {peaks_to_use[1]} (Height = {heights_to_use[1]:.2f}) ---> {Helium_Reference_Lines[1]} nm")
        print(f"Calibration Equation: Wavelength = {slope:.4f} * Pixel + {intercept:.2f}")

        pixel_indices=np.arange(len(i_dist))
        calibrated_wavelengths = slope * pixel_indices + intercept
        calibrated_peak_x = slope * peaks_to_use + intercept

        # num_peaks_found = len(peaks)

        # if num_peaks_found < 2:
        #     print("\n[ERROR] Need at least 2 peaks to calibrate. Lower your 'height threshold.")
        # elif num_peaks_found > len(Helium_Reference_Lines):
        #     print(f"\n[WARNING] Found {num_peaks_found} peaks, which exceeds our reference lines ({len(Helium_Reference_Lines)}).")
        #     print("Raise your 'height' threshold slighlty.")
        # else:
        #     known_wavelengths = Helium_Reference_Lines[:num_peaks_found]
        #     print(f"\n--- Dynamically Calibrating {num_peaks_found} Peaks ---")
        #     for i in range(num_peaks_found):
        #         print(f"Mapping Peak {i+1} (Pixel {peaks[i]}) ---> {known_wavelengths[i]} nm")

        #     slope, intercept = np.polyfit(peaks, known_wavelengths, 1)

        #     print(f"\nCalibration Equation: Wavelength (nm) = {slope:.4f} * Pixel + {intercept:.2f}")

        #     pixel_indices = np.arange(len(i_dist))
        #     calibrated_wavelengths = slope * pixel_indices + intercept
        #     calibrated_peak_x = slope * peaks

            #Plot 2: Calibrated Spectrum
        plt.figure(figsize=(10,8))

        plt.subplot(3, 1, 1)
        plt.title("Captured Spectrum Image")
        plt.imshow(rgb_crop)

        plt.subplot(3, 1, 2)
        plt.title("Mean Intensity Graph (Pixel Space)")
        plt.plot(r_dist, color = 'r', alpha=0.2, label = 'Red')
        plt.plot(g_dist, color = 'g', alpha=0.2, label = 'Green')
        plt.plot(b_dist, color = 'b', alpha=0.2, label='Blue')
        plt.plot(i_dist, color = 'k', linewidth=2, label = 'Mean Intensity')
        plt.plot(peaks_to_use, heights_to_use, "x", color = "red", markersize=12, markeredgewidth=1, label = "Top 2 Peaks")
        plt.xlabel("Pixel Columns")
        plt.ylabel("Intensity (RGB)")
        plt.legend(loc="upper left")
        plt.grid(True, linestyle = "--", alpha = 0.5)

        plt.subplot(3, 1, 3)
        plt.title("Calibrated Spectrum (Phyiscal Wavelength)")
        plt.plot(calibrated_wavelengths, i_dist, color = 'blue', label = 'Calibrating Curve')
        plt.plot(calibrated_peak_x, heights_to_use, "o", color = "orange", markersize=8, label = "Calibrated Lines (nm)")
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Intensity (RGB)")
        plt.legend(loc="upper left")
        plt.grid(True, linestyle = "--", alpha = 0.5)

        plt.tight_layout()
        plt.show()

        np.savez("live_data.npz", w=calibrated_wavelengths, i=i_dist)
cap.release()
cv2.destroyAllWindows()


#         plt.figure(figsize=(8, 6))

#         plt.subplot(2, 1, 1)
#         plt.title("Selected ROI Box")
#         plt.imshow(rgb_crop)

#         plt.subplot(2, 1, 2)
#         plt.title("Color Distribution (Left to Right)")
#         plt.plot(r_dist, color='r', label='Red')
#         plt.plot(g_dist, color='g', label='Green')
#         plt.plot(b_dist, color='b', label='Blue')
#         plt.plot(i_dist, color='k', label='Mean Intensity')
#         plt.legend(loc="upper left")
#         plt.show()

#         cv2.imshow("Crop Feed", cropped)

#     elif k & 0xFF == ord('q'):
#         break

#     cv2.imshow('Live Feed', display_frame)
    
#     live_crop= frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
#     cv2.imshow("ROI Crop", live_crop)

# cap.release()
# cv2.destroyAllWindows()