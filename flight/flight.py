"""Launch code for flight state machine"""
import logging
from mavsdk import System

SIM_ADDR: str = "udp://:14540"  # Address to connect to the simulator
CONTROLLER_ADDR: str = "serial:///dev/ttyUSB0"  # Address to connect to a pixhawk board


class DroneNotFoundError(Exception):
    """
    Exception for when the drone doesn't connect
    """
    logging.warning("DRONE NOT FOUND!")
    pass

async def log_flight_mode(drone: System) -> None:
    """
    Logs the flight modes entered during flight by the drone
    Parameters
    ----------
        drone: System
            MAVSDK object to access drone properties
    """
    previous_flight_mode: str = ""

    async for flight_mode in drone.telemetry.flight_mode():
        if flight_mode is not previous_flight_mode:
            previous_flight_mode: str = flight_mode
            logging.debug("Flight mode: %s", flight_mode)


async def observe_is_in_air(drone: System, self) -> None:
    """
    Monitors whether the drone is flying or not and
    returns after landing
    Parameters
    ----------
        drone: System
            MAVSDK object for drone control
        self
            self for commands current drone situation
    """

    was_in_air: bool = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air: bool = is_in_air

        if was_in_air and not is_in_air:
            self.__state = "exit"
            return


async def wait_for_drone(drone: System) -> None:
    """
    Waits for the drone to be connected and returns
    Parameters
    ----------
        drone: System
            MAVSDK object for drone control
    """
    async for state in drone.core.connection_state():
        if state.is_connected:
            logging.info("Connected to drone with UUID %s", state.uuid)
            return

async def check_for_exit(drone: System) -> None:
    try:
        pass
    except KeyboardInterrupt:
        # Ctrl-C was pressed
        # TODO send a message to the flight process to land instead of
        # basically overwriting the process
        logging.info("Ctrl-C Pressed, forcing drone to land")
        await drone.land

        logging.info("Drone landed, goodbye!")
