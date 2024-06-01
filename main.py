import uasyncio as asyncio
from machine import Pin
from rotary_irq_rp2 import RotaryIRQ
from primitives import Pushbutton, delay_ms
from buzzer_music import music
from utime import sleep, sleep_ms
import lowpower
from oled import showTime, fillDisplay, invertDisplay, powerDisplay


# Initiating encoder
r = RotaryIRQ(
    pin_num_clk=3,
    pin_num_dt=4,
    min_val=0,
    max_val=5999,  # Adjust max value if needed
    reverse=False,  # Adjust if rotation direction needs swapping
    half_step=True,
    pull_up=True,
    incr=5,  # Adjust increment value per encoder step
    range_mode=RotaryIRQ.RANGE_BOUNDED,
)

# Initiate button (using Pushbutton library)
btn_pin = Pin(7, Pin.IN, Pin.PULL_UP)
btn = Pushbutton(btn_pin, suppress=True)

# Global variables
btn_state = [0, 0, 0, 0]
alarm_trg = False


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
    """Executes when sleep_timer reaches 10s."""
    global btn_state
    sleep_timer.stop()
    powerDisplay(0)
    lowpower.dormant_until_pin(7)
    sleep(1)
    btn_state = [0, 0, 0, 0]
    powerDisplay(1)
    sleep_timer.trigger()
    await asyncio.sleep_ms(0)


sleep_timer = delay_ms.Delay_ms(go_to_sleep, duration=10000)  # Initiating sleep timer


async def soundAlarm():
    """Plays a predefined song using the "music" function."""
    song = "0 F5 1 34;1 C6 1 34;2 C6 1 34;2 E6 1 34;3 F6 1 34;4 C7 1 34;6 A6 1 34;7 E7 2 34"
    mySong = music(song, pins=[Pin(5, Pin.OUT, Pin.PULL_UP)], looping=False)
    while mySong.tick():
        mySong.tick()
        await asyncio.sleep_ms(30)


async def vibrateMotor(turn_on):
    """Turns on vibration motor when True sent to function, send anything else to turn off vibration"""
    motorpin = Pin(28, Pin.OUT, Pin.PULL_UP)
    if turn_on:
        motorpin.high()
    else:
        motorpin.low()


async def setTime(current_value=0):
    """Listens for encoder changes and prints the current value."""
    global alarm_trg
    if current_value > 0 and not alarm_trg:  # Keeps last value if alarm hasn't sounded
        r.set(value=current_value)
    alarm_trg = False

    global btn_state
    btn_state = [0, 0, 0, 0]

    sleep_timer.trigger()  # Starting the timout timer
    await asyncio.sleep_ms(0)

    while btn_state != [1, 1, 0, 0]:
        # Check for encoder changes
        new_value = r.value()
        if new_value > current_value:  # Increase
            current_value = new_value
            current_value -= current_value % 5
            sleep_timer.trigger()

        elif new_value < current_value:  # Decrease
            current_value = new_value
            current_value = (current_value + 4) // 5 * 5
            sleep_timer.trigger()

        if btn_state == [1, 0, 0, 1]:  # Reset when btn held
            r.reset()
            btn_state = [0, 0, 0, 0]

        showTime(current_value)
        await asyncio.sleep_ms(10)
    sleep_timer.stop()
    return current_value


async def countDown(set_time):
    """Counts down from a given time (t) with a 1-second delay between each step.
    Displays the current time using the provided showTime function."""
    global btn_state
    await asyncio.sleep_ms(50)
    btn_state = [0, 0, 0, 0]
    t = set_time
    while t >= 0 and btn_state == [0, 0, 0, 0]:
        showTime(t)
        await asyncio.sleep_ms(1000)
        t -= 1
    return t


async def alarm():
    """Blinks the time and makes a sound."""
    global btn_state
    btn_state = [0, 0, 0, 0]
    alarm_time = 0
    while btn_state == [0, 0, 0, 0] and alarm_time <= 10:
        showTime(0)
        await soundAlarm()
        await vibrateMotor(True)
        invertDisplay(True)
        await asyncio.sleep_ms(500)
        await vibrateMotor(False)
        invertDisplay(False)
        await asyncio.sleep_ms(500)
        alarm_time += 1
    return True


async def main():
    global alarm_trg
    # Short startup screen
    showTime(5999)
    sleep(3)

    # Initiating local variables
    set_time = 0

    while True:  # Main Loop
        set_time = await setTime(set_time)
        set_time = await countDown(set_time)
        if set_time <= 0:
            alarm_trg = await alarm()


# Run the event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
