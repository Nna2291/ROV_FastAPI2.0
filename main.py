import json

import troykahat
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import RPi.GPIO as GPIO

import ms5837
from models import EngineOn, Engine

with open('config.json') as f:
    config = json.load(f)

app = FastAPI()
sensor = ms5837.MS5837_30BA()
if not sensor.init():
    print("Sensor could not be initialized")
    exit(1)

if not sensor.read():
    print("Sensor read failed!")
    exit(1)

saltwaterDepth = sensor.depth()  # No nead to read() again
sensor.setFluidDensity(1000)  # kg

ap = troykahat.analog_io()
wp = troykahat.wiringpi_io()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORK_TIME = config['WORK_TIME']
DUTY_CYCLE = config['DUTY_CYCLE']
FREQUENCY = config['FREQUENCY']
ap.pinMode(config['PIN_TDS'], ap.INPUT)
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

engines = []


@app.on_event('startup')
def init_data():
    for el in config['engines']:
        en1 = config['engines'][el]['1']
        en2 = config['engines'][el]['2']
        GPIO.setup(en1, GPIO.OUT)
        GPIO.setup(en2, GPIO.OUT)
        try:
            pwm1 = GPIO.PWM(en1, FREQUENCY)
            pwm2 = GPIO.PWM(en2, FREQUENCY)
            pwm1.start(0)
            pwm2.start(0)
            engines.append([pwm1, pwm2])
            print('done')
        except:
            print('err')
    print(engines)


@app.get("/api/telemetry")
def index() -> dict[str, str]:
    if sensor.read():
        return {
            "depth": round(sensor.depth(), 2),
            "temp": round(sensor.temperature(), 2)
        }

@app.post("/api/engine/on")
def engine_on(command: EngineOn):
    i = command.speed
    # return 'ok'
    if command.id1 == 0:
        en2 = engines[command.id2 - 1][int(command.reverse2)]
        en2.ChangeDutyCycle(i)
        return
    if command.id2 == 0:
        en1 = engines[command.id1 - 1][int(command.reverse1)]
        en1.ChangeDutyCycle(i)
        return
    en1 = engines[command.id1 - 1][int(command.reverse1)]
    en2 = engines[command.id2 - 1][int(command.reverse2)]
    en1.ChangeDutyCycle(i)
    en2.ChangeDutyCycle(i)


@app.post("/api/engine/off")
def engine_off(command: Engine):
    # return 'ok'
    en1 = engines[command.id1 - 1][0]
    en2 = engines[command.id2 - 1][0]
    en1.ChangeDutyCycle(0)
    en2.ChangeDutyCycle(0)
    en1 = engines[command.id1 - 1][1]
    en2 = engines[command.id2 - 1][1]
    en1.ChangeDutyCycle(0)
    en2.ChangeDutyCycle(0)


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1, reload=True)
