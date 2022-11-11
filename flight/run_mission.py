"""
Tests the goto function through a mission
"""
import asyncio
import sys

from mavsdk import System

import logging

from mavsdk.mission import MissionItem, MissionPlan

from intake_gps import Waypoint, extract_gps
from goto import move_to
from landing import manual_land
import argparse


async def run_mission(path: str = "flight/data/target_data.json") -> None:
    """
    Tests the goto function by moving the drone to four different waypoints.

     Parameters
    ----------
    path : str
        File path to the target data JSON file.
    """
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break

    # Set an initial speed limit
    await drone.action.set_maximum_speed(20)

    print("Getting target location and ground altitude for landing...")
    target_data: Waypoint
    ground_altitude: float
    target_data, ground_altitude = extract_gps(path)
    target_latitude = target_data[0]
    target_longitude = target_data[1]

    await drone.mission.start_mission()

    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission upload: {mission_progress.current}/{mission_progress.total}")
        if mission_progress.current == mission_progress.total:
            print("-- Mission Completed!")
            break
        await asyncio.sleep(5)

    print("Starting landing process...")
    await manual_land(drone, target_latitude, target_longitude)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    # Read file to be used as the data file using the -file argument
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-file")
    args: argparse.Namespace = parser.parse_args()

    loop.run_until_complete(run_mission(vars(args)["file"]))
