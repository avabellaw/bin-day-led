import time
import ntptime
import network
from machine import Pin, lightsleep

from env import variables

sta_if = network.WLAN(network.STA_IF)

LED = Pin(0, Pin.OUT)
BUILTIN_LED = Pin(2, Pin.OUT)

# Turn on the built-in LED to indicate the device is running (inverted for built-in LED)
BUILTIN_LED.value(0)

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
bin_day_time = 11  # 11:00
notify_offset_hours = 20  # Number of hours before bin day to notify


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


def get_time():
    """Returns array containing current [hour, minutes, seconds]."""
    l_time = time.localtime()
    hour = l_time[3]
    minutes = l_time[4]
    secs = l_time[5]

    return [hour, minutes, secs]


def is_bin_day():
    """Returns True if it is within the bin day notification offset."""
    hours_until_bin_day = get_seconds_until_next_bin_day() / 60 / 60

    return hours_until_bin_day <= notify_offset_hours


def get_seconds_until_next_bin_day():
    """Calculates the seconds until bin day using the current time and day in the week."""

    # Get the current time
    h, m, s = get_time()

    # Calculate the number of whole days until bin day
    days_until_bin_day = (bin_day - get_day()) % 7

    # Minus the current time from the bin day time and add the number of days
    hours_until_bin_day = (bin_day_time
                           - h
                           - m / 60
                           - s / 60 / 60)
    + (days_until_bin_day * 24)

    # If value is negative, add 7 days to it
    hours_until_bin_day %= 7 * 24

    return round(hours_until_bin_day * 60 * 60)  # Convert to seconds


def main():
    """
        Main function that checks whether it is bin day.
        If it is within the notification period, it flashes the LED every 2.5s.
    """
    BUILTIN_LED.value(1)  # Turn off buiult-in LED (inverted for built-in LED)

    while True:
        while is_bin_day():
            LED.value(1)  # Turn on the LED
            time.sleep(0.5)
            LED.value(0)
            lightsleep(2500)  # Sleep for 2.5 seconds

        # Sleep until the next bin day (ms)
        lightsleep(get_seconds_until_next_bin_day() * 1000)


connect_to_wifi(variables['SSID'], variables['PASS'])
ntptime.settime()
sta_if.active(False)  # Disable WiFi to save power
main()
