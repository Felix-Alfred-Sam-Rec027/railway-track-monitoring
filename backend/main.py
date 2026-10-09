
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone

app = FastAPI(
    title="Railway Track Monitoring API",
    description="Indigenous Track Fault Detection & Monitoring System",
    version="1.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary in-memory storage for live sensor readings.
# Data resets when the server restarts.
latest_readings = {}


class SensorReading(BaseModel):
    rail_id: str
    temperature: float | None = None
    humidity: float | None = None
    distance: float | None = None
    accel_x: int | None = None
    accel_y: int | None = None
    accel_z: int | None = None
    crack_status: str = "UNKNOWN"


@app.get("/")
def home():
    return {
        "message": "Railway Track Monitoring Backend is running",
        "status": "online"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/sensor-data")
def receive_sensor_data(reading: SensorReading):
    rail_id = reading.rail_id.upper()

    if rail_id not in ("RAIL1", "RAIL2"):
        return {
            "status": "error",
            "message": "rail_id must be RAIL1 or RAIL2"
        }

    latest_readings[rail_id] = {
        **reading.model_dump(),
        "rail_id": rail_id,
        "received_at": datetime.now(timezone.utc).isoformat()
    }

    return {
        "status": "received",
        "rail_id": rail_id,
        "message": "Sensor reading stored successfully"
    }


@app.get("/sensors")
def get_sensors():
    return latest_readings


@app.get("/sensors/{rail_id}")
def get_rail_sensors(rail_id: str):
    rail_id = rail_id.upper()

    if rail_id not in latest_readings:
        return {
            "status": "waiting",
            "message": f"No data received yet for {rail_id}"
        }

    return latest_readings[rail_id]
