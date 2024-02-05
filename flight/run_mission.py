"""
runs a mission from a json file to get the drone above a target and lands it
"""

import asyncio
import logging

from mavsdk import System
from flight import intake_gps, landing

import argparse


async def run_mission(competition: bool) -> None:
    """
    Uses data from a json file to retrieve a mission then runs it to get the drone above the target
    once the drone gets 225 feet above the ground the landing code is run which brings it down
    at progressively slower speeds precisely over the target till it lands the drone and shut down

    Parameters
    ----------
    competition : bool
        Decides if competition waypoint are used in the mission or not.

    Notes
    -----
    Drone will be shut off after this is run
    It can be run by python3 run_mission.py -file {json file path}
    """

    waypoint: str
    if competition:
        waypoint = "flight/data/target_data.json"
    else:
        waypoint = "flight/data/golf_target.json"

    drone = System()
    await drone.connect(system_address="udp://:14540")

    logging.info("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            logging.info("Drone discovered!")
            break

    # Set an initial speed limit
    await drone.action.set_maximum_speed(20)

    logging.info("Getting target location and ground altitude for landing...")
    target_data: intake_gps.Waypoint
    ground_altitude: float
    target_data, ground_altitude = await intake_gps.extract_gps(waypoint)
    target_latitude = target_data[0]
    target_longitude = target_data[1]
    await drone.mission.start_mission()
    logging.info("running the mission")
    # Once the drone is below 75m the slow landing code begins to run
    # This is needed as the mission won't end unless a break is included
    async for position in drone.telemetry.position():
        current_altitude: float = round(position.relative_altitude_m, 3)
        if current_altitude < 75.0:
            break

    logging.info("Starting landing process...")
    await landing.manual_land(drone, target_latitude, target_longitude)


if __name__ == "__main__":
    """
    runs run_mission to land a drone with a mission from a json file then lands it precisely
    from the coordinates given by the json
    This is run by python3 run_mission.py -file {json file path}
    If no file path is specified it will use the default target data file path
    """
    # Read file to be used as the data file using the -file argument
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-file")
    args: argparse.Namespace = parser.parse_args()

    DATA_PATH = vars(args)["file"]
    if DATA_PATH is None:
        DATA_PATH = "flight/data/target_data.json"
    asyncio.run(run_mission(DATA_PATH))
