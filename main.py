import json

import troykahat
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from w1thermsensor import W1ThermSensor

from core import get_tds, command_engine
from models import EngineOn, Engine

with open('config.json') as f:
    config = json.load(f)

app = FastAPI()

ap = troykahat.analog_io()
wp = troykahat.wiringpi_io()
ap.pinMode(config['PIN_TDS'], ap.INPUT)
for el in config['engines'].keys():
    ap.pinMode(config['engines'][el]['pwm'], ap.OUTPUT)
    wp.pinMode(config['engines'][el]['1'], wp.OUTPUT)
    wp.pinMode(config['engines'][el]['2'], wp.OUTPUT)

sensor = W1ThermSensor()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/telemetry")
def index() -> dict[str, str]:
    return {
        "temp": round(sensor.get_temperature(), 2),
        "tds": get_tds(ap.analogRead(config['PIN_TDS']) * 4095)
    }


@app.post("/api/engine/on")
def engine(command: EngineOn):
    command_engine(ap, wp, command.id, command.speed, config, command.reverse)
    return {'message': f'Engine {command.id} is on'}


@app.post("/api/engine/off")
def engine(command: Engine):
    command_engine(ap, wp, command.id, 0, config, False)
    return {'message': f'Engine {command.id} is off'}


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=2, reload=True)
