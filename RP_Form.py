from Tkinter import *
import tkMessageBox
import RPi.GPIO as GPIO
import numpy
import time
from time import sleep
import datetime
from datetime import timedelta
from Phidgets.Devices.TemperatureSensor import *
from Phidgets.Devices.InterfaceKit import *
import serial

# Variable declaration
ser = serial.Serial('/dev/ttyACM0', 9600)
start_flag = False
end_flag = False
force_flag = False


def report(disp, flowRate, freq, load, input_temp, operation_time, dlSelection):

    # Create Phidget objects
    try:
        device_temp = TemperatureSensor()
        print("Temperature Phidget created okay")
        device_interface = InterfaceKit()
        print("Interface Phidget created okay")
    except RuntimeError as e:
        print("Runtime Error: %s" % e.message)

    # Opening Phidget devices so that they are ready to use
    try:
        device_temp.openPhidget()
        print("Temperature Phidget opened okay")
        device_interface.openPhidget()
        print("Interface Phidget created okay")
    except PhidgetException as e:
        print("Phidget Opening Exception %i: %s"% (e.code, e.detail))
        exit(1)

    # Form layout
    form2 = Toplevel()
    form2.title("Bioreactor Interface")
    etiquette1 = Label(form2, text="Parameters will be displayed in text windows w/ graph??")
    etiquette1.pack()

    labelframe = LabelFrame(form2, text="Time")
    labelframe.pack(fill="both", expand="yes", pady=10)
    label_time_rem = Label(labelframe, text="-")
    label_time_rem.grid(column=0, row=0, padx=5)
    label_time_el = Label(labelframe, text="-")
    label_time_el.grid(column=1, row=0)

    labelframe2 = LabelFrame(form2, text="Temperatures")
    labelframe2.pack(fill="both", expand="yes", pady=10)
    label_temp1 = Label(labelframe2, text="-")
    label_temp1.grid(column=0, row=0, padx=5)
    label_temp2 = Label(labelframe2, text="-")
    label_temp2.grid(column=1, row=0)
    label_temp3 = Label(labelframe2, text="-")
    label_temp3.grid(column=0, row=1, padx=5)
    label_temp4 = Label(labelframe2, text="-")
    label_temp4.grid(column=1, row=1)

    labelframe3 = LabelFrame(form2, text="Scaffold Load")
    labelframe3.pack(fill="both", expand="yes", pady=10)
    label_force = Label(labelframe3, text="-")
    label_force.grid(column=0, row=0, padx=5)

    labelframe4 = LabelFrame(form2, text="pH of fluid output")
    labelframe4.pack(fill="both", expand="yes", pady=10)
    label_ph = Label(labelframe4, text="-")
    label_ph.grid(column=0, row=0, padx=5)
    label_ph_temp = Label(labelframe4, text="-")
    label_ph_temp.grid(column=1, row=0)

    # User defined constants
    day, hrs, mins, sec = operation_time.split(',', 3)
    total_time = timedelta(days=int(day), hours=int(hrs), minutes=int(mins), seconds=int(sec))

    # Create new iteration in log file
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
    # File write ('a' (append) - prepare to add text to file)
    fw = open('data_logger.txt', 'a')
    fw.write("\n")
    fw.write("\n" + str(st))
    fw.write("\nUser Inputs:")
    fw.write('\nDisplacement = ' + str(disp))
    fw.write('\nFlow rate = ' + str(flowRate))
    fw.write('\nFrequency (Time of delay) = ' + str(freq))
    fw.write('\nLoad = ' + str(load))
    fw.write('\nTemperature = ' + str(input_temp))
    fw.write('\nOperation Time = ' + str(operation_time))
    fw.write('\nLinear (1) or Dynamic (2)? = ' + str(dlSelection))
    fw.write("\nRecordings:")
    fw.write("\n" + "Time (s) * Thermo 1 * Thermo 2 * Core Temp * Amb Temp * Force (N) * pH   * pH based on temp")
    fw.write("\n" + "*******************************************************************************************")
    fw.close()

    print st
    # Write values to text document

    # Threads for parallel scripts
    def stepper_control():
        while True:
            if start_flag is True:
                # Only runs if linear displacement method is selected
                if dlSelection is 1:
                    while True:
                        if end_flag is True:
                            ser.write(str(1))
                            print "End of operation"
                            return
                        else:
                            time.sleep(freq)
                            print(disp)
                            ser.write(str(disp))
                return
        return

    def force_control():
        while True:
            if start_flag is True:
                # Only runs if dynamic compression is selected
                if dlSelection is 2:
                    while True:
                        if end_flag is True:
                            print "End of operation"
                            device_interface.closePhidget()
                            ser.write(str(1))
                            return
                        else:
                            device_interface.waitForAttach(5000)
                            force_reading = (device_interface.getSensorValue(6))/(1000/7.006)
                            time.sleep(freq)
                            ser.write(str(2))
                            while force_reading < int(load):
                                device_interface.waitForAttach(5000)
                                force_reading = (device_interface.getSensorValue(6))/(1000/7.006)
                                time.sleep(0.1)
                            else:
                                print "Motor Stops"
                                ser.write(str(1))
                    return
        return

    def pump_control():
        while True:
            if start_flag is True:
                print(flowRate)
                ser.write(str(flowRate))
                while True:
                    if end_flag is True:
                        print "End of operation"
                        ser.write(str(9))
                        return
                    time.sleep(0.5)
                return
        return

    def temp_control():
        while True:
            if start_flag is True:
                # Loop through pins and set mode and state to 'low'
                GPIO.setup(4, GPIO.OUT)
                GPIO.output(4, GPIO.HIGH)
                while True:
                    if end_flag is True:
                        print "End of operation"
                        device_temp.closePhidget()
                        GPIO.output(4, GPIO.HIGH)
                        GPIO.cleanup()
                        return
                    else:
                        device_temp.waitForAttach(5000)
                        temp1 = (device_temp.getTemperature(0))
                        temp2 = (device_temp.getTemperature(1))
                        core_temp = ((temp1 + temp2)/2)
                        GPIO.output(4, GPIO.LOW)
                        while core_temp < int(input_temp):
                            device_temp.waitForAttach(5000)
                            temp_reading = (device_temp.getTemperature(0))
                            time.sleep(0.1)
                        else:
                            # Heating Circuit Stops
                            GPIO.output(4, GPIO.HIGH)
                return
        return

    def timer_sensor_control():
        global start_flag
        global end_flag
        global force_flag

        # Bioreactor is set to heat before operation
        status = Label(form2, text="Heating Bioreactor to specified heat",  bd=1, relief=SUNKEN, anchor=W)
        status.pack(side=BOTTOM, fill=X)
        device_temp.waitForAttach(5000)
        temp1 = (device_temp.getTemperature(0))
        temp2 = (device_temp.getTemperature(1))
        core_temp = ((temp1 + temp2)/2)
        # Initialising up GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        # Loop through pins and set mode and state to 'low'
        GPIO.setup(4, GPIO.OUT)
        GPIO.output(4, GPIO.LOW)
        current_status = status["text"]
        device_temp.waitForAttach(5000)
        while core_temp < int(21):
            temp1 = (device_temp.getTemperature(0))
            temp2 = (device_temp.getTemperature(1))
            core_temp = ((temp1 + temp2)/2)
            label_temp1["text"] = "Thermocouple 1: %.2f" % temp1 + u"\u2103"
            label_temp2["text"] = "Thermocouple 2: %.2f" % temp2 + u"\u2103"
            label_temp4["text"] = "Core Temperature: %.2f" % core_temp + u"\u2103"
            if current_status.endswith("..."):
                current_status = "Heating Bioreactor to specified heat"
            else:
                current_status += "."
                status["text"] = current_status
            time.sleep(1)
        else:
            # Heating Circuit Stops
            GPIO.output(4, GPIO.HIGH)
            status["text"] = "Temperature reached - operation begins"
            start_flag = True
        for passed_seconds in range(int(total_time.total_seconds())):
            passed_time = timedelta(seconds=passed_seconds)
            rem_time = (total_time - passed_time)
            label_time_rem["text"] = "Time Remaining: ", rem_time
            label_time_el["text"] = "Time Elapsed: ", passed_time

            try:
                thermocouple1 = (device_temp.getTemperature(0))
                label_temp1["text"] = "Thermocouple 1: %.2f" % thermocouple1 + u"\u2103"
                thermocouple2 = (device_temp.getTemperature(1))
                label_temp2["text"] = "Thermocouple 2: %.2f" % thermocouple2 + u"\u2103"
                ambient_temp = (device_temp.getAmbientTemperature())
                label_temp3["text"] = "Ambient Temperature: %.2f" % ambient_temp + u"\u2103"
                core_temperature = ((thermocouple1 + thermocouple2)/2)
                label_temp4["text"] = "Core Temperature: %.2f" % core_temperature + u"\u2103"

            except PhidgetException as e:
                print("Phidget Temp Error %s" % e.message)

            device_interface.waitForAttach(5000)
            try:
                analog_flexi = device_interface.getSensorValue(6)
                analog_ph = device_interface.getSensorValue(7)
                # 1000 is the range of the sensor output. for 1 lbf sensitivity => 1 = .07007 N
                # For 25 lbf = 111.206N i.e. force_flexi = (analog_flexi/(1000/111.206))
                force_flexi = (analog_flexi/(1000/7.006))
                label_force["text"] = "Current Force (N): %.2f" % force_flexi
                # pH Sensor
                ph_phidgets = 0.0178 * analog_ph - 0.889
                ph_temp_phidgets = 7 - ((2.5 - (analog_ph / 200.0)) / (0.257179 + (0.000941468 * thermocouple2))) + 1
                label_ph["text"] = "pH value = %.2f" % ph_phidgets
                label_ph_temp["text"] = "pH value w/ temp = %.2f" % ph_temp_phidgets

            except PhidgetException as e:
                print("Phidget Exception %i: %s"% (e.code, e.detail))
                print "Exit method B4 - Error has caused the program to close"

            # Append values to log
            fw = open('data_logger.txt', 'a')
            fw.write("\n" + str(passed_time) + "  * %.2f" % thermocouple1 + "    * %.2f" % thermocouple2 +
                     "    * %.2f" % core_temperature + "     * %.2f" % ambient_temp + "    * %.2f" % force_flexi +
                     "      * %.2f" % + ph_phidgets + " * %.2f" % ph_temp_phidgets)
            fw.close()

            sleep(1)
        print("Loop Finished")
        end_flag = True

        if tkMessageBox.askokcancel("Operation - Complete", "Operation has ended. Would you like to exit?"):
            print "Exit method B2"
            form2.destroy()

    def ask_quit():
        global end_flag
        if tkMessageBox.askokcancel("Exit", "Are you sure you want to Exit?"):
            print "Exit method B1"
            end_flag = True
            sleep(1)
            form2.destroy()

    # Call of threads
    timer_sensor = threading.Thread(name='Timer Control', target=timer_sensor_control)
    stepper = threading.Thread(name='Stepper Control', target=stepper_control)
    pump = threading.Thread(name='Pump Control', target=pump_control)
    temp = threading.Thread(name='Temperature Control', target=temp_control)
    force = threading.Thread(name='Force Control', target=force_control)

    stepper.daemon = True
    stepper.start()
    pump.daemon = True
    pump.start()
    temp.daemon = True
    temp.start()
    force.daemon = True
    force.start()
    timer_sensor.start()

    # Exit function
    form2.protocol("WM_DELETE_WINDOW", ask_quit)
