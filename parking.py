git initimport cv2
import numpy as np
import streamlit as st
from util import get_parking_spots_bboxes, empty_or_not
from twilio.rest import Client
import folium
from streamlit_folium import folium_static

# Function to calculate the difference between two images
def calc_diff(im1, im2):
    return np.abs(np.mean(im1) - np.mean(im2))

# Twilio SMS function
def send_sms(available_spots, total_spots, slot_number, account_sid, auth_token, twilio_phone_number, user_phone_number):
    client = Client(account_sid, auth_token)

    message_body = f"Hi, We Are From MK Car Parking. Available Slots: {available_spots}, Total Slots: {total_spots}, Your Slot Number: {slot_number}."
    
    client.messages.create(
        to=user_phone_number,
        from_=twilio_phone_number,
        body=message_body
    )

# Create a Folium map
def create_map(location):
    m = folium.Map(location=location, zoom_start=12)
    folium.Marker(location, popup='Parking Location').add_to(m)
    return m

# Streamlit App
st.title('Parking Space Counter with Map')

# Twilio credentials input
account_sid = st.text_input("Enter your Twilio Account SID")
auth_token = st.text_input("Enter your Twilio Auth Token", type="password")
twilio_phone_number = st.text_input("Enter your Twilio Phone Number")
user_phone_number = st.text_input("Enter your Phone Number for SMS")

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
                frame = cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 255, 0), 2)  # Green for occupied
            else:
                frame = cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 0, 255), 2)  # Red for free

        # Add text for available spots
        available_spots = sum(1 for status in spots_status if not status)
        cv2.rectangle(frame, (80, 20), (550, 80), (0, 0, 0), -1)
        cv2.putText(frame, f'Available spots: {available_spots} / {len(spots_status)}',
                    (100, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Display the frame in Streamlit
        stframe.image(frame, channels="BGR", use_column_width=True)

        # Send SMS only once after processing the video
        if frame_nmr == step:
            slot_number = 1  # Change this logic to determine the user's slot number
            send_sms(available_spots, len(spots_status), slot_number, account_sid, auth_token, twilio_phone_number, user_phone_number)

        frame_nmr += 1

    cap.release()
# Create an interactive map showing the parking location
    parking_map = folium.Map(location=[9.1737, 77.9933], zoom_start=15)
    
    # Add markers for available parking spots
    for spot_indx, spot in enumerate(spots):
        x1, y1, w, h = spot
        if spots_status[spot_indx]:  # If spot is available
            folium.Marker([9.1737 + spot_indx * 0.00001, 77.9933], popup=f'Slot {spot_indx + 1} is available').add_to(parking_map)
        else:
            folium.Marker([9.1737 + spot_indx * 0.00001, 77.9933], popup=f'Slot {spot_indx + 1} is occupied', icon=folium.Icon(color='red')).add_to(parking_map)

    # Display the interactive map
    folium_static(parking_map)
