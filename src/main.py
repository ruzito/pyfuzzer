import curses
import asyncio
import signal
import sys

from entry import loop
from report import render, final_report, stop_generating

_curses_handle = None
_signal_recieved = 0
_application_done = False


def sigint_handler(signum, frame):
    global _signal_recieved
    _signal_recieved += 1
    stop_generating()


def curses_init():
    global _curses_handle
    _curses_handle = (
        curses.initscr()
    )  # Initializes the curses module and returns a window object
    curses.curs_set(0)
    curses.noecho()  # Turn off automatic echoing of keys to the screen
    curses.cbreak()  # React to keys instantly, without requiring the Enter key to be pressed


def curses_finalize():
    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)
    curses.endwin()  # Deinitialize the curses module


async def curses_render():
    if _curses_handle:
        _curses_handle.clear()  # Clear the screen
        render(_curses_handle)
        _curses_handle.refresh()  # Refresh the screen to show changes


async def render_loop():
    global _application_done
    while not _application_done:
        await curses_render()
        await asyncio.sleep(0.25)


async def app_loop():
    global _signal_recieved
    global _application_done
    wait = True
    while (wait or _signal_recieved == 0) and _signal_recieved < 3:
        wait = await loop(_signal_recieved)
    _application_done = True


async def async_main():
    curses_init()
    loop = asyncio.get_event_loop()
    render_task = loop.create_task(render_loop())
    app_task = loop.create_task(app_loop())
    print("await gather", file=sys.stderr)
    await asyncio.gather(render_task, app_task)
    print("curses_finalize", file=sys.stderr)
    curses_finalize()
    print("should be visible")
    final_report()


def main():
    signal.signal(signal.SIGINT, sigint_handler)
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
