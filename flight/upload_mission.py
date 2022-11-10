import argparse
import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan

from intake_gps import Waypoint, extract_gps

async def upload_mission(path='flight/data/target_data.json') -> None:
    """
    Connects to the drone and uploads the mission plan for landing the drone.
    
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

    print("Getting target location and ground altitude for landing...")
    target_data: Waypoint
    ground_altitude: float
    target_data, ground_altitude = extract_gps(path)
    print(f"Target Location: {target_data}")
    print(f"Altitude: {ground_altitude}")
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

    print("Uploading mission...")
    await drone.mission.upload_mission(landing_mission)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    
    # Read file to be used as the data file using the -file argument
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-file")
    args: argparse.Namespace = parser.parse_args()
    
    loop.run_until_complete(upload_mission(vars(args)["file"]))