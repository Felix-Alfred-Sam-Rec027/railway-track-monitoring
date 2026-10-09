
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
import httpx

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

# Render backend that receives readings from the ESP32
RENDER_API_URL = "https://railway-track-monitoring-2.onrender.com"

# Fallback in-memory storage for local sensor submissions
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


# Receive sensor data locally if needed
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
        "message": "Local sensor reading stored successfully"
    }


# Retrieve the latest sensor readings from Render
@app.get("/sensors")
def get_sensors():
    try:
        response = httpx.get(
            f"{RENDER_API_URL}/sensors",
            timeout=15.0
        )
        response.raise_for_status()
        readings = response.json()

        if isinstance(readings, dict) and readings:
            return readings

        return {
            "status": "waiting",
            "message": "No sensor readings have been received yet"
        }

    except httpx.HTTPError as exc:
        return {
            "status": "error",
            "message": "Could not retrieve sensor data from Render",
            "detail": str(exc)
        }


# Retrieve a specific rail's latest reading
@app.get("/sensors/{rail_id}")
def get_rail_sensors(rail_id: str):
    rail_id = rail_id.upper()

    if rail_id not in ("RAIL1", "RAIL2"):
        return {
            "status": "error",
            "message": "rail_id must be RAIL1 or RAIL2"
        }

    try:
        response = httpx.get(
            f"{RENDER_API_URL}/sensors/{rail_id}",
            timeout=15.0
        )
        response.raise_for_status()
        reading = response.json()

        if isinstance(reading, dict) and reading.get("status") == "waiting":
            return reading

        if isinstance(reading, dict) and reading.get("rail_id"):
            return reading

        return {
            "status": "waiting",
            "message": f"No reading available for {rail_id}"
        }

    except httpx.HTTPError as exc:
        return {
            "status": "error",
            "message": f"Could not retrieve data for {rail_id} from Render",
            "detail": str(exc)
        }
