import wiringpi
from wiringpi import GPIO

class DHT11:
    def __init__(self, pin):
        self.pin = pin
        wiringpi.wiringPiSetup()
    
    def getval(self):
        tl = []
        tb = []
        # Set pin mode to OUTPUT and send start signal
        wiringpi.pinMode(self.pin, GPIO.OUTPUT)
        wiringpi.digitalWrite(self.pin, GPIO.HIGH)
        wiringpi.delay(1)
        wiringpi.digitalWrite(self.pin, GPIO.LOW)
        wiringpi.delay(25)
        wiringpi.digitalWrite(self.pin, GPIO.HIGH)
        wiringpi.delayMicroseconds(20)
        wiringpi.pinMode(self.pin, GPIO.INPUT)
        
        # Wait for DHT11 response
        while wiringpi.digitalRead(self.pin) == 1:
            pass
        
        # Read data from DHT11
        for i in range(45):
            tc = wiringpi.micros()
            while wiringpi.digitalRead(self.pin) == 0:
                pass
            while wiringpi.digitalRead(self.pin) == 1:
                if wiringpi.micros() - tc > 500:
                    break
            if wiringpi.micros() - tc > 500:
                break
            tl.append(wiringpi.micros() - tc)
        
        # Process the data
        tl = tl[1:]
        for i in tl:
            if i > 100:
                tb.append(1)
            else:
                tb.append(0)
        
        return tb

    def get_result(self):
        for _ in range(10):
            SH = 0
            SL = 0
            TH = 0
            TL = 0
            C = 0
            result = self.getval()

            if len(result) == 40:
                for i in range(8):
                    SH *= 2; SH += result[i]    # humi Integer
                    SL *= 2; SL += result[i+8]  # humi decimal
                    TH *= 2; TH += result[i+16] # temp Integer
                    TL *= 2; TL += result[i+24] # temp decimal
                    C *= 2; C += result[i+32]   # Checksum
                if ((SH + SL + TH + TL) % 256) == C and C != 0:
                    break
                else:
                    print("Read Success, But checksum error! retrying")

            else:
                print("Read failer! Retrying")
                break
            wiringpi.delay(200)
        return SH, SL, TH, TL

# Example usage
dht11_sensor = DHT11(pin=6)
SH, SL, TH, TL = dht11_sensor.get_result()
print("humi:", SH, SL, "temp:", TH, TL)
