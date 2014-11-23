############################################################################
#Program: TkRFID.py
#Language:  Python
#Date:  2014-11-21
#
#Description: Test app to demonstrate I/O functionality of Phidgets.
#Specifcally yhr servo control and RFID modules.
#
############################################################################


# Import Python Libraries___________________________________________________
import Tkinter
import time
import datetime
import csv
from ctypes import *
import sys

# Import Phidgets Libraries________________________________________________
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, OutputChangeEventArgs, SensorChangeEventArgs
from Phidgets.Devices.RFID import RFID, RFIDTagProtocol
from Phidgets.Devices.AdvancedServo import AdvancedServo


# Define GUI parameters___________________________________________________
mywindow = Tkinter.Tk()
mywindow.geometry("300x250")
mywindow.title("RFID Phidget Tester")
label_rfidTag = Tkinter.Label(mywindow, text = "RFID Tag: ")
label_LockedStatus = Tkinter.Label(mywindow, text = "LOCKED")


# Define global variables_________________________________________________
servoOpenPosition = 110
servoLockedPosition = 50
safeTag = "4742006"
lastTag = ""
servoLocked=Tkinter.IntVar()
servoLocked.set(1)
antennaOn = Tkinter.IntVar()
antennaOn.set(0)


# Event Handler Callback Functions________________________________________
def rfidAttached(e):
    attached = e.device
    print("RFID %i Attached!" % (attached.getSerialNum()))

def rfidDetached(e):
    detached = e.device
    print("RFID %i Detached!" % (detached.getSerialNum()))

def rfidError(e):
    try:
        source = e.device
        print("RFID %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))

def rfidOutputChanged(e):
    source = e.device
    print("RFID %i: Output %i State: %s" % (source.getSerialNum(), e.index, e.state))

def rfidTagGained(e):
	global lastTag
	source = e.device
	rfid.setLEDOn(1)
	lastTag = e.tag
	print("RFID %i: Tag Read: %s" % (source.getSerialNum(), e.tag))
	label_rfidTagText = ("RFID Tag: %s          " % e.tag)
	label_rfidTag.configure(text = label_rfidTagText)
	checkRFID(e.tag)

def rfidTagLost(e):
    source = e.device
    rfid.setLEDOn(0)
    print("RFID %i: Tag Lost: %s" % (source.getSerialNum(), e.tag))





# Sub-Functions_____________________________________________________
def checkRFID(tagID):
	global safeTag
	global servoLockedPosition
	global servoOpenPosition

	if tagID == safeTag:
		if servoLocked.get():
			unlockDevice()
			print("ID Confirmed...unlocked.  Servo turned to %d" % servoOpenPosition)
		else:
			lockDevice()
			print("ID Confirmed...LOCKED. Servo turned to %d" % servoLockedPosition)
	else:
		lockDevice()
		print("Incorrect tag detected.  Locking device. Servo turned to %d" % servoLockedPosition)
	statusDump()


def exitProgram():
	lockDevice()
	print("Locking device. Servo turned to %d" % servoLockedPosition)

	print("Closing Phidgets...")

	statusDump()

	try:
		rfid.closePhidget()
	except PhidgetException as e:
		print("Phidget Exception %i: %s" % (e.code, e.details))
		print("Exiting....")
		exit(1)
	try:
		advancedServo.closePhidget()
	except PhidgetException as e:
		print("Phidget Exception %i: %s" % (e.code, e.details))
		print("Exiting....")
		exit(1)
	print("Program successfully shutdown.  Goodbye.")
	exit(0)


def statusDump():
	global safeTag
	global lastTag
	global servoLocked
	ts = time.time()
	currTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	print("Current Status (%s) [tag - servoLocked]: %s - %d" % (currTime, lastTag, servoLocked.get()))

	#Write status of all I/O to .CSV file
	fp = open('DataDump.csv', 'a')
	writer = csv.writer(fp, delimiter=',')
	data=[currTime, lastTag, servoLocked.get()]
	writer.writerow(data)
	fp.close()


def unlockDevice():
	global servoLocked
	global servoOpenPosition
	try:
		advancedServo.setPosition(0, servoOpenPosition)
	except PhidgetException as e:
		print("Phidget Exception %i: %s" % (e.code, e.details))
	servoLocked.set(0)
	label_LockedStatus.configure(text="UNLOCKED")


def lockDevice():
	global servoLocked
	global servoLockedPosition
	try:
		advancedServo.setPosition(0, servoLockedPosition)
	except PhidgetException as e:
		print("Phidget Exception %i: %s" % (e.code, e.details))
	servoLocked.set(1)
	label_LockedStatus.configure(text="LOCKED")

def toggleAntenna():
	global antennaOn
	rfid.setAntennaOn(antennaOn.get())
	if antennaOn.get():
		print("Antenna turned on.")
	else:
		print("Antenna turned off.")


# Create and Initialize AdvancedServo object__________________________
print("Initialzing Servo...")
try:
    advancedServo = AdvancedServo()
except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)

try:
    advancedServo.openPhidget()
    advancedServo.waitForAttach(10000)
    advancedServo.setEngaged(0, True)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    try:
        advancedServo.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    print("Exiting....")
    exit(1)

advancedServo.setPosition(0, servoLockedPosition)
print("Servo initialized.")


# Create and Initialize RFID object_________________________________
print("Initialzing RFID Reader...")
try:
    rfid = RFID()
except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)

try:
    rfid.setOnAttachHandler(rfidAttached)
    rfid.setOnDetachHandler(rfidDetached)
    rfid.setOnErrorhandler(rfidError)
    rfid.setOnOutputChangeHandler(rfidOutputChanged)
    rfid.setOnTagHandler(rfidTagGained)
    rfid.setOnTagLostHandler(rfidTagLost)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

try:
    rfid.openPhidget()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

try:
    rfid.waitForAttach(10000)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    try:
        rfid.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    print("Exiting....")
    exit(1)

print("Turning on the RFID antenna....")
rfid.setAntennaOn(True)
antennaOn.set(1)
print("System setup complete.  Ready to read RFID tags.")


# Main Loop__________________________________________________
def main():
	antennaOnCheckbox = Tkinter.Checkbutton(text="Antenna On", command=toggleAntenna, variable=antennaOn, onvalue=1, offvalue=0)
	antennaOnCheckbox.place(x=200, y=5)

	statusDumpButton = Tkinter.Button(mywindow, text="Send Status", command=statusDump)
	statusDumpButton.place(x=5, y= 200)

	exitButton = Tkinter.Button(mywindow, text="Exit", command=exitProgram)
	exitButton.place(x=235, y= 200)

	label_rfidTag.place(x=25, y=120)
	label_LockedStatus.place(x=120, y=90)

	mywindow.mainloop()

if __name__ == '__main__':
    main()