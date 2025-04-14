import time
import ntptime
import network
from machine import Pin

from env import variables

sta_if = network.WLAN(network.STA_IF)

LED = Pin(0, Pin.OUT)
BUILTIN_LED = Pin(2, Pin.OUT)

BUILTIN_LED.value(0)  # Turn on the built-in LED to indicate the device is running (inverted for built-in LED)

BIN_DAYS = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6,
}

bin_day = BIN_DAYS['Thursday']  # Thursday


def connect_to_wifi(ssid, password):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            print("Connecting to WiFi...")
            time.sleep(1)


def get_day():
    """Returns the day of the week (0-6)"""
    day = time.localtime()[6]
    return day


def get_time_hour():
    """Returns the current hour (0-23)"""
    hour = time.localtime()[3]
    return hour


def is_bin_day():
    """Returns whether it is bin day"""
    return get_day() == bin_day


def get_seconds_until_next_bin_day():
    """Uses the current day in the week and hour to calculate the seconds until 12:00am the day before bin day"""
    current_day = get_day()
    current_hour = get_time_hour()

    # Calculate the number of days until bin day
    days_until_bin_day = (bin_day - current_day) % 7

    # If it's the day before bin day, set the hour to 0
    if days_until_bin_day == 1:
        current_hour = 0

    # Calculate the total minutes until bin day at 12:00am
    total_minutes_until_bin_day = (days_until_bin_day * 24 * 60) - (current_hour * 60)

    return total_minutes_until_bin_day * 60  # Convert to seconds


def main():
    BUILTIN_LED.value(1) # Turn off buiult-in LED (inverted for built-in LED)
    while True:
        if is_bin_day():
            LED.value(1)  # Turn on the LED
            time.sleep(12 * 60 * 60)  # Sleep for 12 hours
            LED.value(0)

        time.sleep(get_seconds_until_next_bin_day())


print("Connecting to wifi...")
connect_to_wifi(variables['SSID'], variables['PASS'])
ntptime.settime()
main()
