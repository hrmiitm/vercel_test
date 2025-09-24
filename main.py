from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import numpy as np

app = FastAPI(title="eShopCo Latency Monitor", version="1.0.0")

# More comprehensive CORS configuration for Vercel
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

class RegionMetrics(BaseModel):
    avg_latency: float
    p95_latency: float
    avg_uptime: float
    breaches: int

def load_sample_data():
    """Load sample telemetry data - replace this with actual data loading logic"""
    return {
        "apac": [
            {"latency_ms": 120, "uptime": 1, "timestamp": "2024-01-01T00:00:00Z"},
            {"latency_ms": 145, "uptime": 1, "timestamp": "2024-01-01T00:01:00Z"},
            {"latency_ms": 200, "uptime": 1, "timestamp": "2024-01-01T00:02:00Z"},
            {"latency_ms": 110, "uptime": 0, "timestamp": "2024-01-01T00:03:00Z"},
            {"latency_ms": 180, "uptime": 1, "timestamp": "2024-01-01T00:04:00Z"},
            {"latency_ms": 165, "uptime": 1, "timestamp": "2024-01-01T00:05:00Z"},
            {"latency_ms": 190, "uptime": 1, "timestamp": "2024-01-01T00:06:00Z"},
            {"latency_ms": 130, "uptime": 1, "timestamp": "2024-01-01T00:07:00Z"},
            {"latency_ms": 175, "uptime": 1, "timestamp": "2024-01-01T00:08:00Z"},
            {"latency_ms": 155, "uptime": 1, "timestamp": "2024-01-01T00:09:00Z"},
        ],
        "amer": [
            {"latency_ms": 95, "uptime": 1, "timestamp": "2024-01-01T00:00:00Z"},
            {"latency_ms": 105, "uptime": 1, "timestamp": "2024-01-01T00:01:00Z"},
            {"latency_ms": 170, "uptime": 1, "timestamp": "2024-01-01T00:02:00Z"},
            {"latency_ms": 185, "uptime": 1, "timestamp": "2024-01-01T00:03:00Z"},
            {"latency_ms": 90, "uptime": 0, "timestamp": "2024-01-01T00:04:00Z"},
            {"latency_ms": 150, "uptime": 1, "timestamp": "2024-01-01T00:05:00Z"},
            {"latency_ms": 160, "uptime": 1, "timestamp": "2024-01-01T00:06:00Z"},
            {"latency_ms": 140, "uptime": 1, "timestamp": "2024-01-01T00:07:00Z"},
            {"latency_ms": 125, "uptime": 1, "timestamp": "2024-01-01T00:08:00Z"},
            {"latency_ms": 135, "uptime": 1, "timestamp": "2024-01-01T00:09:00Z"},
        ],
        "emea": [
            {"latency_ms": 85, "uptime": 1, "timestamp": "2024-01-01T00:00:00Z"},
            {"latency_ms": 115, "uptime": 1, "timestamp": "2024-01-01T00:01:00Z"},
            {"latency_ms": 175, "uptime": 1, "timestamp": "2024-01-01T00:02:00Z"},
            {"latency_ms": 195, "uptime": 1, "timestamp": "2024-01-01T00:03:00Z"},
            {"latency_ms": 100, "uptime": 1, "timestamp": "2024-01-01T00:04:00Z"},
            {"latency_ms": 125, "uptime": 1, "timestamp": "2024-01-01T00:05:00Z"},
            {"latency_ms": 155, "uptime": 0, "timestamp": "2024-01-01T00:06:00Z"},
            {"latency_ms": 135, "uptime": 1, "timestamp": "2024-01-01T00:07:00Z"},
            {"latency_ms": 165, "uptime": 1, "timestamp": "2024-01-01T00:08:00Z"},
            {"latency_ms": 145, "uptime": 1, "timestamp": "2024-01-01T00:09:00Z"},
        ]
    }

def calculate_metrics(data: List[Dict], threshold_ms: int) -> RegionMetrics:
    """Calculate metrics for a region's telemetry data"""
    if not data:
        return RegionMetrics(avg_latency=0, p95_latency=0, avg_uptime=0, breaches=0)
    
    # Extract latency and uptime values
    latencies = [record["latency_ms"] for record in data]
    uptimes = [record["uptime"] for record in data]
    
    # Calculate metrics
    avg_latency = np.mean(latencies)
    p95_latency = np.percentile(latencies, 95)
    avg_uptime = np.mean(uptimes)
    breaches = sum(1 for lat in latencies if lat > threshold_ms)
    
    return RegionMetrics(
        avg_latency=round(avg_latency, 2),
        p95_latency=round(p95_latency, 2),
        avg_uptime=round(avg_uptime, 3),
        breaches=breaches
    )

# Explicit OPTIONS handler for CORS preflight
@app.options("/analyze")
@app.options("/{path:path}")
async def options_handler(request: Request):
    """Handle CORS preflight requests"""
    return JSONResponse(
        content={},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"message": "eShopCo Latency Monitor API is running"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "eShopCo Latency Monitor"}

@app.post("/analyze", response_model=Dict[str, RegionMetrics])
def analyze_latency(request: TelemetryRequest):
    """
    Analyze telemetry data for specified regions
    
    Args:
        request: TelemetryRequest containing regions list and threshold_ms
    
    Returns:
        Dictionary with region names as keys and RegionMetrics as values
    """
    try:
        # Load telemetry data (in production, this would load from your data source)
        telemetry_data = load_sample_data()
        
        # Validate regions
        available_regions = set(telemetry_data.keys())
        requested_regions = set(request.regions)
        invalid_regions = requested_regions - available_regions
        
        if invalid_regions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid regions: {list(invalid_regions)}. Available regions: {list(available_regions)}"
            )
        
        # Calculate metrics for each requested region
        results = {}
        for region in request.regions:
            region_data = telemetry_data.get(region, [])
            metrics = calculate_metrics(region_data, request.threshold_ms)
            results[region] = metrics
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
