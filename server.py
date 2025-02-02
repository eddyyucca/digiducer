from flask import Flask, jsonify, render_template, request
import numpy as np
import sounddevice as sd
import queue
import threading
import sqlite3
from datetime import datetime
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

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            acceleration REAL,
            velocity REAL,
            demodulation REAL
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(acceleration, velocity, demodulation):
    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO measurements (timestamp, acceleration, velocity, demodulation)
        VALUES (?, ?, ?, ?)
    """, (datetime.now(), acceleration, velocity, demodulation))
    conn.commit()
    conn.close()

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
        with sd.InputStream(
            device=device_index,
            channels=2,
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            callback=audio_callback,
            dtype='float32'
        ) as stream:
            print("Audio stream started...")
            while running:
                sd.sleep(100)  # Allow thread to run
    except NoDevicesFound as e:
        print(e)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Audio stream stopped.")

# Route to serve real-time data
@app.route("/data", methods=["GET", "POST"])
def data():
    try:
        if request.method == "POST":
            if not q.empty():
                raw_data = q.get()
                # Hitung Acceleration
                acceleration = raw_data[:, 0] / DEFAULT_SENSITIVITY * CONVERSION_FACTOR

                # Hitung Velocity (numerical integration)
                dt = 1 / SAMPLE_RATE
                velocity = np.cumsum(acceleration) * dt  # mm/s

                # Hitung Demodulation
                demodulation = np.abs(hilbert(raw_data[:, 0]))

                # Simpan data ke database
                mean_acceleration = round(np.mean(acceleration), 3)
                mean_velocity = round(np.mean(velocity), 3)
                mean_demodulation = round(np.mean(demodulation), 3)
                save_to_db(mean_acceleration, mean_velocity, mean_demodulation)

                return jsonify({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "acceleration": mean_acceleration,
                    "velocity": mean_velocity,
                    "demodulation": mean_demodulation
                })
            else:
                return jsonify({
                    "error": "No data available in queue",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "acceleration": 0.0,
                    "velocity": 0.0,
                    "demodulation": 0.0
                })

        elif request.method == "GET":
            if not q.empty():
                raw_data = q.get()
                # Hitung Acceleration
                acceleration = raw_data[:, 0] / DEFAULT_SENSITIVITY * CONVERSION_FACTOR

                # Hitung Velocity (numerical integration)
                dt = 1 / SAMPLE_RATE
                velocity = np.cumsum(acceleration) * dt  # mm/s

                # Hitung Demodulation
                demodulation = np.abs(hilbert(raw_data[:, 0]))

                return jsonify({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "acceleration": round(np.mean(acceleration), 3),
                    "velocity": round(np.mean(velocity), 3),
                    "demodulation": round(np.mean(demodulation), 3)
                })
            else:
                return jsonify({
                    "error": "No data available in queue",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "acceleration": 0.0,
                    "velocity": 0.0,
                    "demodulation": 0.0
                })

    except Exception as e:
        print(f"Error in /data endpoint: {e}")
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "acceleration": 0.0,
            "velocity": 0.0,
            "demodulation": 0.0
        })
def save_to_db(acceleration, velocity, demodulation):
    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()
    print(f"Saving to DB: Acceleration={acceleration}, Velocity={velocity}, Demodulation={demodulation}")  # Log data
    cursor.execute("""
        INSERT INTO measurements (timestamp, acceleration, velocity, demodulation)
        VALUES (?, ?, ?, ?)
    """, (datetime.now(), acceleration, velocity, demodulation))
    conn.commit()
    conn.close()

@app.route("/view-data")
def view_data():
    try:
        # Buka koneksi ke database
        conn = sqlite3.connect("results.db")
        cursor = conn.cursor()

        # Ambil semua data dari tabel measurements
        cursor.execute("SELECT * FROM measurements ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()

        # Kirim data ke template
        return render_template("view_data.html", rows=rows)
    except Exception as e:
        return f"An error occurred: {e}"


# Route to retrieve stored samples
@app.route("/samples")
def samples():
    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM measurements ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    results = [
        {"id": row[0], "timestamp": row[1], "acceleration": row[2], "velocity": row[3], "demodulation": row[4]}
        for row in rows
    ]
    return jsonify(results)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stop")
def stop():
    global running
    running = False
    return "Stream stopped!"

# Start audio stream in a background thread
audio_thread = threading.Thread(target=start_stream, daemon=True)
audio_thread.start()

if __name__ == "__main__":
    init_db()  # Initialize the database
    print(r"""
  _____     _      _                                                                                  
 | ____| __| |  __| | _   _  _   _  _   _   ___  __ _                                                 
 |  _|  / _` | / _` || | | || | | || | | | / __|/ _` |                                                
 | |___| (_| || (_| || |_| || |_| || |_| || (__| (_| |                                                
 |_____|\__,_| \__,_| \__, | \__, | \__,_| \___|\__,_|                                                
                      |___/  |___/                                                                    
    """)
    app.run(debug=True)
    running = False  # Stop the audio thread when the server is stopped
