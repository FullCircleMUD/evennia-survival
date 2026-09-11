"""
Server startstop hooks

This module contains functions called by Evennia at various points during
its startup, reload and shutdown sequence.

The two survival clocks are started here rather than in an AppConfig, since
`ready()` also runs during `evennia migrate` and management commands where a
clock should not be spinning up.
"""

from evennia_survival.services import (
    start_regeneration_clock,
    start_survival_clock,
    stop_regeneration_clock,
    stop_survival_clock,
)


def at_server_init():
    """Called first, before any other hook, on server start/reload/reset."""


def at_server_start():
    """Called every time the server starts up, including reloads."""
    start_survival_clock()
    start_regeneration_clock()


def at_server_stop():
    """Called at the end of a shutdown, reload or reset."""
    stop_survival_clock()
    stop_regeneration_clock()


def at_server_reload_start():
    pass


def at_server_reload_stop():
    pass


def at_server_cold_start():
    pass


def at_server_cold_stop():
    pass
