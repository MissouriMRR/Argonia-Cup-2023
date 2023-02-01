#!/usr/bin/env python3
"""Main runnable file for the codebase"""

import logging
import flight.config as config
from flight.upload_mission import upload_mission
from flight.run_mission import run_mission

from flight_manager import FlightManager

SIM_ADDR: str = "udp://:14540"  # Address to connect to the simulator
CONTROLLER_ADDR: str = "serial:///dev/ttyUSB0"  # Address to connect to a pixhawk board

if __name__ == "__main__":
    # Parse through arguments, create competition and simulation variables.
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-c", "--competition", help="Using the competition waypoints", action="store_true")
    parser.add_argument("-s", "--simulation", help="Using a simulator", action="store_true")
    args = parser.parse_args()
    competition: bool = args.competition
    simulation: bool = args.simulation
    logging.debug("Competition flag %s", "enabled" if competition else "disabled")
    logging.debug("Simulation flag %s", "enabled" if simulation else "disabled")

    # Connect to drone with either sim or controller address depending on simulation boolean.
    sys_addr: str = SIM_ADDR if simulation else CONTROLLER_ADDR
    drone: System = System()
    await drone.connect(system_address=sys_addr)
    logging.debug("Waiting for drone to connect...")
    try:
        await asyncio.wait_for(wait_for_drone(drone), timeout=5)
    except asyncio.TimeoutError:
        raise DroneNotFoundError()

    # Run config params in config file
    await config.config_params(drone)

    # !! Get rid of this outdated stuff !!
    try:
        logging.debug("Running upload_mission")
        await upload_mission(competition)
        logging.debug("Running run_mission")
        await run_mission(competition)
    except:
        logging.exception("Unfixable error detected")

    # Instead of this, we want to do something that runs:
    # upload_mission.py > run_mission.py
    # We don't need any states if its just two files that need to be run after another