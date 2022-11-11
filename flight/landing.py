"""
Lands the drone precisely on the target using goto and slowing it down as it gets closer to the ground
"""
from mavsdk import System
import mavsdk as sdk
import logging
import goto


async def manual_land(drone: System, Target_Latitude: float, Target_Longitude: float) -> None:
    """
    Function to increasingly slowly land the drone while honing in on the target
    by using goto to lower the drone closer to the ground and to stay above the Target
    Latitude and Longitude, while getting slower everytime it uses goto to get lower
    It calls itself to update the drones location in the code, so it will know its position
    until it gets around 6 inches off the ground then it will shut off the drone allowing it
    to get to the ground from a safe height


    Parameters
    ----------
    drone : System
        a drone object that has all offboard data needed for computation
    Target_Latitude : float
        a float containing the target latitude that needs to be reached
    Target_Longitude : float
        a float containing the target longitude that needs to be reached

    Recursively calls itself to update its own position and when it calls itself
    it should run the next goto to get even lower
    """

    # Lands the drone using the goto command to get it centered on the target while landing slowly
    logging.info("Landing the drone")
    async for position in drone.telemetry.position():
        current_altitude: float = round(position.relative_altitude_m, 3)
        print(current_altitude)
        if current_altitude > 10.0:
            print(current_altitude)
            # Descends at 4.5 feet/s at altitudes > 10 meters down to 27 feet
            await drone.action.set_current_speed(4.5)
            await goto.move_to(drone, Target_Latitude, Target_Longitude, 27)
            print(current_altitude)
            # Calls itself to update its location in the code
            await manual_land(drone, Target_Latitude, Target_Longitude)
            return
        elif 10.0 > current_altitude > 1:
            print(current_altitude)
            # Descends at 1.5 feet/s at altitudes < 10 meters and > 1 meters down to 6 inches
            await drone.action.set_current_speed(1.5)
            await goto.move_to(drone, Target_Latitude, Target_Longitude, 0.5)
            # Calls itself to update its location in the code
            await manual_land(drone, Target_Latitude, Target_Longitude)
            return
        else:
            # Sets downward velocity to 0, so the drone will stop moving
            await drone.offboard.set_velocity_body(
                sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
            )
            # forcebly lands the drone by killing it
            logging.info("Disarming the drone")
            await drone.action.kill()
            return
