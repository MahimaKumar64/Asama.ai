from fastapi import APIRouter, HTTPException

from app.services.simulation import (
    get_simulation_status,
    start_simulation as activate_simulation,
    stop_simulation as deactivate_simulation,
)

router = APIRouter(tags=["Simulation"])


@router.get("/simulation/status")
def simulation_status():
    return {
        "simulation_status": get_simulation_status()
    }


@router.post("/simulation/start")
def start_simulation():
    status = activate_simulation()

    return {
        "simulation_status": status,
        "message": "Simulation started. Publisher agents will begin generating posts."
    }


@router.post("/simulation/stop")
def stop_simulation():
    status = deactivate_simulation()

    return {
        "simulation_status": status,
        "message": "Simulation stopped. Already published posts will continue through the routing pipeline."
    }
