import RPi.GPIO as GPIO

class Gpio():
    def start(self):
        # For GPIO numbering, instead of pin numbering
        GPIO.setmode(GPIO.BCM)

        self.redLed = 21
        self.greenLed = 20

        GPIO.setup(self.redLed, GPIO.OUT)
        GPIO.setup(self.greenLed, GPIO.OUT)

    def startPod(self):
        GPIO.output(self.redLed, False)
        GPIO.output(self.greenLed, True)
        print('Pod started')

    def brakePod(self):
        GPIO.output(self.redLed, True)
        GPIO.output(self.greenLed, False)
        print('Pod braked')

    def ledDemo(self):
        for i in range(2):
            GPIO.output(self.redLed, True)
            GPIO.output(self.greenLed, False)
            time.sleep(1)
            GPIO.output(self.redLed, False)
            GPIO.output(self.greenLed, True)
            time.sleep(1)
    def stop():
        GPIO.cleanup()