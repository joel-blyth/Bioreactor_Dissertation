from Tkinter import *
import tkMessageBox
import RP_Form
import serial

ser = serial.Serial('/dev/ttyACM0', 9600)
root = Tk()
root.title("Bioreactor Interface")

def beginOperation():
    # Set displacement variable to corresponding value for Arduino logic
    if var_displacement.get() == "10":
        di = 3
    elif var_displacement.get() == "5":
        di = 4
    else:
        di = 5
    # Set flow rate variable to corresponding value for Arduino logic
    if var_flow_rate.get() == "8":
        fl = 6
    elif var_flow_rate.get() == "6":
        fl = 7
    else:
        fl = 8
    # Set frequency for delay in secs
    if var_frequency.get() == "1/hr":
        fr = 3600
    elif var_frequency.get() == "1/min":
        fr = 60
    else:
        fr = 6
    lo = var_load.get()
    te = var_temp.get()
    ti = entry_time.get()
    dl = compression_selection.get()
    while True:
        try:
            day, hrs, mins, sec = ti.split(',', 3)
        except (ValueError, TypeError, NameError, SyntaxError):
            tkMessageBox.showerror("Error", "Please enter all times including 0 values, separated by commas, "
                                            "in correct numerical format.")
            return
        else:
            print("All good")
            break
    if dl < 1:
        tkMessageBox.showerror("Error", "Please select a mode of compression.")
        return
    else:
        RPForm8.report(di, fl, fr, lo, te, ti, dl)


def zero_stepper():
    ser.write(str(0))


def run_pump():
    ser.write(str(6))


def stop_pump():
    ser.write(str(9))


# Labels - Using grid layout - by default column = 0
label_time = Label(root, text="Time of Operation (dd,hh,mm,ss)")
label_time.grid(row=0)
label_temp = Label(root, text="Temperature (" + u"\u2103" + ")")
label_temp.grid(row=1)
label_flow_rate = Label(root, text="Flow Rate (mL/min)")
label_flow_rate.grid(row=2)
label_displacement = Label(root, text="Linear Displacement (mm)")
label_displacement.grid(row=3)
label_load = Label(root, text="Dynamic Compression - Load (N)")
label_load.grid(row=4)
label_frequency = Label(root, text="Frequency ")
label_frequency.grid(row=5)

# Declarations
var_time = StringVar(root)
var_temp = StringVar(root)
var_flow_rate = StringVar(root)
var_displacement = StringVar(root)
var_load = StringVar(root)
var_frequency = StringVar(root)

# Option dictionaries
option_temp = [35, 36, 37, 38, 39]
var_temp.set(37)
option_flow_rate = ["4", "6", "8"]
var_flow_rate.set(option_flow_rate[1])
option_displacement = ["2.5", "5", "10"]
var_displacement.set(option_displacement[1])
option_load = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6]
var_load.set(3)
option_frequency = ["1/hr", "1/min", "6/s"]
var_frequency.set(option_frequency[1])

# Radio Button Selection
compression_selection = IntVar()
set_displacement = Radiobutton(root, text=' ', variable=compression_selection, value=1)
set_load = Radiobutton(root, text=' ', variable=compression_selection, value=2)
set_displacement.grid(row=3, column=2)
set_load.grid(row=4, column=2)

# Input field
entry_time = Entry(root)
drop_temp = OptionMenu(root, var_temp, *option_temp)
drop_flow_rate = OptionMenu(root, var_flow_rate, *option_flow_rate)
drop_displacement = OptionMenu(root, var_displacement, *option_displacement)
drop_load = OptionMenu(root, var_load, *option_load)
drop_frequency = OptionMenu(root, var_frequency, *option_frequency)
entry_time.grid(row=0, column=1)
drop_temp.grid(row=1, column=1)
drop_flow_rate.grid(row=2, column=1)
drop_displacement.grid(row=3, column=1)
drop_load.grid(row=4, column=1)
drop_frequency.grid(row=5, column=1)

# Buttons
button2 = Button(root, text="Zero Stepper", command=zero_stepper)
button2.grid(row=0, column=2)
button3 = Button(root, text="Run Pump", command=run_pump)
button3.grid(row=1, column=2)
button4 = Button(root, text="Stop Pump", command=stop_pump)
button4.grid(row=2, column=2)
button1 = Button(root, text="Start", command=beginOperation)
button1.grid(row=5, column=2)

root.mainloop()
