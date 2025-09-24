from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class TelemetryRequest(BaseModel):
    regions: List[str]
    threshold_ms: int

# Sample telemetry data
TELEMETRY_DATA = {
    "apac": [
        {"latency_ms": 120, "uptime": 1},
        {"latency_ms": 145, "uptime": 1},
        {"latency_ms": 200, "uptime": 1},
        {"latency_ms": 110, "uptime": 0},
        {"latency_ms": 180, "uptime": 1},
        {"latency_ms": 165, "uptime": 1},
        {"latency_ms": 190, "uptime": 1},
        {"latency_ms": 130, "uptime": 1},
        {"latency_ms": 175, "uptime": 1},
        {"latency_ms": 155, "uptime": 1},
    ],
    "amer": [
        {"latency_ms": 95, "uptime": 1},
        {"latency_ms": 105, "uptime": 1},
        {"latency_ms": 170, "uptime": 1},
        {"latency_ms": 185, "uptime": 1},
        {"latency_ms": 90, "uptime": 0},
        {"latency_ms": 150, "uptime": 1},
        {"latency_ms": 160, "uptime": 1},
        {"latency_ms": 140, "uptime": 1},
        {"latency_ms": 125, "uptime": 1},
        {"latency_ms": 135, "uptime": 1},
    ]
}

@app.post("/analyze")
def analyze_latency(request: TelemetryRequest):
    """
    Analyze telemetry data for specified regions
    """
    results = {}
    
    for region in request.regions:
        data = TELEMETRY_DATA.get(region, [])
        
        if not data:
            results[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue
        
        latencies = [record["latency_ms"] for record in data]
        uptimes = [record["uptime"] for record in data]
        
        results[region] = {
            "avg_latency": round(np.mean(latencies), 2),
            "p95_latency": round(np.percentile(latencies, 95), 2),
            "avg_uptime": round(np.mean(uptimes), 3),
            "breaches": sum(1 for lat in latencies if lat > request.threshold_ms)
        }
    
    return results

