import serial
import sys

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

input("Make sure the spectroeter screen says STOP. Press ENTER to continue.")
print("Waiting for data. Press RUN/STOP button on spectrometer.")
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
print(f"Read {n} readings.")
file.close()
print(f"Now open {file_name} in your favorite spreadsheet")