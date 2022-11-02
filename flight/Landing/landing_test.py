# Pretend Landing Spot: 37.949297, -91.784501, 0
# Landing Spot: "longitude": 37.167814, "latitude": -97.739912
import asyncio
from mavsdk import System
import sys

sys.path.append("/home/alen/Argonia-Cup-2023/flight")
from intake_gps import Waypoint, extract_gps
from goto import move_to
from landing import manual_land
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

    print("-- Arming")
    await drone.action.arm()
    
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

    print("Calculating mission points:")
    # While we could first just move to the latitude and longitude of the target and then go straight down,
    # we can take a way more efficient path by using pythagorean theorem to find optimal points for our
    # speed limit change and landing.
    # We want to first calculate our altitude to get our multiplier for our similar triangles.
    # Altitude:
    speed_limit_alt = 122
    speed_limit_mult = (drone_alt - speed_limit_alt) / drone_alt
    # Latitude:
    speed_limit_lat = target_latitude - ((drone_lat - target_latitude) * speed_limit_mult)
    # Longitude:
    speed_limit_lon = target_longitude - ((drone_long - target_longitude) * speed_limit_mult)
    
    print(f'   Speed Limit Latitude: {speed_limit_lat:.7f}')
    print(f'   Speed Limit Longitude: {speed_limit_lon:.7f}')
    print(f'   Speed Limit Altitude: {speed_limit_alt}')
    
    print("Moving to speed limit point...")
    # Have to round the speed limit location to 7 decimal places, or else the move_to function will get angry.
    await move_to(drone, round(speed_limit_lat,7), round(speed_limit_lon,7), speed_limit_alt)
    
    print("Setting speed limit and moving 50m above target location...")
    await drone.action.set_maximum_speed(6)
    await move_to(drone, target_latitude, target_longitude, 50)
    
    print("Starting landing process...")
    await manual_land(drone, target_latitude, target_longitude)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
