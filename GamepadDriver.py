import RPi.GPIO as GPIO
import smbus
import uinput
import subprocess
import xmltodict
import argparse
import time

address = 0x48
bus=smbus.SMBus(1)
cmd=0x40

# Pins associated with corresponding button
AButton = 15
BButton = 16
XButton = 24
YButton = 23
DPadUpButton = 5
DPadDownButton = 6
DPadLeftButton = 26
DPadRightButton = 12
StartButton = 20
SelectButton = 21
VolumeUpButton = 13
VolumeDownButton = 19
L2Button = 14
L1Button = 18
R2Button = 8
R1Button = 7
L3Button = 25
R3Button = 17

# Setup GPIO Mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(AButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # a button
GPIO.setup(BButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # b button
GPIO.setup(XButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # x button
GPIO.setup(YButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # y button
GPIO.setup(DPadUpButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # dpadup button
GPIO.setup(DPadDownButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # dpaddown button
GPIO.setup(DPadLeftButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # dpadleft button
GPIO.setup(DPadRightButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # dpadright button
GPIO.setup(StartButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # start button button
GPIO.setup(SelectButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # select button
GPIO.setup(VolumeUpButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # volume up button
GPIO.setup(VolumeDownButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # volume down button
GPIO.setup(L2Button, GPIO.IN, pull_up_down=GPIO.PUD_UP) # l2 button
GPIO.setup(L1Button, GPIO.IN, pull_up_down=GPIO.PUD_UP) # l1 button
GPIO.setup(R2Button, GPIO.IN, pull_up_down=GPIO.PUD_UP) # r2 button
GPIO.setup(R1Button, GPIO.IN, pull_up_down=GPIO.PUD_UP) # r1 button
GPIO.setup(L3Button, GPIO.IN, pull_up_down=GPIO.PUD_UP) # l3 button
GPIO.setup(R3Button, GPIO.IN, pull_up_down=GPIO.PUD_UP) # r3 button

# Creating the virtual gamepad
events = (
	uinput.BTN_DPAD_UP,
	uinput.BTN_DPAD_DOWN,
	uinput.BTN_DPAD_LEFT,
	uinput.BTN_DPAD_RIGHT,
	uinput.BTN_SELECT,
	uinput.BTN_START,
    uinput.BTN_A,
	uinput.BTN_B,
	uinput.BTN_X,
	uinput.BTN_Y,
	uinput.BTN_TL,
	uinput.BTN_TL2,
	uinput.BTN_TR,
	uinput.BTN_TR2,
    uinput.BTN_THUMBL,
    uinput.BTN_THUMBR,
    uinput.ABS_X + (0, 255, 0, 0),
    uinput.ABS_Y + (0, 255, 0, 0),
    uinput.ABS_RX + (0, 255, 0, 0),
    uinput.ABS_RY + (0, 255, 0, 0),
)

device = uinput.Device(events)

# Center joystick output
x_value = 128 #8 bit center
y_value = 128 #8 bit center
device.emit(uinput.ABS_X, x_value, syn=False)
device.emit(uinput.ABS_Y, y_value)
device.emit(uinput.ABS_RX, x_value, syn=False)
device.emit(uinput.ABS_RY, y_value)

# Values for analog sticks to overwrite with xml config
analog_values_dict = {
    "lx_min" : 0,
    "lx_mid" : 128,
    "lx_max" : 255,
    "rx_min" : 0,
    "rx_mid" : 128,
    "rx_max": 255
}

def analogRead(chn):
    bus.write_byte(address,cmd+chn)
    value = bus.read_byte(address)
    return value


def analogWrite(value):
    bus.write_byte_data(address,cmd,value)


def convertValue(oldValue, oldMin, oldMax):

    # Constants for range
    MID_VALUE = 128
    MAX_VALUE = 255
    MIN_VALUE = 0

    # Convert the value
    if oldValue < MID_VALUE:

        # Convert value if it's below mid (128)
        oldRange = ((MID_VALUE - 1) - oldMin)
        newRange = ((MID_VALUE - 1) - MIN_VALUE)
        newValue = (((oldValue - oldMin) * newRange) / oldRange) + MIN_VALUE

    # Convert value if it's above mid (128)
    elif oldValue > MID_VALUE:
        oldRange = (oldMax - (MID_VALUE + 1))
        newRange = (MAX_VALUE - (MID_VALUE + 1))
        newValue = (((oldValue - (MID_VALUE + 1)) * newRange) / oldRange) + (MID_VALUE + 1)

    # Return the value directly if it is exactly mid (128)
    else:
        return oldValue

    # Return converted value
    return newValue


def read_xml_config(path_to_xml_config):
    with open(path_to_xml_config, "r") as xml_config_file:
        doc = xmltodict.parse(xml_config_file.read())
        analog_values_dict["lx_min"] = int(doc["gamepad_config"]["left_analog"]["x_axis"]["min"])
        analog_values_dict["lx_mid"] = int(doc["gamepad_config"]["left_analog"]["x_axis"]["mid"])
        analog_values_dict["lx_max"] = int(doc["gamepad_config"]["left_analog"]["x_axis"]["max"])
        analog_values_dict["rx_min"] = int(doc["gamepad_config"]["right_analog"]["x_axis"]["min"])
        analog_values_dict["rx_mid"] = int(doc["gamepad_config"]["right_analog"]["x_axis"]["mid"])
        analog_values_dict["rx_max"] = int(doc["gamepad_config"]["right_analog"]["x_axis"]["max"])

        analog_values_dict["ly_min"] = int(doc["gamepad_config"]["left_analog"]["y_axis"]["min"])
        analog_values_dict["ly_mid"] = int(doc["gamepad_config"]["left_analog"]["y_axis"]["mid"])
        analog_values_dict["ly_max"] = int(doc["gamepad_config"]["left_analog"]["y_axis"]["max"])
        analog_values_dict["ry_min"] = int(doc["gamepad_config"]["right_analog"]["y_axis"]["min"])
        analog_values_dict["ry_mid"] = int(doc["gamepad_config"]["right_analog"]["y_axis"]["mid"])
        analog_values_dict["ry_max"] = int(doc["gamepad_config"]["right_analog"]["y_axis"]["max"])

try:

    # Parse args, path to XML config file
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_xml_config")
    args = parser.parse_args()

    # Read in the XML config file
    read_xml_config(args.path_to_xml_config)
    # Calculate the offset between the read mid value and what the midpoint should be (128)
    # TODO: Fix this for if value is LESS than the mid value (offset to the left),
    # currently assumes it is offset to the right side of the midpoint
    LX_OFFSET = analog_values_dict["lx_mid"] - 128
    RX_OFFSET = analog_values_dict["rx_mid"] - 128
    LY_OFFSET = analog_values_dict["ly_mid"] - 128
    RY_OFFSET = analog_values_dict["ry_mid"] - 128
    while True:
        val_Y = analogRead(0)
        val_X = analogRead(2)
        val_X = convertValue(val_X - LX_OFFSET, analog_values_dict["lx_min"] - LX_OFFSET, analog_values_dict["lx_max"] - LX_OFFSET)
        val_Y = convertValue(val_Y - LY_OFFSET, analog_values_dict["ly_min"] - LY_OFFSET, analog_values_dict["ly_max"] - LY_OFFSET)
        val_RY = analogRead(1)
        val_RX = analogRead(3)
        val_RX = convertValue(val_RX - RX_OFFSET, analog_values_dict["rx_min"] - RX_OFFSET, analog_values_dict["rx_max"] - RX_OFFSET)
        val_RY = convertValue(val_RY - RY_OFFSET, analog_values_dict["ry_min"] - RY_OFFSET, analog_values_dict["ry_max"] - RY_OFFSET)
        device.emit(uinput.ABS_X, int(val_X))
        device.emit(uinput.ABS_Y, int(val_Y))
        #print("LX: %d, LY: %d, RX: %d, RY: %d" % (val_X, val_Y, val_RX, val_RY))
        device.emit(uinput.ABS_RX, int(val_RX))
        device.emit(uinput.ABS_RY, int(val_RY))

        # handle button inputs here
        if GPIO.input(AButton) == GPIO.LOW:
            print("=== A Button Pressed ===")
            device.emit(uinput.BTN_A, 1)
        else:
            device.emit(uinput.BTN_A, 0)

        if GPIO.input(BButton) == GPIO.LOW:
            print("=== B Button Pressed ===")
            device.emit(uinput.BTN_B, 1)
        else:
            device.emit(uinput.BTN_B, 0)

        if GPIO.input(XButton) == GPIO.LOW:
            print("=== X Button Pressed ===")
            device.emit(uinput.BTN_X, 1)
        else:
            device.emit(uinput.BTN_X, 0)

        if GPIO.input(YButton) == GPIO.LOW:
            print("=== Y Button Pressed ===")
            device.emit(uinput.BTN_Y, 1)
        else:
            device.emit(uinput.BTN_Y, 0)

        if GPIO.input(DPadUpButton) == GPIO.LOW:
            print("=== D-Pad Up Button Pressed ===")
            device.emit(uinput.BTN_DPAD_UP, 1)
        else:
            device.emit(uinput.BTN_DPAD_UP, 0)

        if GPIO.input(DPadDownButton) == GPIO.LOW:
            print("=== D-Pad Down Button Pressed ===")
            device.emit(uinput.BTN_DPAD_DOWN, 1)
        else:
            device.emit(uinput.BTN_DPAD_DOWN, 0)

        if GPIO.input(DPadLeftButton) == GPIO.LOW:
            print("=== D-Pad Left Button Pressed ===")
            device.emit(uinput.BTN_DPAD_LEFT, 1)
        else:
            device.emit(uinput.BTN_DPAD_LEFT, 0)

        if GPIO.input(DPadRightButton) == GPIO.LOW:
            print("=== D-Pad Right Button Pressed ===")
            device.emit(uinput.BTN_DPAD_RIGHT, 1)
        else:
            device.emit(uinput.BTN_DPAD_RIGHT, 0)

        if GPIO.input(StartButton) == GPIO.LOW:
            print("=== Start Button Pressed ===")
            device.emit(uinput.BTN_START, 1)
        else:
            device.emit(uinput.BTN_START, 0)

        if GPIO.input(SelectButton) == GPIO.LOW:
            print("=== Select Button Pressed ===")
            device.emit(uinput.BTN_SELECT, 1)
        else:
            device.emit(uinput.BTN_SELECT, 0)

        if GPIO.input(VolumeUpButton) == GPIO.LOW:
            print("=== Volume Up Button Pressed ===")
            subprocess.run(["amixer", "-q", "-M", "sset", "Headphone", "5%+"])

        if GPIO.input(VolumeDownButton) == GPIO.LOW:
            print("=== Volume Down Button Pressed ===")
            subprocess.run(["amixer", "-q", "-M", "sset", "Headphone", "5%-"])

        if GPIO.input(L2Button) == GPIO.LOW:
            print("=== L2 Button Pressed ===")
            device.emit(uinput.BTN_TL2, 1)
        else:
            device.emit(uinput.BTN_TL2, 0)

        if GPIO.input(L1Button) == GPIO.LOW:
            print("=== L1 Button Pressed ===")
            device.emit(uinput.BTN_TL, 1)
        else:
            device.emit(uinput.BTN_TL, 0)

        if GPIO.input(R2Button) == GPIO.LOW:
            print("=== R2 Button Pressed ===")
            device.emit(uinput.BTN_TR2, 1)
        else:
            device.emit(uinput.BTN_TR2, 0)

        if GPIO.input(R1Button) == GPIO.LOW:
            print("=== R1 Button Pressed ===")
            device.emit(uinput.BTN_TR, 1)
        else:
            device.emit(uinput.BTN_TR, 0)

        if GPIO.input(L3Button) == GPIO.LOW:
            print("=== L3 Button Pressed ===")
            device.emit(uinput.BTN_THUMBL, 1)
        else:
            device.emit(uinput.BTN_THUMBL, 0)

        if GPIO.input(R3Button) == GPIO.LOW:
            print("=== R3 Button Pressed ===")
            device.emit(uinput.BTN_THUMBR, 1)
        else:
            device.emit(uinput.BTN_THUMBR, 0)

        # Power down console
        if GPIO.input(L2Button) == GPIO.LOW and GPIO.input(R2Button) == GPIO.LOW and GPIO.input(L1Button) == GPIO.LOW and GPIO.input(R1Button) == GPIO.LOW and GPIO.input(DPadRightButton) == GPIO.LOW and GPIO.input(XButton):
            print("=== Powering Down... ===")
            subprocess.run(["sudo", "poweroff"])

        # Reset console
        if GPIO.input(L2Button) == GPIO.LOW and GPIO.input(R2Button) == GPIO.LOW and GPIO.input(L1Button) == GPIO.LOW and GPIO.input(R1Button) == GPIO.LOW and GPIO.input(DPadLeftButton) == GPIO.LOW and GPIO.input(AButton):
            print("=== Resetting... ===")
            subprocess.run(["sudo", "reboot"])

        # Run analog callibration script
        if GPIO.input(L2Button) == GPIO.LOW and GPIO.input(R2Button) == GPIO.LOW and GPIO.input(L1Button) == GPIO.LOW and GPIO.input(R1Button) == GPIO.LOW and GPIO.input(DPadDownButton) == GPIO.LOW and GPIO.input(BButton):
            print("=== Callibrating... ===")
            time.sleep(1)
            all_callibrated = False

            doc = None
            with open("/home/pi/GamepadConfig.xml", "r") as xml_config_file:
                doc = xmltodict.parse(xml_config_file.read())
                xml_config_file.close()

            while not all_callibrated:
                for key, value in analog_values_dict.items():
                    submitted = False
                    while not submitted:
                        value = None
                        if key == "lx_min":
                            print(f"=== Hold L Left and Press A: {key}, {analogRead(0)} ===")
                            value = analogRead(0)
                        elif key == "lx_mid":
                            print(f"=== Keep Neutral and Press A: {key}, {analogRead(0)} ===")
                            value = analogRead(0)
                        elif key == "lx_max":
                            print(f"=== Hold L Right and Press A: {key}, {analogRead(0)} ===")
                            value = analogRead(0)
                        elif key == "rx_min":
                            print(f"=== Hold R Left and Press A: {key}, {analogRead(1)} ===")
                            value = analogRead(1)
                        elif key == "rx_mid":
                            print(f"=== Hold Neutral and Press A: {key}, {analogRead(1)} ===")
                            value = analogRead(1)
                        elif key == "rx_max":
                            print(f"=== Hold R Right and Press A: {key}, {analogRead(1)} ===")
                            value = analogRead(1)
                        elif key == "ly_min":
                            print(f"=== Hold L Down and Press A: {key}, {analogRead(2)} ===")
                            value = analogRead(2)
                        elif key == "ly_mid":
                            print(f"=== Hold Neutral and Press A: {key}, {analogRead(2)} ===")
                            value = analogRead(2)
                        elif key == "ly_max":
                            print(f"=== Hold L Up and Press A: {key}, {analogRead(2)} ===")
                            value = analogRead(2)
                        elif key == "ry_min":
                            print(f"=== Hold R Down and Press A: {key}, {analogRead(3)} ===")
                            value = analogRead(3)
                        elif key == "ry_mid":
                            print(f"=== Hold Neutral and Press A: {key}, {analogRead(3)} ===")
                            value = analogRead(3)
                        else:
                            print(f"=== Hold R Up and Press A: {key}, {analogRead(3)} ===")
                            value = analogRead(3)

                        if GPIO.input(AButton) == GPIO.LOW:
                            print(f"=== Submitted: {key} ===")
                            # Write the value to the analog direction dictionary and the xml config file

                            with open("/home/pi/GamepadConfig.xml", "w") as xml_config_file:
                                xml_config_file.write(xmltodict.unparse(doc))
                                if key == "lx_min":
                                    doc["gamepad_config"]["left_analog"]["x_axis"]["min"] = value
                                elif key == "lx_mid":
                                    doc["gamepad_config"]["left_analog"]["x_axis"]["mid"] = value
                                elif key == "lx_max":
                                    doc["gamepad_config"]["left_analog"]["x_axis"]["max"] = value
                                elif key == "rx_min":
                                    doc["gamepad_config"]["right_analog"]["x_axis"]["min"] = value
                                elif key == "rx_mid":
                                    doc["gamepad_config"]["right_analog"]["x_axis"]["mid"] = value
                                elif key == "rx_max":
                                    doc["gamepad_config"]["right_analog"]["x_axis"]["max"] = value
                                elif key == "ly_min":
                                    doc["gamepad_config"]["left_analog"]["y_axis"]["min"] = value
                                elif key == "ly_mid":
                                    doc["gamepad_config"]["left_analog"]["y_axis"]["mid"] = value
                                elif key == "ly_max":
                                    doc["gamepad_config"]["left_analog"]["y_axis"]["max"] = value
                                elif key == "ry_min":
                                    doc["gamepad_config"]["right_analog"]["y_axis"]["min"] = value
                                elif key == "ry_mid":
                                    doc["gamepad_config"]["right_analog"]["y_axis"]["mid"] = value
                                else:
                                    doc["gamepad_config"]["right_analog"]["y_axis"]["max"] = value
                                xml_config_file.close()

                            analog_values_dict[key] = value
                            submitted = True
                            time.sleep(1)
                all_callibrated = True
                print("=== Callibration Complete ===")


except:
    GPIO.cleanup()
    device.destroy()
