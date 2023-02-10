#!/usr/bin/env python3
"""Main runnable file for the codebase"""

import argparse
import logging
import asyncio
from multiprocessing import Queue
from flight import logger, upload_mission
import flight.config as config
from mavsdk import System
from flight import upload_mission
from flight.run_mission import run_mission
from flight.flight import wait_for_drone, log_flight_mode, observe_is_in_air, DroneNotFoundError

SIM_ADDR: str = "udp://:14540"  # Address to connect to the simulator
CONTROLLER_ADDR: str = "serial:///dev/ttyUSB0"  # Address to connect to a pixhawk board

async def init_and_begin(simulation: bool, competition: bool) -> None:
    """
    Creates drone object and passes it to start_flight
    Parameters
    ----------
        self
            self for commands current drone situation
        simulation: bool
            boolean that helps decide where the drone lands
    """
    try:
        drone: System = await init_drone(simulation)
        await start_flight(drone, competition)
    except DroneNotFoundError:
        logging.exception("Drone was not found")
        return
    except:
        logging.exception("Uncaught error occurred")
        return

async def start_flight(drone: System, competition: bool) -> None:
    # Run config params in config file
    await config.config_params(drone)

    log_queue: Queue = Queue(-1)
    logger.worker_configurer(log_queue)
    logging.debug("Flight process started")

    # Continuously log flight mode changes
    flight_mode_task = asyncio.ensure_future(log_flight_mode(drone))
    # Will stop flight code if the drone lands
    termination_task = asyncio.ensure_future(observe_is_in_air(drone))

    try:
        logging.debug("Running upload_mission")
        await upload_mission.upload_mission(competition)
        logging.debug("Running run_mission")
        await run_mission(competition)
    except:
        logging.exception("Exception in flight process occurred")

async def init_drone(simulation: bool) -> System:
    # Connect to drone with either sim or controller address depending on simulation boolean.
    sys_addr: str = SIM_ADDR if simulation else CONTROLLER_ADDR
    drone: System = System()
    await drone.connect(system_address=sys_addr)
    logging.debug("Waiting for drone to connect...")
    try:
        await asyncio.wait_for(wait_for_drone(drone), timeout=5)
    except asyncio.TimeoutError:
        raise DroneNotFoundError()
    return drone

if __name__ == "__main__":

    logging.info(">> Starting landing process")

    # Parse through arguments, create competition and simulation variables.
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-c", "--competition", help="Using the competition waypoints", action="store_true")
    parser.add_argument("-s", "--simulation", help="Using a simulator", action="store_true")
    args = parser.parse_args()
    competition: bool = args.competition
    simulation: bool = args.simulation
    logging.debug("Competition flag %s", "enabled" if competition else "disabled")
    logging.debug("Simulation flag %s", "enabled" if simulation else "disabled")

    """Starts the asyncronous event loop for the flight code"""
    asyncio.get_event_loop().run_until_complete(
        init_and_begin(simulation, competition)
    )