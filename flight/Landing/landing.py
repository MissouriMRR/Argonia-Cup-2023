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
        # Lands the drone using the goto command to get it centered on the target while landing slowly
        logging.info("Landing the drone")
        async for position in drone.telemetry.position():
            current_altitude: float = round(position.relative_altitude_m, 3)
            print(current_altitude)
            if current_altitude > 10.0:
                print("-- I do be working1")
                print(current_altitude)
                # Descends at 4 feet/s at altitudes > 10 meters down to 27 feets
                await drone.action.set_current_speed(1.5)
                await goto.move_to(drone, Target_Latitude, Target_Longitude, 27)
                print(current_altitude)
                await manual_land(drone, Target_Latitude, Target_Longitude)
                return
            elif 10.0 > current_altitude > 1:
                print("-- I do be working2")
                print(current_altitude)
                # Descends at 1.5 feet/s at altitudes < 10 meters and > .3 meters down to 6 inches
                await drone.action.set_current_speed(1.5)
                await goto.move_to(drone, Target_Latitude, Target_Longitude, .5)
                await manual_land(drone, Target_Latitude, Target_Longitude)
                return
            else:
                print("-- I do be working3")
                # Sets downward velocity to 0 otherwise
                await drone.offboard.set_velocity_body(
                    sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
                )
                # forcebly lands the drone by killing it
                logging.info("Disarming the drone")
                await drone.action.kill()
                return