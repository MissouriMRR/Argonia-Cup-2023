"""Launch code for flight state machine"""
import asyncio
import logging
import config
from mavsdk import System
import mavsdk as sdk
from multiprocessing import Queue

import logger
from ..run import simulation

SIM_ADDR: str = "udp://:14540"  # Address to connect to the simulator
CONTROLLER_ADDR: str = "serial:///dev/ttyUSB0"  # Address to connect to a pixhawk board


class DroneNotFoundError(Exception):
    """Exception for when the drone doesn't connect"""
    logging.warning("WARNING!!!! DRONE NOT FOUND!?!?!?!?@@!@?!@")
    pass

async def _check_arm_or_arm(self, drone: System) -> None:
        """
        Verifies that the drone is armed, if not armed, arms the drone
        Parameters
        ---------
            drone: System
                The drone system; used for flight operations.
        Returns
        -------
            None
        """
        async for is_armed in drone.telemetry.armed():
            if not is_armed:
                logging.debug("Not armed. Attempting to arm")
                await drone.action.arm()
            else:
                logging.warning("Drone armed")
                break

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
        comm: Communication
            Communication object for collaboration in pipeline
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


def flight(self, log_queue: Queue, simulation) -> None:
    """
    Starts the asynchronous event loop for the flight code
    Parameters
    ----------
        comm: Communication
            Communication object for collaboration in pipeline
        log_queue: Queue
            Queue object to hold logging processes
        state_settings: StateSettings
            Settings for the flight state machine
    """
    logger.worker_configurer(log_queue)
    logging.debug("Flight process started")
    asyncio.get_event_loop().run_until_complete(init_and_begin(self, simulation))


async def init_and_begin(self, simulation) -> None:
    """
    Creates drone object and passes it to start_flight
    Parameters
    ----------
        comm: Communication
            Communication object for collaboration in pipeline
        state_settings: StateSettings
            Settings for flight state machine
    """
    try:
        drone: System = await init_drone(simulation)
        await start_flight(self, drone)
    except DroneNotFoundError:
        logging.exception("Drone was not found")
        return
    except:
        logging.exception("Uncaught error occurred")
        return


async def init_drone(simulation) -> System:
    """
    Connects to the pixhawk or simulator and returns the drone
    Parameters
    ----------
        state_settings: StateSettings
            Settings for flight state machine
    Returns
    -------
        System
            MAVSDK System object corresponding to the drone
    """

    sys_addr: str = SIM_ADDR if run.simulation else CONTROLLER_ADDR
    drone: System = System()
    await drone.connect(system_address=sys_addr)
    logging.debug("Waiting for drone to connect...")
    try:
        await asyncio.wait_for(wait_for_drone(drone), timeout=5)
    except asyncio.TimeoutError:
        raise DroneNotFoundError()

    # Add lines to control takeoff height
    # config drone param's
    await config.config_params(drone)
    return drone


async def start_flight(self, drone: System) -> None:
    """
    Creates the state machine and watches for exceptions
    Parameters
    ----------
        comm: Communication
            Communication object for collaboration in pipeline
        drone: System
            MAVSDK object for physcial control of the drone
        state_settings: StateSettings
            Settings for flight state machine
    """
    # Continuously log flight mode changes
    flight_mode_task = asyncio.ensure_future(log_flight_mode(drone))
    # Will stop flight code if the drone lands
    termination_task = asyncio.ensure_future(observe_is_in_air(drone, self))

    try:
        # Initialize the state machine at the current state
        self.__state != ""
    except Exception:
        logging.exception("Exception occurred in state machine")
        try:
            await drone.offboard.set_position_ned(
                sdk.offboard.PositionNedYaw(0, 0, 0, 0)
            )
            await drone.offboard.set_velocity_ned(
                sdk.offboard.VelocityNedYaw(0, 0, 0, 0)
            )
            await drone.offboard.set_velocity_body(
                sdk.offboard.VelocityBodyYawspeed(0, 0, 0, 0)
            )

            await asyncio.sleep(config.WAIT)

            try:
                await drone.offboard.stop()
            except sdk.offboard.OffboardError as error:
                logging.exception(
                    "Stopping offboard mode failed with error code: %s", str(error)
                )
                # Worried about what happens here
            await asyncio.sleep(config.WAIT)
            logging.info("Landing the drone")
            await drone.action.land()
        except:
            logging.error("No system available")
            self.__state = "final"
            return

    self.__state = "final"

    await termination_task
    flight_mode_task.cancel()