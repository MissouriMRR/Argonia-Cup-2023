import typing
import asyncio
from mavsdk import System
import logging
import math

# Implement go_to function with use of rtk data with slow mode off in order to ensure
# that we are as close as possible to the position that the function is given

# Use System.rtk
# http://mavsdk-python-docs.s3-website.eu-central-1.amazonaws.com/plugins/rtk.html

# Find out what format the rtk data needs to be sent in
# send_rtcm_data(rtcm), rtcm should be a string containing the byte array of data that the rtcm
# controller(?) provides.