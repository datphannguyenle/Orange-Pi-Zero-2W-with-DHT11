import wiringpi
from wiringpi import GPIO
import paho.mqtt.client as mqtt

class DHT11:
    def __init__(self, pin):
        self.pin = pin
        wiringpi.wiringPiSetup()
    
    def send_to_mqtt(self, sh, sl, th, tl):
        client = mqtt.Client()
        client.connect("192.168.1.218", 1883, 60)
        payload = f"SH={sh}, SL={sl}, TH={th}, TL={tl}"
        client.publish("dht", payload)
        client.disconnect()
    
    def get_result(self):
        SH = SL = TH = TL = C = 0
        result = [0] * 40  # Dummy data for demonstration
        # Your existing code to read data from DHT11 sensor
        if len(result) == 40:
            for i in range(8):
                SH *= 2; SH += result[i]    # humi Integer
                SL *= 2; SL += result[i+8]  # humi decimal
                TH *= 2; TH += result[i+16] # temp Integer
                TL *= 2; TL += result[i+24] # temp decimal
                C *= 2; C += result[i+32]   # Checksum
            if ((SH + SL + TH + TL) % 256) == C and C != 0:
                print("Read Success")
            else:
                print("Read Success, But checksum error! retrying")
        else:
            print("Read failer! Retrying")
        
        wiringpi.delay(200)
        return SH, SL, TH, TL

# Example usage
dht11_sensor = DHT11(pin=6)
SH, SL, TH, TL = dht11_sensor.get_result()
print("humi:", SH, SL, "temp:", TH, TL)
dht11_sensor.send_to_mqtt(SH, SL, TH, TL)
