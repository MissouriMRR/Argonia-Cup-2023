"""Logging configuration and functions"""
import logging
from typing import TextIO
from datetime import datetime
from multiprocessing import Queue
from logging import Formatter, FileHandler, StreamHandler
from logging.handlers import QueueHandler, QueueListener

LOG_FILE: str = f"logs/{datetime.now()}.log"
LOG_FORMAT: str = "%(levelname)s | %(asctime)s @  %(processName)s:%(funcName)s > %(message)s"
LOG_LEVEL = logging.DEBUG


def init_logger(queue: Queue[str]) -> QueueListener:
    """
    Creates a QueueListener that will process all log messages throughout the application

    Parameters
    ----------
    queue: Queue[str]
        Queue object that holds logging processes

    Returns
    -------
    queuelistener: QueueListener
        Object to process log messages
    """
    console_formatter: Formatter = logging.Formatter(LOG_FORMAT)
    file_formatter: Formatter = logging.Formatter(LOG_FORMAT)

    file: FileHandler = logging.FileHandler(LOG_FILE, "a")
    file.setFormatter(file_formatter)

    console: StreamHandler[TextIO] = logging.StreamHandler()
    console.setFormatter(console_formatter)

    return QueueListener(queue, file, console)


def worker_configurer(queue: Queue[str]) -> None:
    """
    It configures the logger of this process to submit logs to the logging process (QueueListener)

    Parameters
    ----------
    queue: Queue[str]
        Queue object that holds logging processes
    """
    queue_handler: QueueHandler = QueueHandler(queue)  # Just the one handler needed
    root: logging.Logger = logging.getLogger()
    root.addHandler(queue_handler)
    root.setLevel(LOG_LEVEL)
