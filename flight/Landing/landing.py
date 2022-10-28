from mavsdk import System
import mavsdk as sdk
import logging
import goto

async def manual_land(drone: System, Target_Latitude, Target_Longitude) -> None:
        """
        Function to increasingly slowly land the drone while honing in on the target
        Parameters:
                drone(System, Target_Latitude, Target_Longitude): our drone object
        Return:
            None
        """
        # Lands the drone using manual velocity values
        logging.info("Landing the drone")
        async for position in drone.telemetry.position():
            current_altitude: float = round(position.relative_altitude_m, 3)
            if current_altitude > 10.0:
                await drone.action.set_current_speed(4)
                await goto.move_to(drone, Target_Latitude, Target_Longitude, 9.5)
            elif 10.0 > current_altitude > 1.0:
                # Descends at 0.7 m/s at altitudes > 1 m
                await drone.action.set_current_speed(2.5)
                await goto.move_to(drone, Target_Latitude, Target_Longitude, .9)
            elif 1.0 > current_altitude > 0.5:
                # Descends at 0.35 m/s at altitudes < 1 m && > 0.5 m
                await drone.action.set_current_speed(1.75)
                await goto.move_to(drone, Target_Latitude, Target_Longitude, .4)
            elif 0.5 > current_altitude > 0.15:
                # Descends at 0.1 m/s at altitudes < 0.5 m && > 0.15 m
                await drone.action.set_current_speed(1)
                await goto.move_to(drone, Target_Latitude, Target_Longitude, .1)
            else:
                # Sets downward velocity to 0 otherwise
                await drone.offboard.set_velocity_body(
                    sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
                )
                logging.info("Disarming the drone")
                await drone.action.kill()
                return
