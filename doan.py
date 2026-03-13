import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from rpi_ws281x import PixelStrip, Color
import mysql.connector
import time
import os

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

DOOR_SERVO_PIN = 23
ROOF_SERVO_PIN = 22
RAIN_PIN = 24
RST_PIN = 25

LED_PIN = 18
LED_COUNT = 8

GPIO.setup(DOOR_SERVO_PIN, GPIO.OUT)
GPIO.setup(ROOF_SERVO_PIN, GPIO.OUT)
GPIO.setup(RAIN_PIN, GPIO.IN)
GPIO.setup(RST_PIN, GPIO.OUT)

door_servo = GPIO.PWM(DOOR_SERVO_PIN,50)
roof_servo = GPIO.PWM(ROOF_SERVO_PIN,50)

door_servo.start(0)
roof_servo.start(0)

strip = PixelStrip(LED_COUNT, LED_PIN)
strip.begin()


def led_green():
    for i in range(LED_COUNT):
        strip.setPixelColor(i,Color(0,255,0))
    strip.show()


def led_red():
    for i in range(LED_COUNT):
        strip.setPixelColor(i,Color(255,0,0))
    strip.show()


def led_off():
    for i in range(LED_COUNT):
        strip.setPixelColor(i,Color(0,0,0))
    strip.show()


def reset_rfid():

    GPIO.output(RST_PIN,0)
    time.sleep(0.1)
    GPIO.output(RST_PIN,1)
    time.sleep(0.1)


print("Khoi dong RFID...")

time.sleep(3)

reset_rfid()

reader = SimpleMFRC522()


db = mysql.connector.connect(
    host="localhost",
    user="iot",
    password="123456",
    database="smart_home",
    autocommit=True
)

cursor = db.cursor(dictionary=True)


def servo_move(servo,duty):

    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)
    servo.ChangeDutyCycle(0)


def door_open():
    servo_move(door_servo,5.5)


def door_close():
    servo_move(door_servo,2.5)


def roof_open():
    servo_move(roof_servo,2.5)


def roof_close():
    servo_move(roof_servo,7.5)


door_state = "CLOSE"
roof_state = None

door_timer = 0
door_opening = False

light_state = None

last_uid = None
last_seen = 0

CARD_TIMEOUT = 2

try:

    while True:

        cursor.execute("SELECT mode FROM system LIMIT 1")
        mode = cursor.fetchone()["mode"].strip().upper()

        rain = GPIO.input(RAIN_PIN)

        if rain == 0:

            if roof_state != "CLOSE":

                roof_close()
                roof_state = "CLOSE"

                cursor.execute("UPDATE devices SET status='MUA' WHERE type='rain'")

        else:

            if roof_state != "OPEN":

                roof_open()
                roof_state = "OPEN"

                cursor.execute("UPDATE devices SET status='KHO' WHERE type='rain'")


        if mode == "AUTO":

            try:

                uid = reader.read_id_no_block()

            except:

                print("RFID loi -> reset")

                reset_rfid()
                reader = SimpleMFRC522()
                uid = None


            if uid:

                uid = str(uid)

                last_seen = time.time()

                if uid != last_uid:

                    last_uid = uid

                    cursor.execute(
                        "SELECT * FROM users WHERE rfid_uid=%s",
                        (uid,)
                    )

                    user = cursor.fetchone()

                    if user:

                        print("Access OK")

                        led_green()

                        if door_state == "CLOSE":

                            door_open()

                            cursor.execute(
                                "INSERT INTO rfid_logs(rfid_uid,result) VALUES(%s,'ACCESS')",
                                (uid,)
                            )

                            door_timer = time.time()
                            door_opening = True
                            door_state = "OPEN"

                    else:

                        print("Access Denied")

                        led_red()

                        cursor.execute(
                            "INSERT INTO rfid_logs(rfid_uid,result) VALUES(%s,'DENIED')",
                            (uid,)
                        )

            else:

                if last_uid and time.time() - last_seen > CARD_TIMEOUT:

                    last_uid = None
                    led_off()


            if door_opening and time.time() - door_timer > 5:

                door_close()
                door_opening = False
                door_state = "CLOSE"


        if mode == "MANUAL":

            cursor.execute("SELECT status FROM devices WHERE type='servo'")
            cmd = cursor.fetchone()["status"]

            if cmd == "OPEN" and door_state != "OPEN":

                door_open()
                door_state = "OPEN"

            if cmd == "CLOSE" and door_state != "CLOSE":

                door_close()
                door_state = "CLOSE"


            cursor.execute("SELECT status FROM devices WHERE type='light'")
            light = cursor.fetchone()["status"]

            if light == "ON" and light_state != "ON":

                led_green()
                light_state = "ON"

            if light == "OFF" and light_state != "OFF":

                led_off()
                light_state = "OFF"


        time.sleep(0.05)


except KeyboardInterrupt:
    pass


finally:

    door_servo.stop()
    roof_servo.stop()
    GPIO.cleanup()
