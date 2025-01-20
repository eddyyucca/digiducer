from flask import Flask, jsonify, render_template
import numpy as np
import sounddevice as sd
import queue
import threading
from scipy.signal import hilbert

# Flask app
app = Flask(__name__)

# Global variables
q = queue.Queue()
DEFAULT_SENSITIVITY = 4.00  # Sensitivity (4.00% FSV/g for Channel A)
CONVERSION_FACTOR = 9.80665  # 1 g = 9.80665 m/s²
SAMPLE_RATE = 48000  # Frekuensi sampel
BLOCK_SIZE = 1024  # Ukuran blok data
running = True  # Untuk menghentikan thread audio stream

# Custom exceptions
class NoDevicesFound(Exception):
    """Exception raised when no compatible devices are found."""
    pass

# Function to find compatible device
def find_device(target_model="333D01"):
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if target_model in device['name']:
            print(f"Found device: {device['name']} at index {i}")
            return i
    raise NoDevicesFound(f"No compatible device ({target_model}) found.")

# Audio callback to handle data
def audio_callback(indata, frames, time, status):
    if status:
        print(f"Status: {status}")
    q.put(indata[:, :])  # Push data to queue

# Start audio stream in a separate thread
def start_stream():
    global running
    try:
        device_index = find_device()  # Find compatible device
        stream = sd.InputStream(
            device=device_index,
            channels=2,
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            callback=audio_callback,
            dtype='float32'
        )
        stream.start()
        print("Audio stream started...")
        while running:
            pass  # Keep thread alive
        stream.stop()
        print("Audio stream stopped.")
    except NoDevicesFound as e:
        print(e)
    except Exception as e:
        print(f"Error: {e}")

# Route to serve real-time data
@app.route("/data")
def data():
    try:
        if not q.empty():
            raw_data = q.get()
            # Calculate Acceleration
            acceleration = raw_data[:, 0] / DEFAULT_SENSITIVITY * CONVERSION_FACTOR

            # Calculate Velocity (numerical integration)
            dt = 1 / SAMPLE_RATE
            velocity = np.cumsum(acceleration) * dt  # mm/s

            # Calculate Demodulation
            demodulation = np.abs(hilbert(raw_data[:, 0]))

            return jsonify({
                "acceleration": round(np.mean(acceleration), 3),
                "velocity": round(np.mean(velocity), 3),
                "demodulation": round(np.mean(demodulation), 3)
            })
        else:
            return jsonify({
                "acceleration": 0.0,
                "velocity": 0.0,
                "demodulation": 0.0
            })
    except Exception as e:
        print(e)
        return jsonify({
            "acceleration": 0.0,
            "velocity": 0.0,
            "demodulation": 0.0
        })

# Route to serve the web page
@app.route("/")
def index():
    return render_template("index.html")

# Stop the stream when the app stops
@app.route("/stop")
def stop():
    global running
    running = False
    return "Stream stopped!"

# Start audio stream in a background thread
audio_thread = threading.Thread(target=start_stream, daemon=True)
audio_thread.start()

if __name__ == "__main__":
    app.run(debug=True)
