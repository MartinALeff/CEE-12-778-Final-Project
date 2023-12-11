import atexit
import serial
import sqlite3
from pynmeagps import NMEAReader


# python ≥3.0
def only_numerics(seq):
    seq_type = type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))


def commitsqlatexit():
    con.commit()
    con.close()


# Set up Database
con = sqlite3.connect('Noise and Position.db')
atexit.register(commitsqlatexit)

# Create cursor to interact with the database
cursor = con.cursor()

# Creating table for noise levels and position
cursor.execute("""
        CREATE TABLE IF NOT EXISTS noise
        (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            longitude REAL,
            latitude REAL, 
            noise REAL      
        )
        """)

ser = serial.Serial("/dev/cu.SLAB_USBtoUART", 57600)
ser2 = serial.Serial("/dev/cu.usbmodem2101", 115200)

gnrmc = 'GNRMC'

id = 0

while True:
    nmr = NMEAReader(ser)
    (raw_data, parsed_data) = nmr.read()
    noise_raw = ser2.readline()
    noise_data = noise_raw.decode().strip()
    if gnrmc in str(parsed_data):
        id = id + 1
        lat = parsed_data.lat
        long = parsed_data.lon
        print(lat, long, noise_data)
        if lat and long and noise_data:
            time = str(parsed_data.time)
            date = str(parsed_data.date)
            dateAndTime = date + '_' + time
            all_data = [(dateAndTime, long, lat, noise_data)]
            cursor.executemany('INSERT INTO noise (timestamp, longitude, latitude, noise) VALUES (?, ?, ?, ?)',
                               all_data)
