import time
import wiringpi
from wiringpi import GPIO
import paho.mqtt.client as mqtt
from abc import ABC, abstractmethod

# MQTT configuration
broker_address = "106fe3e8b38542f1bac5bd11d49751c9.s1.eu.hivemq.cloud"
port = 8883
username = "alphabits"
password = "AlphaBits1"
TEMPERATURE_TOPIC = "smart-farm/hub/sensor/temperature"
HUMIDITY_TOPIC = "smart-farm/hub/sensor/humidity"


class Sensor(ABC):
    @abstractmethod
    def read(self):
        pass


class DHT11Sensor(Sensor):
    def __init__(self, pin):
        self.pin = pin

    def read(self):
        for _ in range(10):
            result = self._get_raw_data()
            if len(result) == 40:
                data = self._process_data(result)
                if self._validate_checksum(data):
                    return data
            print("Read failed! Retrying")
            wiringpi.delay(200)
        return None

    def _get_raw_data(self):
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(self.pin, GPIO.OUTPUT)
        self._send_start_signal()
        wiringpi.pinMode(self.pin, GPIO.INPUT)
        return self._collect_data()

    def _send_start_signal(self):
        wiringpi.digitalWrite(self.pin, GPIO.HIGH)
        wiringpi.delay(1)
        wiringpi.digitalWrite(self.pin, GPIO.LOW)
        wiringpi.delay(25)
        wiringpi.digitalWrite(self.pin, GPIO.HIGH)
        wiringpi.delayMicroseconds(20)

    def _collect_data(self):
        data = []
        for _ in range(45):
            start_time = wiringpi.micros()
            while wiringpi.digitalRead(self.pin) == 0:
                pass
            while wiringpi.digitalRead(self.pin) == 1:
                if wiringpi.micros() - start_time > 500:
                    return data
            data.append(wiringpi.micros() - start_time)
        return data[1:]

    def _process_data(self, raw_data):
        return [1 if t > 100 else 0 for t in raw_data]

    def _validate_checksum(self, data):
        *values, checksum = [sum(data[i : i + 8]) for i in range(0, 40, 8)]
        return sum(values) % 256 == checksum and checksum != 0


class MQTTPublisher:
    def __init__(self, broker_address, port):
        self.broker_address = broker_address
        self.port = port

    def publish(self, topic, message):
        client = mqtt.Client()
        try:
            client.connect(self.broker_address, port=self.port)
            result = client.publish(topic, message)
            result.wait_for_publish()
            print(f"Published to {topic}")
        except Exception as e:
            print(f"Failed to publish to {topic}: {e}")
        finally:
            client.disconnect()


class SensorDataProcessor:
    def __init__(self, sensor, publisher):
        self.sensor = sensor
        self.publisher = publisher

    def process_and_publish(self):
        data = self.sensor.read()
        if data:
            humidity = f"{data[0]}.{data[1]}"
            temperature = f"{data[2]}.{data[3]}"
            self.publisher.publish(HUMIDITY_TOPIC, humidity)
            self.publisher.publish(TEMPERATURE_TOPIC, temperature)
            print(f"Humidity: {humidity}, Temperature: {temperature}")
        else:
            print("Failed to read sensor data")


def main():
    pin = 6

    sensor = DHT11Sensor(pin)
    publisher = MQTTPublisher(BROKER_ADDRESS, PORT)
    processor = SensorDataProcessor(sensor, publisher)

    while True:
        processor.process_and_publish()
        time.sleep(5)


if __name__ == "__main__":
    main()
