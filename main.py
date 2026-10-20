# declare vars
import RPi.GPIO as GPIO
import time

isMotion = false;
btnPin = 40;
PIRPin = 38;

TRIG = 11;
ECHO = 12;
VIBRATION_MOTOR = 16;

# collect inputs

# write logic

def setup():
    GPIO.setmode(GPIO.BOARD);

    GPIO.setup(PIRPin, GPIO.IN) # pir setup
    GPIO.setup(BTNPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# Set BUTTON'S mode is input, and pull up to high level(3.3V)
	GPIO.add_event_detect(BTNPin, GPIO.BOTH, callback=detect, bouncetime=200)


	GPIO.setup(TRIG, GPIO.OUT) # Ultrasonic setup
    GPIO.setup(ECHO, GPIO.IN)

	GPIO.setup(VIBRATION_MOTOR, GPIO.OUT) 
    GPIO.output(VIBRATION_MOTOR, GPIO.LOW)  # Turn off the vibration motor initially

def distance(): # Function to measure distance with ultrasonic sensor
	GPIO.output(TRIG, 0)
    time.sleep(0.000002)
    GPIO.output(TRIG, 1) # turns on TRIG then off very fast in order to send out a "ping"
    time.sleep(0.00001) 
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0:
        pass
    time1 = time.time()
    
    while GPIO.input(ECHO) == 1:
        pass
    time2 = time.time()

    duration = time2 - time1 # time it takes for ping to reach object and then return
    return (duration * 340 / 2) * 100  # Conversion to centimeters

def loop():
    while true:
        buttonOn = bool(GPIO.input(GPIO.HIGH))
        if (buttonOn) isMotion = bool(GPIO.input(PIR)) # this is an if statement in one line
        
        

def vibrate():
    #FIXME-get the vibration to occur once button is pressed


if __name__ == '__main__': 	# Program start from here
    setup()
	try:
    	loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()  


