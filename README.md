# Parking Space Counter

The **Parking Space Counter** is a Streamlit application designed to monitor parking lot occupancy through video analysis. It uses image processing to detect available and occupied parking spots, sends SMS notifications via the Twilio API, and visualizes parking locations with an interactive map. 

## Features
- **Video Processing**: Analyze parking lot videos to determine parking space availability.
- **SMS Notifications**: Notify users about available parking slots.
- **Interactive Map**: Visual representation of parking locations with markers for available and occupied spots.
- **Machine Learning Integration**: Utilizes a pre-trained model to classify parking spots.

## Requirements
- Python 3.x
- Streamlit
- OpenCV
- NumPy
- Twilio
- Folium
- scikit-image
- pickle (for loading the model)

## Installation
1. Clone the repository: 
   ```bash
   git clone https://github.com/yourusername/parking-space-counter.git 
   cd parking-space-counter
## Twilio Setup
1.Sign up for a Twilio account.
2.Get your Account SID and Auth Token from the Twilio Console.
3.Purchase a Twilio phone number for sending SMS.
## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any suggestions or bugs.
