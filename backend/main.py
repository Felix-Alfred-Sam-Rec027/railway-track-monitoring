from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Railway Track Monitoring API",
    description="Indigenous Track Fault Detection & Monitoring System",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Railway Track Monitoring Backend is running",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/sensors")
def get_sensors():
    return {
        "vibration": 0.32,
        "temperature": 28.4,
        "humidity": 64,
        "battery": 78,
        "ultrasonic": 1.42
    }


@app.get("/track")
def get_track():
    return {
        "track_id": "TRACK-02",
        "kilometer": 125.4,
        "condition": "Good",
        "health": 92
    }


@app.get("/alerts")
def get_alerts():
    return [
        {
            "type": "System Normal",
            "message": "All sensors operating normally",
            "severity": "normal"
        },
        {
            "type": "Abnormal Vibration",
            "message": "Temporary vibration detected",
            "severity": "warning"
        },
        {
            "type": "Track Defect Detected",
            "message": "Inspection recommended at KM 124.8",
            "severity": "danger"
        },
        {
            "type": "Temperature High",
            "message": "Sensor temperature elevated",
            "severity": "warning"
        }
    ]