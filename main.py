from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
import json
import os
from collections import defaultdict

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

def load_telemetry_data():
    """Load telemetry data from q-vercel-latency.json"""
    try:
        # Get the current working directory and construct path to JSON file
        json_path = os.path.join(os.getcwd(), 'q-vercel-latency.json')
        
        with open(json_path, 'r') as f:
            raw_data = json.load(f)
        
        # Group data by region
        telemetry_data = defaultdict(list)
        
        for record in raw_data:
            region = record.get('region')
            if region:
                # Convert uptime_pct to decimal (97.807 -> 0.97807)
                uptime_decimal = record.get('uptime_pct', 0) / 100
                
                telemetry_data[region].append({
                    'latency_ms': record.get('latency_ms', 0),
                    'uptime': uptime_decimal,
                    'service': record.get('service', ''),
                    'timestamp': record.get('timestamp', '')
                })
        
        return dict(telemetry_data)
    
    except FileNotFoundError:
        print("q-vercel-latency.json file not found")
        return {}
    except json.JSONDecodeError:
        print("Error parsing JSON file")
        return {}
    except Exception as e:
        print(f"Error loading telemetry data: {e}")
        return {}

@app.post("/analyze")
def analyze_latency(request: TelemetryRequest):
    """
    Analyze telemetry data for specified regions
    """
    # Load data from JSON file
    telemetry_data = load_telemetry_data()
    
    region_metrics = {}
    
    for region in request.regions:
        data = telemetry_data.get(region, [])
        
        if not data:
            region_metrics[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue
        
        latencies = [record["latency_ms"] for record in data]
        uptimes = [record["uptime"] for record in data]
        
        region_metrics[region] = {
            "avg_latency": round(np.mean(latencies), 2),
            "p95_latency": round(np.percentile(latencies, 95), 2),
            "avg_uptime": round(np.mean(uptimes), 3),
            "breaches": sum(1 for lat in latencies if lat > request.threshold_ms)
        }
    
    # Return response with "regions" wrapper
    return {"regions": region_metrics}
