# declare vars
import RPi.GPIO as GPIO
import time
import subprocess
import base64
import sys
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

buttonPressed = False;
isMotion = False;
btnPin = 40;  # button
PIRPin = 38;  #gpio20 : PIR

TRIG = 11;  # ultrasonic
ECHO = 12;	# ultra
VIBRATION_MOTOR = 16;
MAX_DISTANCE = 152.4; # cm, approx 5 feet
dis = 0;

# openAI
API_KEY = os.environ["OPENAI_API_KEY"]
MODEL = "gpt-5-nano-2025-08-07"      
IMAGE_PATH = "captured_image.jpg"
RESOLUTION = "640x480"

client = OpenAI(api_key=API_KEY);
prompt = "Describe the emotion of the person in front of you in one word: happy (if they are smiling), neutral, or sad (if they are frowning)"

# deepgram
load_dotenv()                        # reads the keys from .env
DEEPGRAM_KEY = os.environ["DEEPGRAM_API_KEY"]

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
    
def loop():
    while True:
        isMotion = bool(GPIO.input(PIRPin));
        dis = distance();
        print(dis);
        print(isMotion)
        if isMotion and dis < MAX_DISTANCE:
            print(f"Object detected at: {dis} cm.");
            vibrate(2);
        buttonPressed = bool(GPIO.input(btnPin));
        if buttonPressed:
            capture_image(IMAGE_PATH)
            data_url = to_data_url(IMAGE_PATH)
            emotion = getEmotionFromImage(data_url)
            output_text = "The person in front of you is " + emotion
            text_to_speech(output_text)
        time.sleep(0.3)

def getEmotionFromImage(data_url):
	resp = client.responses.create(
            model=MODEL,
            reasoning={"effort": "low"},     # minimize hidden reasoning for speed
            max_output_tokens=1024,           # big headroom -> no practical cap
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": data_url}
                ]
            }],
        )

	return (extract_text(resp))
        

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


def vibrate(s):
    GPIO.output(VIBRATION_MOTOR, GPIO.HIGH)  # Turn on
    time.sleep(s)  # CHANGE TO SOMETHING ELSE
    GPIO.output(VIBRATION_MOTOR, GPIO.LOW)  # Turn off
    
def capture_image(path: str):
	# -S 2 skips a couple frames so exposure settles faster
	subprocess.run(["fswebcam", "-r", RESOLUTION, "-S", "2", "--no-banner", path], check=True)

def to_data_url(path: str) -> str:
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"

def extract_text(resp):
    text = getattr(resp, "output_text", None)
    if text:
        return text.strip()
    try:
        for item in getattr(resp, "output", []):
            for part in getattr(item, "content", []):
                if getattr(part, "type", None) in ("output_text", "text") and getattr(part, "text", None):
                    return part.text.strip()
    except Exception:
        pass
    try:
        return resp.model_dump_json(indent=2)
    except Exception:
        return str(resp)

def text_to_speech(text):
    r = requests.post(
        "https://api.deepgram.com/v1/speak?model=aura-2-thalia-en&encoding=linear16&container=wav",
        headers={"Authorization": "Token " + DEEPGRAM_KEY},
        json={"text": text})
    r.raise_for_status()
    open("answer.wav", "wb").write(r.content)

def destroy():
    GPIO.cleanup();

if __name__ == '__main__': 	# Program start from here
    setup();
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()  
