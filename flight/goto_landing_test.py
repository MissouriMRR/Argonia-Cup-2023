"""
A flight path going to four different waypoints near the golf course to test the goto function.
"""

import asyncio

from mavsdk import System
from goto import move_to
from Landing import landing

# Home coordinates
# PX4_HOME_LAT=37.9490953
# PX4_HOME_LON=-91.7848293

waypoints = [
    [37.949803, -91.784440, 75],
    [37.949576, -91.783739, 75],
    [37.949098, -91.783825, 75],
    [37.949297, -91.784501, 75],
]


async def run() -> None:
    """
    Tests the goto function by moving the drone to four different waypoints.
    """
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Using move_to() to move to waypoints")
    await move_to(drone, waypoints[0][0], waypoints[0][1], waypoints[0][2])
    await move_to(drone, waypoints[1][0], waypoints[1][1], waypoints[1][2])
    await move_to(drone, waypoints[2][0], waypoints[2][1], waypoints[2][2])
    await move_to(drone, waypoints[3][0], waypoints[3][1], waypoints[3][2])

    print("-- Using manual_land() to land the drone precisely on the waypoint")
    await landing.manual_land(drone, waypoints[3][0], waypoints[3][1])


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
