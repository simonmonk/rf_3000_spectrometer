from tkinter import * 
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
import serial.tools.list_ports
from tkinter import ttk, messagebox
import sys
from time import sleep

# the main Tkinter window 
window = Tk() 
window.title('RF-2000 Spectrometer') 
window.geometry("1200x600") 
  

fig = Figure(figsize = (5, 5), dpi = 100)   
plot1 = fig.add_subplot(111) 
canvas = FigureCanvasTkAgg(fig, master = window) 

button_frame = Frame(window)

ports = serial.tools.list_ports.comports()

start_f = StringVar(window, '70')
end_f = StringVar(window, '130')
step = StringVar(window, '1')
port = StringVar(window, '')

def connect():
    global ports, ser
    port_str = port.get()
    print("Selected port: " + port_str)
    if port_str == "":
        messagebox.showerror(title = "Error", message = "No port selected")
        ports = serial.tools.list_ports.comports()
        return
    try:
        ser = serial.Serial(port_str, 115200)
        if ser.is_open:
            messagebox.showinfo(title = "Success", message = "Connected to Spectrometer")
    except:
        messagebox.showerror(title = "Error", message = "Couldn't connect to Spectrometer.")
        ports = serial.tools.list_ports.comports()

def clear():
    global plot1
    fig.clf() 
    plot1 = fig.add_subplot(111)


# start sampling data - first setting parameters
def start():
    global plot1, canvas
    f0 = float(start_f.get())
    f1 = float(end_f.get())
    df = float(step.get())
    expected = int((f1 - f0) / df)
    if f0 >= f1:
        messagebox.showerror(title = "Error", message = "Start frequency must be less than end frequency")
        return
    stop_spectrometer()
    set_param('w1', int(f0 * 1000))
    set_param('w2', int(f1 * 1000))
    set_param('w3', int(df * 1000))
    n, fs, dbs = take_readings(f0, f1, df)
    if n != expected:
        messagebox.showerror(title = "Error", message = f"Expected {expected} readings, got {n}")
        stop_spectrometer()
        return
    plot1.plot(fs, dbs) 
    plot1.set_ylim(-90, 0)
    plot1.set_ylabel('dB')
    plot1.set_xlabel('Frequency (MHz)')
    plot1.yaxis.grid(visible=True, which='major')
    plot1.xaxis.grid(visible=True, which='both')
    canvas.draw() 
    canvas.get_tk_widget().pack(side='top', fill='both') 

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

def take_readings(f0, f1, df):
    start_spectrometer()
    dbs = []
    fs = []
    f = f0
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
        dbs.append(reading)
        fs.append(f)
        f += df
        print(f"{str(f)},{str(reading)}")
        n += 1
    stop_spectrometer()
    return (n-1, fs, dbs)


# buttons and controls
connect_button = Button(master = button_frame, command = connect, height = 2,  width = 10, text = "Connect")
start_button = Button(master = button_frame, command = start, height = 2,  width = 10, text = "Start")
com_port_combo = ttk.Combobox(master = button_frame, state="readonly", textvariable = port, values=[port.device for port in ports])
com_port_label = Label(master = button_frame, text="Port")
start_f_label = Label(master = button_frame, text="Start Frequency (MHz)")
start_f_field = ttk.Entry(master = button_frame, width=7, textvariable = start_f)
end_f_label = Label(master = button_frame, text="End Frequency (MHz)")
end_f_field = ttk.Entry(master = button_frame, width=7, textvariable = end_f)
step_f_label = Label(master = button_frame, text="Step (MHz)")
step_f_field = ttk.Entry(master = button_frame, width=7, textvariable = step)
clear_button = Button(master = button_frame, command = clear, height = 2,  width = 10, text = "Clear")

com_port_label.pack(side='left')
com_port_combo.pack(side='left')
connect_button.pack(side='left')
start_f_label.pack(side='left')
start_f_field.pack(side='left')
end_f_label.pack(side='left')
end_f_field.pack(side='left')
step_f_label.pack(side='left')
step_f_field.pack(side='left')
start_button.pack(side='left')
clear_button.pack(side='left')
button_frame.pack(side='top', fill='x')
  
# run the gui 
window.mainloop() 