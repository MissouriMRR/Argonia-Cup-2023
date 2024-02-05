"""
Connects to the drone and uploads the mission plan for landing the drone.
"""

import argparse
import asyncio
import logging
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from flight import intake_gps


async def upload_mission(competition: bool) -> None:
    """
    Connects to the drone and uploads the mission plan for landing the drone.

    Parameters
    ----------
    competition : bool
        Decides if competition waypoints are used in the mission or not.
    """

    waypoint_path: str
    if competition:
        waypoint_path = "flight/data/target_data.json"
    else:
        waypoint_path = "flight/data/golf_target.json"

    drone = System()
    await drone.connect(system_address="udp://:14540")

    logging.info("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            logging.info("Drone discovered!")
            break

    logging.info("Getting target location and ground altitude for landing...")
    target_data: intake_gps.Waypoint
    ground_altitude: float
    target_data, ground_altitude = await intake_gps.extract_gps(waypoint_path)
    logging.info(f"Target Location: {target_data}")
    logging.info(f"Altitude: {ground_altitude}")
    target_latitude = target_data[0]
    target_longitude = target_data[1]

    # Clear mission on drone if there is one
    await drone.mission.clear_mission()

    # Create the mission plan
    # 122m = 400 ft
    speed_limit_point = MissionItem(
        target_latitude,
        target_longitude,
        122,
        20,
        True,
        float("nan"),
        float("nan"),
        MissionItem.CameraAction.NONE,
        float("nan"),
        float("nan"),
        0.001,
        0,
        0,
    )

    # Activate speed limit
    above_target_point = MissionItem(
        target_latitude,
        target_longitude,
        50,
        6,
        True,
        float("nan"),
        float("nan"),
        MissionItem.CameraAction.NONE,
        float("nan"),
        float("nan"),
        0.0001,
        0,
        0,
    )

    landing_mission = MissionPlan([speed_limit_point, above_target_point])

    logging.info("Uploading mission...")
    await drone.mission.upload_mission(landing_mission)


if __name__ == "__main__":
    """
    Uploads a mission plan to QGroundControl for the drone to land at a target.
    This is run by python3 upload_mission.py -file {json file path}.
    If no file path is specified it will use the default target data file path.
    """
    # Read file to be used as the data file using the -file argument
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-file")
    args: argparse.Namespace = parser.parse_args()

    # Use default target data if no file is specified
    DATA_PATH = vars(args)["file"]
    if DATA_PATH is None:
        DATA_PATH = "flight/data/target_data.json"
    asyncio.run(upload_mission(DATA_PATH))
