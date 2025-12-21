# upower-pywrapper

A UPower DBus wrapper using Dbus-next inspired by [wogscpar](https://github.com/wogscpar)'s upower-python.

## Functions

### Core
*   **`connect()`**: Connect to the System Bus. This is required before calling other methods.

### Manager
*   **`get_devices()`**: Enumerate all power devices and fetch their object paths.
*   **`get_display_device()`**: Fetch the object path of the composite display device.
*   **`get_critical_action()`**: Get the configured critical action for the system.
*   **`get_manager_status()`**: Fetch global power manager status, including:
    *   `on_battery`: Boolean indicating if running on battery.
    *   `lid_closed`: Boolean indicating if lid is closed.
    *   `daemon_ver`: The UPower daemon version.
    *   `lid_present`: Boolean indicating if a lid is present.
*   **`is_lid_present()`**: Check if the system has a lid.
*   **`is_lid_closed()`**: Check if the lid is closed.
*   **`on_battery()`**: Check if the device is currently running on battery power.

### Wakeups
*   **`has_wakeup_capabilities()`**: Check if the system supports wakeup capabilities.
*   **`get_wakeup_data()`**: Get data regarding system wakeups.
*   **`get_wakeup_total()`**: Get the total number of wakeups.

### Device
These methods typically require a device object path (string) as an argument.

*   **`get_device_percentage(obj)`**: Returns the remaining battery percentage for the specified device.
*   **`is_charging(obj)`**: Check if the specified device is currently charging.
*   **`get_full_device_information(obj)`**: Returns a comprehensive dictionary of device information (e.g., Capacity, Energy, Model, Vendor, Voltage, etc.).
*   **`get_device_state(obj)`**: Returns the readable state string of the device (e.g., "Charging", "Discharging", "Full").

## Example

#### Quick example on how to fetch remaining battery percentage:

```python
import asyncio
from upower_api import UPowerWrapper


async def main():
    mybus = UPowerWrapper()
    await mybus.connect()

    disp_device = await mybus.get_display_device()
    percentage = await mybus.get_device_percentage(disp_device)
    print(percentage)

if __name__ == "__main__":
    asyncio.run(main())

```
