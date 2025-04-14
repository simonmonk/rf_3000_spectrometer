import serial
import sys
from time import sleep

if len(sys.argv) != 6:
    print(f"Usage: spectrometer.py <port> <start f MHz> <end f MHz> <step MHz>")
    print("For example (MacOS): % python3 spectrometer.py /dev/cu.usbserial-1430 80 103 0.1 test.csv")
    sys.exit(1)

prog, port, start_str, end_str, step_str, file_name = sys.argv

start_f = float(start_str)
end_f = float(end_str)
step = float(step_str)

expected_readings = int((end_f - start_f) / step)
print(f"Expecting {expected_readings} readings")

try:
    ser = serial.Serial(port, 115200)
    print("Connecting to: " + ser.name)
    if ser.is_open:
        print("Connected to Spectrometer")
except:
    print("Couldn't connect to Spectrometer.")
    sys.exit(1)

file = open(file_name, 'w')
file.write("f, db\n")

# scraped from interface⸮stop#w10015000#w20020000#w30000100#start#

def stop_spectrometer():
    sleep(0.1)
    ser.write(b'#stop#') 
    sleep(0.1)

def start_spectrometer():
    sleep(0.1)
    ser.write(b'#start#') 
    sleep(0.1)


def set_param(param, value):
    cmd = '#' + param + "{:07d}".format(value) + '#'
    ser.write(cmd.encode('utf-8'))
    sleep(0.1)

stop_spectrometer()
set_param('w1', int(start_f * 1000))
set_param('w2', int(end_f * 1000))
set_param('w3', int(step * 1000))
start_spectrometer()


f = start_f
n = 0
while True:
    ch = ser.read()
    while ch[0] != ord('$'):
        ch = ser.read()
    hash = ser.read()
    reading_str = ''
    while ch[0] != ord(' '):
        reading_str += ch.decode("utf-8")
        ch = ser.read()    
    if len(reading_str) <= 1:
        break
    reading = float(reading_str[1:])
    line = f"{str(f)},{str(reading)}"
    f += step
    print(line)
    file.write(line + "\n")
    n += 1

stop_spectrometer()
print(f"Read {n} readings.")
file.close()
print(f"Now open {file_name} in your favorite spreadsheet")
