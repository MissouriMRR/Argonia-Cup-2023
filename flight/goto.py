"""
Contains the move_to function responsible
for moving the drone to a certain location
given latitude, longitude, and altitude.
"""

import asyncio
from mavsdk import System


async def move_to(drone: System, latitude: float, longitude: float, altitude: float) -> None:
    """
    This function takes in a latitude, longitude and altitude and autonomously
    moves the drone to that waypoint. This function will also auto convert the altitude
    from feet to meters.

    Attributes
    ----------
    drone : System
        a drone object that has all offboard data needed for computation
    latitude : float
        a float containing the requested latitude to move to
    longitude : float
        a float containing the requested longitude to move to
    altitude : float
        a float contatining the requested altitude to go to (in feet)
    """

    # Convert the altitude given from feet into meters,
    # as MAVSDK returns altitude data in meters
    altitude = altitude * 0.3048

    # Constantly get the current absolute altitude and assign it to absolute_altitude
    async for terrain_info in drone.telemetry.home():
        absolute_altitude: float = terrain_info.absolute_altitude_m
        break

    # Use the built-in goto_location function from MAVSDK to start moving
    await drone.action.goto_location(latitude, longitude, altitude + absolute_altitude, 0)
    location_reached: bool = False

    # Repeatedly check the drone's location while drone is in motion, and returning the function
    # once the drone has reached the desired location.
    while not location_reached:
        async for position in drone.telemetry.position():
            # Assign longitude/latitude (in degrees) and altitude (in meters) to variables
            drone_lat: float = position.latitude_deg
            drone_long: float = position.longitude_deg
            drone_alt: float = position.relative_altitude_m

            # If drone is within certain distance of the desired waypoint, break.
            # Currently, this target is within .00000001 of a degree, or about a 0.011m radius.
            # Formula: degrees / 111,139 = meters
            if ((round(drone_lat,8)==round(latitude,8)) and
                (round(drone_long,8)==round(longitude,8)) and
                (round(drone_alt,3)==round(altitude,3))):
                location_reached = True
                break

        # Tell process to sleep to prevent contstant polling, preventing battery drain
        await asyncio.sleep(1)
    return
