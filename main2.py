import asyncio
from machine import Pin
from rotary_irq_rp2 import RotaryIRQ
from oled import showTime, fillDisplay
from primitives import Pushbutton, delay_ms
from buzzer_music import music
from time import sleep
import lowpower


# Initiating encoder
r = RotaryIRQ(
    pin_num_clk=3,
    pin_num_dt=4,
    min_val=0,
    max_val=5999,  # Adjust max value if needed
    reverse=True,  # Adjust if rotation direction needs swapping
    half_step=True,
    pull_up=True,
    incr=5,  # Adjust increment value per encoder step
    range_mode=RotaryIRQ.RANGE_BOUNDED,
)

# Initiate button (using Pushbutton library)
btn_pin = Pin(7, Pin.IN, Pin.PULL_UP)
btn = Pushbutton(btn_pin, suppress=True)

# Global variables
global btn_state
global alarm_trg
btn_state = [0, 0, 0, 0]


async def buttonMonitor(new_value, index):
    """Updates the button state history based on button press events."""
    global btn_state
    btn_state[index] = new_value


# Assign functions to button events
btn.press_func(buttonMonitor, (1, 0))
btn.release_func(buttonMonitor, (1, 1))
btn.double_func(buttonMonitor, (1, 2))
btn.long_func(buttonMonitor, (1, 3))


async def go_to_sleep():
    global btn_state
    sleep_timer.stop()
    fillDisplay(0)
    print("Natti", sleep_timer.rvalue())
    lowpower.dormant_until_pin(7)
    await asyncio.sleep_ms(20)
    btn_state = [0, 0, 0, 0]
    sleep_timer.trigger()


sleep_timer = delay_ms.Delay_ms(go_to_sleep, duration=10000)


async def soundAlarm():
    """Plays a predefined song using the "music" function"""
    song = "0 F5 1 34;1 C6 1 34;2 C6 1 34;2 E6 1 34;3 F6 1 34;4 C7 1 34;6 A6 1 34;7 E7 2 34"
    mySong = music(song, pins=[Pin(5, Pin.OUT, Pin.PULL_UP)], looping=False)
    while mySong.tick():
        mySong.tick()
        await asyncio.sleep_ms(30)


async def setTime(current_value=0):
    """Listens for encoder changes and prints the current value."""
    global alarm_trg
    if current_value > 0 and not alarm_trg:
        r.set(value=current_value)
    alarm_trg = False
    global btn_state
    btn_state = [0, 0, 0, 0]
    sleep_timer.trigger()
    while btn_state != [1, 1, 0, 0]:
        # Check for encoder changes
        new_value = r.value()
        if new_value > current_value:  # Increase
            current_value = new_value
            current_value -= current_value % 5
            print("Current time:", current_value)
            sleep_timer.trigger()

        elif new_value < current_value:  # Decrease
            current_value = new_value
            current_value = (current_value + 4) // 5 * 5
            print("Current time:", current_value)
            sleep_timer.trigger()

        if r.value() != current_value:
            r.set(value=current_value)

        if btn_state == [1, 0, 0, 1]:
            r.reset()
            print("Reset time")
            btn_state = [0, 0, 0, 0]

        showTime(current_value)
        await asyncio.sleep_ms(50)
    sleep_timer.stop()
    return current_value


async def countDown(set_time):
    """Counts down from a given time (t) with a 1-second delay between each step.
    Displays the current time using the provided showTime function."""
    global btn_state
    btn_state = [0, 0, 0, 0]
    t = set_time
    while t >= 0 and btn_state == [0, 0, 0, 0]:
        showTime(t)
        await asyncio.sleep_ms(1000)
        t -= 1
    return t


async def alarm():
    global button_list
    button_list = [0, 0, 0, 0]
    alarm_time = 0
    while btn_state == [0, 0, 0, 0] and alarm_time <= 10:
        print("Alarm")
        showTime(0)
        await soundAlarm()
        await asyncio.sleep_ms(500)
        fillDisplay(0)
        await asyncio.sleep_ms(500)
        alarm_time += 1
    return True


async def main():
    global alarm_trg
    alarm_trg = False
    set_time = 0
    showTime(5999)
    print("Starting hej")
    sleep(10)
    r.set(0)
    print("Starting")
    while True:
        task1 = asyncio.create_task(setTime(set_time))
        set_time = await task1  # type: ignore
        task2 = asyncio.create_task(countDown(set_time))
        set_time = await task2  # type: ignore
        if set_time <= 0:
            task3 = asyncio.create_task(alarm())
            alarm_trg = await task3  # type: ignore


# Run the event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
