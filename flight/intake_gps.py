"""
Contains the intake_gps() function for extracting data out of
the provided waypoint data JSON file for the SUAS competition.
"""
from typing import Any, NamedTuple
import json
import argparse

# Initialize namedtuples to store latitude/longitude/altitude data for provided points
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


def extract_gps(path: str) -> Waypoint:
    """
    Returns the waypoints, boundary points, and altitude limits from a waypoint data file.
    Parameters
    ----------
    path : str
        File path to the waypoint data JSON file.
    Returns
    -------
    GPSData : TypedDict[
        list[Waypoint[float, float, int]], list[BoundaryPoint[float, float]], list[int, int]
        ]
        The data in the waypoint data file
        waypoints : list[Waypoint[float, float, float]]
            Waypoint : Waypoint[float, float, float]
                latitude : float
                    The latitude of the waypoint.
                longitude : float
                    The longitude of the waypoint.
                altitude : float
                    The altitude of the waypoint.
        boundary_points : list[BoundaryPoint[float, float]]
            BoundaryPoint : BoundaryPoint[float, float]
                latitude : float
                    The latitude of the boundary point.
                longitude : float
                    The longitude of the boundary point.
        altitude_limits : list[int, int]
            altitude_min : int
                The minimum altitude that the drone must fly at all times.
            altitude_max : int
                The maximum altitude that the drone must fly at all times.
    """

    # Load the JSON file as a Python dict to be able to easily access the data
    with open(path, encoding="UTF-8") as data_file:
        json_data: dict[str, Any] = json.load(data_file)
    
    target: list[float] = json_data["target"]

    ground_altitude: float = json_data["ground_altitude_amsl"]

    # Package all data into the Waypoint NamedTuple to be exported
    target_data: Waypoint = {
        target["latitude"],
        target["longitude"],
        target["altitude"]
    }
    return target_data, ground_altitude


# If run on its own, use the default data location
if __name__ == "__main__":
    # Read file to be used as the data file using the -file argument
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-file")
    args: argparse.Namespace = parser.parse_args()

    extract_gps(vars(args)["file"])