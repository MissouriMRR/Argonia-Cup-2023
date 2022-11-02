""" just refrences for Landing.py most of this can be ignored just"""


"""Holds all of the movement functions for our drone device"""
from flight import config
from flight.utils.latlon import LatLon
from mavsdk import System
import mavsdk as sdk
import logging
import math


class MovementController:
    """
    Params: Drone, Pylon
    Return: Boolean or None
    Calculates and uses gps coordinates of the drone to move to the location of the target pylon
    """

    async def move_to(self, drone: System, pylon: LatLon) -> bool:
        """
        Function to calculate movement velocity:
        Parameters:
            Drone(System): Our drone object
            Pylon(LatLon): Targets for the drone found using GPS Latitude and Longitude
        Return:
            bool: True or false if the target is within range
            None: If we don't reach the target
        """

        count: int = 0

        async for gps in drone.telemetry.position():
            altitude: float = round(gps.relative_altitude_m, 2)
            # not allowed to go past 15m
            # at or above, go down (positive)
            # below tolerance, go up (negative)

            if altitude >= config.ALT_RANGE_MAX:
                alt = config.ALT_CORRECTION_SPEED  # go down m/s
            elif altitude <= config.ALT_RANGE_MIN:
                alt = -config.ALT_CORRECTION_SPEED  # go up m/s
            else:
                alt = -0.15  # don't move

            # Configure current position and store it
            lat: float = round(gps.latitude_deg, 8)
            lon: float = round(gps.longitude_deg, 8)
            current: float = LatLon(lat, lon)  # you are here

            # Only for first run through loop
            if count == 0:
                # How many degrees we need to turn in order to look at the pylon
                # Think of a unit circle
                deg_to_pylon: float = current.heading_initial(pylon)
                # Creating a new position we need to go to
                # Distance to the offset point from the pylon
                offset_point: float = pylon.offset(deg_to_pylon + config.DEG_OFFSET, config.OFFSET)
                logging.debug(offset_point.to_string("d% %m% %S% %H"))  # you are here
            # distance we have to go in order to get to the offset point
            dist: float = current.distance(offset_point)
            # degrees needed to change to get to offset position
            deg: float = current.heading_initial(offset_point)

            # East, West
            x: float = dist * math.sin(math.radians(deg)) * 1000  # from km to m
            # North, South
            y: float = dist * math.cos(math.radians(deg)) * 1000  # from km to m

            if count == 0:
                reference_x: float = abs(x)
                reference_y: float = abs(y)

                dx: float = math.copysign(
                    config.MAX_SPEED * math.cos(math.asin(y / (math.sqrt((x**2) + (y**2))))),
                    x,
                )
                dy: float = math.copysign(
                    config.MAX_SPEED * math.sin(math.asin(y / (math.sqrt((x**2) + (y**2))))),
                    y,
                )
            # continuously update information on the drone's location
            # and update the velocity of the drone
            await drone.offboard.set_velocity_ned(sdk.offboard.VelocityNedYaw(dy, dx, alt, deg))
            # if the x and y values are close enough (2m) to the original position * precision
            # if inside the circle, move on to the next
            # if outside of the circle, keep running to you get inside
            if (
                abs(x) <= reference_x * config.POINT_PERCENT_ACCURACY
                and abs(y) <= reference_y * config.POINT_PERCENT_ACCURACY
            ):
                return True
            count += 1

    async def turn(self, drone: System) -> bool:
        """
        Turns the drone around the pylon it is currently at
        Parameters:
            Drone(System): Our drone object
        """
        count: int = 0
        async for tel in drone.telemetry.attitude_euler():
            current: float = (360 + round(tel.yaw_deg)) % 360
            if count == 0:
                temp = (current + 180) % 360

            await drone.offboard.set_velocity_body(
                sdk.offboard.VelocityBodyYawspeed(5, -3, -0.1, -60)
            )
            # await asyncio.sleep(config.FAST_THINK_S)
            val = abs(current - temp)
            # TODO: Add case so that it can overshoot the point and still complete
            if val < 10:
                logging.debug("Finished Turn")
                return True
            count += 1

    async def check_altitude(self, drone: System) -> bool:
        """
        Checks the altitude of the drone to make sure that we are at our target
        Parameters:
            Drone(System): Our drone object
        """
        async for position in drone.telemetry.position():
            altitude: float = round(position.relative_altitude_m, 2)
            if altitude >= config.TAKEOFF_ALT:
                return True

    async def takeoff(self, drone: System):
        """Takes off vertically to a height defined by alt"""

        await drone.offboard.set_velocity_ned(
            sdk.offboard.VelocityNedYaw(0.0, 0.0, -1.0, 0.0)
            # Sets the velocity of the drone to be straight up
        )
        await self.check_altitude(drone)
        # Waits until altitude TAKEOFF_ALT is reached, before moving on to EarlyLaps

        return

    async def move_to_takeoff(self, drone: System, takeoff_location: LatLon) -> None:
        """
        Similar to move_to function, but heights are changed so drone only descends when moving
        Parameters:
                drone(System): our drone object
                takeoff_location(LatLon): gives lat & lon of takeoff location
        Return:
            None
        """
        # Moves drone to initial takeoff location
        logging.info("Moving to Takeoff location")
        count: int = 0
        async for gps in drone.telemetry.position():
            altitude: float = round(gps.relative_altitude_m, 2)
            # not allowed to go past 15m
            # at or above, go down (positive)
            # below tolerance, go up (negative)

            if altitude > 2:
                alt = config.ALT_CORRECTION_SPEED  # go down m/s
            elif altitude < 2:
                alt = -config.ALT_CORRECTION_SPEED  # go up m/s
            else:
                alt = -0.15  # don't move

            # Configure current position and store it
            lat: float = round(gps.latitude_deg, 8)
            lon: float = round(gps.longitude_deg, 8)
            current: float = LatLon(lat, lon)  # you are here

            # distance we have to go in order to get to the offset point
            dist: float = current.distance(takeoff_location)
            # degrees needed to change to get to offset position
            deg: float = current.heading_initial(takeoff_location)

            # East, West
            x: float = dist * math.sin(math.radians(deg)) * 1000  # from km to m
            # North, South
            y: float = dist * math.cos(math.radians(deg)) * 1000  # from km to m

            if count == 0:
                reference_x: float = abs(x)
                reference_y: float = abs(y)

                dx: float = math.copysign(
                    config.MAX_SPEED * math.cos(math.asin(y / (math.sqrt((x**2) + (y**2))))),
                    x,
                )
                dy: float = math.copysign(
                    config.MAX_SPEED * math.sin(math.asin(y / (math.sqrt((x**2) + (y**2))))),
                    y,
                )
            # continuously update information on the drone's location
            # and update the velocity of the drone
            await drone.offboard.set_velocity_ned(sdk.offboard.VelocityNedYaw(dy, dx, alt, deg))
            count += 1
            # if the x and y values are close enough (2m) to the original position * precision
            # if inside the circle, move on to the next
            # if outside of the circle, keep running to you get inside
            if (
                abs(x) <= reference_x * config.POINT_PERCENT_ACCURACY
                and abs(y) <= reference_y * config.POINT_PERCENT_ACCURACY
            ):
                return True

    async def manual_land(self, drone: System) -> None:
        """
        Function to slowly land the drone vertically
        Parameters:
                drone(System): our drone object
        Return:
            None
        """
        # Lands the drone using manual velocity values
        logging.info("Landing the drone")
        async for position in drone.telemetry.position():
            current_altitude: float = round(position.relative_altitude_m, 3)
            if current_altitude > 1.0:
                # Descends at 0.7 m/s at altitudes > 1 m
                await drone.offboard.set_velocity_body(
                    sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.7, 0.0)
                )
            elif 1.0 > current_altitude > 0.5:
                # Descends at 0.35 m/s at altitudes < 1 m && > 0.3 m
                await drone.offboard.set_velocity_body(
                    sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.35, 0.0)
                )
            else:
                # Sets downward velocity to 0 otherwise
                await drone.offboard.set_velocity_body(
                    sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
                )
                return


"""
File containing the move_to function responsible
for moving the drone to a certain waypoint
"""

import asyncio
from mavsdk import System
import logging


async def move_to(
    drone: System, latitude: float, longitude: float, altitude: float, fast_mode: bool
) -> None:
    """
    This function takes in a latitude, longitude and altitude and autonomously
    moves the drone to that waypoint. This function will also auto convert the altitude
    from feet to meters.

    Parameters
    ----------
    drone: System
        a drone object that has all offboard data needed for computation
    latitude: float
        a float containing the requested latitude to move to
    longitude: float
        a float containing the requested longitude to move to
    altitude: float
        a float contatining the requested altitude to go to (in feet)
    fast_mode: bool
        a boolean that determines if the drone will take less time checking its precise location
        before moving on to another waypoint. If its true, it will move faster, if it is false,
        it will move at normal speed
    """

    # converts feet into meters
    altitude = altitude * 0.3048

    # get current altitude
    async for terrain_info in drone.telemetry.home():
        absolute_altitude: float = terrain_info.absolute_altitude_m
        break

    await drone.action.goto_location(latitude, longitude, altitude + absolute_altitude, 0)
    location_reached: bool = False
    # First determine if we need to move fast through waypoints or need to slow down at each one
    # Then loops until the waypoint is reached
    if fast_mode == True:
        while not location_reached:
            logging.info("Going to waypoint")
            async for position in drone.telemetry.position():
                # continuously checks current latitude, longitude and altitude of the drone
                drone_lat: float = position.latitude_deg
                drone_long: float = position.longitude_deg
                drone_alt: float = position.relative_altitude_m

                # roughly checks if location is reached and moves on if so
                if (
                    (round(drone_lat, 5) == round(latitude, 5))
                    and (round(drone_long, 5) == round(longitude, 5))
                    and (round(drone_alt, 1) == round(altitude, 1))
                ):
                    location_reached = True
                    logging.info("arrived")
                    break

            # tell machine to sleep to prevent contstant polling, preventing battery drain
            await asyncio.sleep(1)
    else:
        while not location_reached:
            logging.info("Going to waypoint")
            async for position in drone.telemetry.position():
                # continuously checks current latitude, longitude and altitude of the drone
                drone_lat = position.latitude_deg
                drone_long = position.longitude_deg
                drone_alt = position.relative_altitude_m

                # accurately checks if location is reached and moves on if so
                if (
                    (round(drone_lat, 6) == round(latitude, 6))
                    and (round(drone_long, 6) == round(longitude, 6))
                    and (round(drone_alt, 1) == round(altitude, 1))
                ):
                    location_reached = True
                    logging.info("arrived")
                    break

            # tell machine to sleep to prevent contstant polling, preventing battery drain
            await asyncio.sleep(1)
    return
