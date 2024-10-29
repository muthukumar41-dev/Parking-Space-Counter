import cv2
import numpy as np
import streamlit as st
from util import get_parking_spots_bboxes, empty_or_not

def calc_diff(im1, im2):
    return np.abs(np.mean(im1) - np.mean(im2))

# Streamlit App
st.title('Parking Space Counter')

# File uploader for video and mask images
uploaded_video = st.file_uploader("Upload a parking lot video", type=["mp4", "avi", "mov"])
uploaded_mask = st.file_uploader("Upload the corresponding mask image", type=["png", "jpg"])

if uploaded_video is not None and uploaded_mask is not None:
    # Save the uploaded video and mask temporarily
    video_path = 'temp_video.mp4'
    mask_path = 'temp_mask.png'
    
    with open(video_path, mode='wb') as f:
        f.write(uploaded_video.read())
        
    with open(mask_path, mode='wb') as f:
        f.write(uploaded_mask.read())
    
    # Load the mask dynamically
    mask = cv2.imread(mask_path, 0)

    # Process the video
    cap = cv2.VideoCapture(video_path)

    connected_components = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
    spots = get_parking_spots_bboxes(connected_components)
    spots_status = [None for _ in spots]
    diffs = [None for _ in spots]

    previous_frame = None
    frame_nmr = 0
    step = 30
    ret = True

    stframe = st.empty()  # To display video frames in Streamlit

    while ret:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_nmr % step == 0 and previous_frame is not None:
            for spot_indx, spot in enumerate(spots):
                x1, y1, w, h = spot
                spot_crop = frame[y1:y1 + h, x1:x1 + w, :]
                diffs[spot_indx] = calc_diff(spot_crop, previous_frame[y1:y1 + h, x1:x1 + w, :])

        if frame_nmr % step == 0:
            if previous_frame is None:
                arr_ = range(len(spots))
            else:
                arr_ = [j for j in np.argsort(diffs) if diffs[j] / np.amax(diffs) > 0.4]
            for spot_indx in arr_:
                spot = spots[spot_indx]
                x1, y1, w, h = spot
                spot_crop = frame[y1:y1 + h, x1:x1 + w, :]
                spot_status = empty_or_not(spot_crop)
                spots_status[spot_indx] = spot_status

        if frame_nmr % step == 0:
            previous_frame = frame.copy()

        # Draw rectangles on the spots
        for spot_indx, spot in enumerate(spots):
            spot_status = spots_status[spot_indx]
            x1, y1, w, h = spots[spot_indx]
            if spot_status:
                frame = cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 255, 0), 2)
            else:
                frame = cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 0, 255), 2)

        # Add text for available spots
        cv2.rectangle(frame, (80, 20), (550, 80), (0, 0, 0), -1)
        cv2.putText(frame, f'Available spots: {sum(spots_status)} / {len(spots_status)}',
                    (100, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Display the frame in Streamlit
        stframe.image(frame, channels="BGR", use_column_width=True)

        frame_nmr += 1

    cap.release()
