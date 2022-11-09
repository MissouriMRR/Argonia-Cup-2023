import asyncio
from mavsdk import System
import sys

sys.path.append("/home/alen/Argonia-Cup-2023/flight")
from intake_gps import Waypoint, extract_gps
from goto import move_to
from landing import manual_land
from mavsdk.mission import MissionPlan, MissionItem
import logging


async def run() -> None:
    """
    Tests the goto function by moving the drone to four different waypoints.
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
    """ target_data: Waypoint
    ground_altitude: float
    target_data, ground_altitude = extract_gps('/home/alen/Argonia-Cup-2023/flight/data/target_data.json')
    print(f"Target Location: {target_data}")
    print(f"Altitude: {ground_altitude}")
    target_latitude = target_data[0]
    target_longitude = target_data[1] """
    target_latitude = 37.949297
    target_longitude = -91.784501

    print("Getting current location to calculate mission points:")
    async for position in drone.telemetry.position():
        # Assign longitude/latitude (in degrees) and altitude (in meters) to variables
        drone_lat: float = position.latitude_deg
        drone_long: float = position.longitude_deg
        drone_alt: float = position.relative_altitude_m
        print(f"Current Location: {drone_lat}, {drone_long}, {drone_alt}")
        break

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
    loop.run_until_complete(run())
