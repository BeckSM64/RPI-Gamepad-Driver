import RPi.GPIO as GPIO
import smbus
import uinput
import subprocess

address = 0x48
bus=smbus.SMBus(1)
cmd=0x40

Z_Pin = 24

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
GPIO.setup(Z_Pin, GPIO.IN, GPIO.PUD_UP) # R3/L3 button
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
# syn=False to emit an "atomic" (128, 128) event.
x_value = 128 #8 bit center
y_value = 128 #8 bit center
device.emit(uinput.ABS_X, x_value, syn=False)
device.emit(uinput.ABS_Y, y_value)
device.emit(uinput.ABS_RX, x_value, syn=False)
device.emit(uinput.ABS_RY, y_value)

def analogRead(chn):
    bus.write_byte(address,cmd+chn)
    value = bus.read_byte(address)
    return value

def analogWrite(value):
    bus.write_byte_data(address,cmd,value)

def convertValue(oldValue):

    # Convert the value
    if oldValue < 128:
        oldRange = (127 - -57)
        newRange = (127 - 0)
        newValue = (((oldValue - -57) * newRange) / oldRange) + 0
    elif oldValue > 128:
        oldRange = (175 - 129)
        newRange = (255 - 129)
        newValue = (((oldValue - 129) * newRange) / oldRange) + 129
    else:
        return oldValue

    # Check if value is negative, then force zero
    if newValue < 0:
        newValue = 0

    return newValue

try:
    while True:
        val_Z = GPIO.input(Z_Pin)
        val_Y = analogRead(0)
        val_X = analogRead(2)
        val_X = convertValue(val_X - 79)
        val_RY = analogRead(1)
        val_RX = analogRead(3)
        print("Click: %d, Y: %d, X: %d" % (val_Z, val_Y, val_X))
        device.emit(uinput.ABS_X, int(val_X))
        device.emit(uinput.ABS_Y, int(val_Y))
        print("Click: %d, Y: %d, X: %d" % (val_Z, val_RY, val_RX))
        device.emit(uinput.ABS_RX, int(val_RX))
        device.emit(uinput.ABS_RY, int(val_RY))

        # handle button inputs here
        if GPIO.input(AButton) == GPIO.LOW:
            print("A Button Pressed")
            device.emit(uinput.BTN_A, 1)
        else:
            device.emit(uinput.BTN_A, 0)

        if GPIO.input(BButton) == GPIO.LOW:
            print("B Button Pressed")
            device.emit(uinput.BTN_B, 1)
        else:
            device.emit(uinput.BTN_B, 0)

        if GPIO.input(XButton) == GPIO.LOW:
            print("X Button Pressed")
            device.emit(uinput.BTN_X, 1)
        else:
            device.emit(uinput.BTN_X, 0)

        if GPIO.input(YButton) == GPIO.LOW:
            print("Y Button Pressed")
            device.emit(uinput.BTN_Y, 1)
        else:
            device.emit(uinput.BTN_Y, 0)

        if GPIO.input(DPadUpButton) == GPIO.LOW:
            print("D-Pad Up Button Pressed")
            device.emit(uinput.BTN_DPAD_UP, 1)
        else:
            device.emit(uinput.BTN_DPAD_UP, 0)

        if GPIO.input(DPadDownButton) == GPIO.LOW:
            print("D-Pad Down Button Pressed")
            device.emit(uinput.BTN_DPAD_DOWN, 1)
        else:
            device.emit(uinput.BTN_DPAD_DOWN, 0)

        if GPIO.input(DPadLeftButton) == GPIO.LOW:
            print("D-Pad Left Button Pressed")
            device.emit(uinput.BTN_DPAD_LEFT, 1)
        else:
            device.emit(uinput.BTN_DPAD_LEFT, 0)

        if GPIO.input(DPadRightButton) == GPIO.LOW:
            print("D-Pad Right Button Pressed")
            device.emit(uinput.BTN_DPAD_RIGHT, 1)
        else:
            device.emit(uinput.BTN_DPAD_RIGHT, 0)

        if GPIO.input(StartButton) == GPIO.LOW:
            print("Start Button Pressed")
            device.emit(uinput.BTN_START, 1)
        else:
            device.emit(uinput.BTN_START, 0)

        if GPIO.input(SelectButton) == GPIO.LOW:
            print("Select Button Pressed")
            device.emit(uinput.BTN_SELECT, 1)
        else:
            device.emit(uinput.BTN_SELECT, 0)

        if GPIO.input(VolumeUpButton) == GPIO.LOW:
            print("Volume Up Button Pressed")
            subprocess.run(["amixer", "-q", "-M", "sset", "Headphone", "5%+"])

        if GPIO.input(VolumeDownButton) == GPIO.LOW:
            print("Volume Down Button Pressed")
            subprocess.run(["amixer", "-q", "-M", "sset", "Headphone", "5%-"])

        if GPIO.input(L2Button) == GPIO.LOW:
            print("L2 Button Pressed")
            device.emit(uinput.BTN_TL2, 1)
        else:
            device.emit(uinput.BTN_TL2, 0)

        if GPIO.input(L1Button) == GPIO.LOW:
            print("L1 Button Pressed")
            device.emit(uinput.BTN_TL, 1)
        else:
            device.emit(uinput.BTN_TL, 0)

        if GPIO.input(R2Button) == GPIO.LOW:
            print("R2 Button Pressed")
            device.emit(uinput.BTN_TR2, 1)
        else:
            device.emit(uinput.BTN_TR2, 0)

        if GPIO.input(R1Button) == GPIO.LOW:
            print("R1 Button Pressed")
            device.emit(uinput.BTN_TR, 1)
        else:
            device.emit(uinput.BTN_TR, 0)

        if GPIO.input(L3Button) == GPIO.LOW:
            print("L3 Button Pressed")
            device.emit(uinput.BTN_THUMBL, 1)
        else:
            device.emit(uinput.BTN_THUMBL, 0)

        if GPIO.input(R3Button) == GPIO.LOW:
            print("R3 Button Pressed")
            device.emit(uinput.BTN_THUMBR, 1)
        else:
            device.emit(uinput.BTN_THUMBR, 0)

except:
    GPIO.cleanup()
    device.destroy()
