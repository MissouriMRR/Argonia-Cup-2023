"""
Contains the extract_gps() function for extracting data out of
a provided target waypoint data JSON file for the Argonia Cup competition.
"""
import asyncio
from typing import Any, NamedTuple
import json


class Waypoint(NamedTuple):
    """
    NamedTuple storing the data for a single waypoint.

    Attributes
    ----------
    latitude : float
        The latitude of the waypoint.
    longitude : float
        The longitude of the waypoint.
    altitude : float
        The altitude of the waypoint.
    """

    latitude: float
    longitude: float
    altitude: float


async def extract_gps(path: str) -> tuple[Waypoint, float]:
    """
    Returns the target location and ground altitude from a json file specified by a parameter.

    Parameters
    ----------
    path : str
        File path to the target data JSON file.

    Returns
    -------
    target_data : Waypoint[float, float, float]
        latitude : float
            The latitude of the target.
        longitude : float
            The longitude of the target.
        altitude : float
            The altitude of the target.
    ground_altitude: float
        The ground altitude of the launch area in ASML (above mean sea level), as the drone
        must navigate using AMSL instead of relative launch altitude.
    """

    # Load the JSON file as a Python dict to be able to easily access the data
    with open(path, encoding="UTF-8") as data_file:
        json_data: dict[str, Any] = json.load(data_file)

    # Define variables for the target's location
    latitude: float = json_data["target"]["latitude"]
    longitude: float = json_data["target"]["longitude"]
    altitude: float = json_data["target"]["altitude"]

    # Package all data into the Waypoint NamedTuple to be exported
    target_data: Waypoint = Waypoint(latitude, longitude, altitude)

    # Name a variable for ground altitude to be exported
    ground_altitude: float = json_data["ground_altitude_amsl"]

    return target_data, ground_altitude


async def main() -> None:
    import argparse

    # Read file to be used as the data file using the -file argument
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-file")
    args: argparse.Namespace = parser.parse_args()

    # Unpack the tuple that is returned
    target_location: Waypoint
    launch_altitude: float

    target_location, launch_altitude = await extract_gps(vars(args)["file"])
    print(f"Target Location: {target_location}")
    print(f"Altitude: {launch_altitude}")


# If run on it's own, use file path from command argument
if __name__ == "__main__":
    asyncio.run(main())
