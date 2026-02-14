#!/usr/bin/env python3
"""
Simple GPIO control service for The BlackBox challenges.
Runs alongside theblackbox.py on a different port (5001).

Provides:
  GET /gpio/set?pin=17&state=1   - Set GPIO pin HIGH
  GET /gpio/set?pin=17&state=0   - Set GPIO pin LOW

Requires: pip3 install RPi.GPIO
"""

import RPi.GPIO as GPIO
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Allow CORS from localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track initialized pins
initialized_pins = set()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

@app.get("/gpio/set")
async def gpio_set(pin: int = 0, state: int = 0):
    if pin < 1 or pin > 27:
        return {"error": "Invalid pin number"}

    # Initialize pin if not already done
    if pin not in initialized_pins:
        GPIO.setup(pin, GPIO.OUT)
        initialized_pins.add(pin)

    # Set pin state
    GPIO.output(pin, GPIO.HIGH if state > 0 else GPIO.LOW)
    return {"pin": pin, "state": state}

@app.get("/gpio/cleanup")
async def gpio_cleanup():
    GPIO.cleanup()
    initialized_pins.clear()
    return {"status": "cleanup done"}

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="127.0.0.1", port=5001)
    finally:
        GPIO.cleanup()
