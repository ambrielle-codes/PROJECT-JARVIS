# declare vars
import RPi.GPIO as GPIO
import time

isMotion = False;
btnPin = 40;
PIRPin = 38;

TRIG = 11;
ECHO = 12;
VIBRATION_MOTOR = 16;
MAX_DISTANCE = 152.4; # cm, approx 5 feet

# collect inputs

# write logic

def setup():
    
    GPIO.setmode(GPIO.BOARD);

    #pir setup
    GPIO.setup(PIRPin, GPIO.IN);

    #button setup
    GPIO.setup(btnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP);	# Set BUTTON'S mode is input, and pull up to high level(3.3V)
    GPIO.add_event_detect(btnPin, GPIO.BOTH, callback=None, bouncetime=200);
    
    #ultrasonic setup
    GPIO.setup(TRIG, GPIO.OUT);
    GPIO.setup(ECHO, GPIO.IN);
    
    GPIO.setup(VIBRATION_MOTOR, GPIO.OUT);
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
        buttonPressed = bool(GPIO.input(GPIO.HIGH));
        if (buttonPressed):
            isMotion = bool(GPIO.input(PIR));
            print(isMotion);

        # if motion detected and distance is less than threshold value then vibrate for 2 secs
        dis = distance();
        print(dis);
        if(isMotion && distance() < MAX_DISTANCE):
            print(f"Object detected at: {dis} cm.");
            vibrate(2);
        
        

def vibrate(s):
    GPIO.output(VIBRATION_MOTOR, GPIO.HIGH)  # Turn on
    time.sleep(s)  # CHANGE TO SOMETHING ELSE
    GPIO.output(VIBRATION_MOTOR, GPIO.LOW)  # Turn off

def destory():
    GPIO.cleanup();

if __name__ == '__main__': 	# Program start from here
    setup()
	try:
    	loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()  


