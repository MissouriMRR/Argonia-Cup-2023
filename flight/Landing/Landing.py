from mavsdk import System
import mavsdk as sdk
import logging


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
            # Descends at 0.35 m/s at altitudes < 1 m && > 0.5 m
            await drone.offboard.set_velocity_body(
                sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.35, 0.0)
            )
        elif 0.5 > current_altitude > 0.1:
            # Descends at 0.35 m/s at altitudes < 0.5 m && > 0.1 m
            await drone.offboard.set_velocity_body(
                sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.1, 0.0)
            )
        else:
            # Sets downward velocity to 0 otherwise
            await drone.offboard.set_velocity_body(
                sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
            )
            logging.info("Disarming the drone")
            await drone.action.kill()
            return
