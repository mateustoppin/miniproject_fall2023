"""
Response time - single-threaded
"""

from machine import Pin
import time
import random
import json
import os
import sys

# ======================================================================================

is_micropython = sys.implementation.name == "micropython"

if not is_micropython:
    import os.path

def get_params(param_file: str) -> tuple[int, int, float, float]:
    """Reads parameters from a JSON file."""

    if not is_regular_file(param_file):
        raise OSError(f"File {param_file} not found")

    with open(param_file) as f:
        params = json.load(f)

    return params["loop_count1"], params["loop_count2"], params["sample_time"], params["on_time"]


def is_regular_file(path: str) -> bool:
    """Checks if a regular file exists."""

    if not is_micropython:
        return os.path.isfile(path)

    S_IFREG = 0x8000

    try:
        return os.stat(path)[0] & S_IFREG != 0
    except OSError:
        return False

# ======================================================================================


P1: int = 10
P2: int = 0
sample_ms = 10.0
on_ms = 500


def random_time_interval(tmin: float, tmax: float) -> float:
    """return a random time interval between max and min"""
    return random.uniform(tmin, tmax)


def blinker(N: int, led: Pin) -> None:
    # %% let user know game started / is over

    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)


def write_json(json_filename: str, data: dict) -> None:
    """Writes data to a JSON file.

    Parameters
    ----------

    json_filename: str
        The name of the file to write to. This will overwrite any existing file.

    data: dict
        Dictionary data to write to the file.
    """

    with open(json_filename, "w") as f:
        json.dump(data, f)


def scorer(t: list[int | None]) -> None:
    # %% collate results
    misses = t.count(None)
    print(f"You missed the light {misses} / {len(t)} times")

    t_good = [x for x in t if x is not None]

    print(t_good)
    
    avg_show= sum(t_good)/len(t_good);
    min_show= min(t_good);
    max_show= max(t_good);

    print(f"The average response time {avg_show}")
    print(f"The minimum response time {min_show}")
    print(f"The maximum response time {max_show}")
    print(f"Number of misses v. Total light flashes: {misses} v. {P1+P2}")

    # add key, value to this dict to store the minimum, maximum, average response time
    # and score (non-misses / total flashes) i.e. the score a floating point number
    # is in range [0..1]
    data = f"""You missed the light {misses} / {P1+P2} times 
     The average response time is {avg_show} 
     The minimum response time is {min_show} 
     The maximum response time is {max_show} 
     {misses} v. {P1+P2}"""

    # %% make dynamic filename and write JSON

    now: tuple[int] = time.localtime()

    now_str = "-".join(map(str, now[:3])) + "T" + "_".join(map(str, now[3:6]))
    filename = f"proj1-{now_str}.json"

    print("write", filename)

    write_json(filename, data)


if __name__ == "__main__":
    # using "if __name__" allows us to reuse functions in other script files

    led = Pin("LED", Pin.OUT)
    button1 = Pin(16, Pin.IN, Pin.PULL_UP)
    button2 = Pin(20, Pin.IN, Pin.PULL_UP)
    
    P1, P2, sample_ms, on_ms = get_params("project01.json")

    t: list[int | None] = []

    blinker(3, led)

    for i in range(P1):
        time.sleep(random_time_interval(0.5, 5.0))

        led.high()

        tic = time.ticks_ms()
        t0 = None
        while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
            if button1.value() == 0:
                t0 = time.ticks_diff(time.ticks_ms(), tic)
                led.low()
                break
        t.append(t0)

        led.low()
        
    blinker(3, led)
        
    for i in range(P2):
        time.sleep(random_time_interval(0.5, 5.0))

        led.high()

        tic = time.ticks_ms()
        t0 = None
        while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
            if button2.value() == 0:
                t0 = time.ticks_diff(time.ticks_ms(), tic)
                led.low()
                break
        t.append(t0)

        led.low()

    blinker(5, led)

    scorer(t)

