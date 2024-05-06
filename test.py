# import asyncio
from machine import Pin
from rotary_irq_rp2 import RotaryIRQ
from oled import showTime, fillDisplay
from primitives import Pushbutton, delay_ms
from buzzer_music import music
from utime import sleep, sleep_ms, ticks_ms, ticks_diff
import lowpower
import asyncio


# Initiating encoder
r = RotaryIRQ(
    pin_num_clk=3,
    pin_num_dt=2,
    min_val=0,
    max_val=5999,  # Adjust max value if needed
    reverse=True,  # Adjust if rotation direction needs swapping
    half_step=True,
    pull_up=True,
    incr=5,  # Adjust increment value per encoder step
    range_mode=RotaryIRQ.RANGE_BOUNDED,
)


# Global variables
alarm_trg = False
btn_state = [0, 0, 0, 0]
last_time = 0


def buttonMonitor(pin):
    """Updates the button state history based on button press events."""
    global btn_state, last_time
    new_time = utime.ticks_ms()
    if (new_time - last_time) > 50:
        btn_state = [1, 1, 0, 0]
        last_time = new_time


# Initiate button
btn_pin = Pin(7, Pin.IN, Pin.PULL_UP)
# Initiate button interrupt
btn_pin.irq(handler=buttonMonitor, trigger=Pin.IRQ_FALLING)

# Assign functions to button events
# btn.press_func(buttonMonitor, (1, 0))
# btn.release_func(buttonMonitor, (1, 1))
# btn.double_func(buttonMonitor, (1, 2))
# btn.long_func(buttonMonitor, (1, 3))


def go_to_sleep():
    global btn_state
    fillDisplay(0)
    print("Natti", sleep_timer.rvalue())
    lowpower.dormant_until_pin(7)
    sleep_ms(20)
    btn_state = [0, 0, 0, 0]


sleep_timer = delay_ms.Delay_ms(go_to_sleep, duration=10000)


def soundAlarm():
    """Plays a predefined song using the "music" function"""
    song = "0 F5 1 34;1 C6 1 34;2 C6 1 34;2 E6 1 34;3 F6 1 34;4 C7 1 34;6 A6 1 34;7 E7 2 34"
    mySong = music(song, pins=[Pin(5, Pin.OUT, Pin.PULL_UP)], looping=False)
    while mySong.tick():
        mySong.tick()
        sleep_ms(30)


def setTime(current_value=0):
    """Listens for encoder changes and prints the current value."""
    global alarm_trg
    if current_value > 0 and not alarm_trg:
        r.set(value=current_value)
    alarm_trg = False
    
    global btn_state
    btn_state = [0, 0, 0, 0]
    sleep_timer = ticks_ms()
    while btn_state != [1, 1, 0, 0]:
        # Check for encoder changes
        new_value = r.value()
        if new_value > current_value:  # Increase
            current_value = new_value
            current_value -= current_value % 5
            print("Current time:", current_value)
            sleep_timer = ticks_ms()

        elif new_value < current_value:  # Decrease
            current_value = new_value
            current_value = (current_value + 4) // 5 * 5
            print("Current time:", current_value)
            sleep_timer = ticks_ms()

        if r.value() != current_value:
            r.set(value=current_value)

        if btn_state == [1, 0, 0, 1]:
            r.reset()
            print("Reset time")
            btn_state = [0, 0, 0, 0]
            
        if ticks_diff(ticks_ms(), sleep_timer) > 10000:
            go_to_sleep()
            sleep_timer = ticks.ms()

        showTime(current_value)
        sleep_ms(50)
    sleep_timer.stop()
    return current_value


def countDown(set_time):
    """Counts down from a given time (t) with a 1-second delay between each step.
    Displays the current time using the provided showTime function."""
    global btn_state
    btn_state = [0, 0, 0, 0]
    t = set_time
    while t >= 0 and btn_state == [0, 0, 0, 0]:
        showTime(t)
        sleep_ms(1000)
        t -= 1
    return t


def alarm():
    global button_list
    button_list = [0, 0, 0, 0]
    while btn_state == [0, 0, 0, 0]:
        print("Alarm")
        showTime(0)
        soundAlarm()
        sleep_ms(500)
        fillDisplay(0)
        sleep_ms(500)
    return True


def main():
    global alarm_trg
    set_time = 0
    showTime(5999)
    print("Starting hej")
    sleep(10)
    r.set(0)
    print("Starting")
    while True:
        set_time = setTime(set_time)
        set_time = countDown(set_time)
        if set_time <= 0:
            alarm_trg = alarm()



# Run the event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
