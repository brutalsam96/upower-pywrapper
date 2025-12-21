from typing import Optional, Any
from dbus_next.aio.message_bus import MessageBus
from dbus_next.constants import BusType
from dbus_next.errors import InterfaceNotFoundError


class UPowerWrapper:
    # constants for better readability
    UPOWER_PATH = "/org/freedesktop/UPower"
    UPOWER_MANAGER_IFACE = "org.freedesktop.UPower"
    UPOWER_DEVICE_IFACE = "org.freedesktop.UPower.Device"

    # for Wakeups(needs testing)
    WAKEUPS_PATH = "/org/freedesktop/UPower/Wakeups"
    IFACE_WAKEUPS = "org.freedesktop.UPower.Wakeups"

    # Mapping UPower State integers to readable strings
    # Ref: https://upower.freedesktop.org/docs/Device.html
    STATE_MAP = {
        0: "Unknown",
        1: "Charging",
        2: "Discharging",
        3: "Empty",
        4: "Fully Charged",
        5: "Pending Charge",
        6: "Pending Discharge",
    }

    def __init__(self) -> None:
        self.bus: Optional[MessageBus] = None

    async def connect(self):
        """Connect to System Bus"""
        self.bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    async def _get_interface(self, path, iface_name):
        """
        Helper function to introspect and return specific interface,
        Raises exception if interface is not found or path is invalid.
        """
        if self.bus is None:
            raise RuntimeError("Bus is not connected")

        introspect = await self.bus.introspect(self.UPOWER_MANAGER_IFACE, path)
        proxy = self.bus.get_proxy_object(self.UPOWER_MANAGER_IFACE, path, introspect)
        return proxy.get_interface(iface_name)

    async def _get_wakeups_interface(self):
        """
        GRACEFUL Helper: Specifically for Wakeups.
        Returns None if missing instead of raising an exception.
        """
        try:
            return await self._get_interface(self.WAKEUPS_PATH, self.IFACE_WAKEUPS)
        except (InterfaceNotFoundError, Exception):
            return None

    async def get_devices(self):
        """Enumerate all power devices and fetch their details"""
        interface: Any = await self._get_interface(
            self.UPOWER_PATH, self.UPOWER_MANAGER_IFACE
        )

        device_paths = await interface.call_enumerate_devices()
        return device_paths

    async def get_display_device(self):
        """Fetch display device"""
        interface: Any = await self._get_interface(
            self.UPOWER_PATH, self.UPOWER_MANAGER_IFACE
        )

        display_dev = await interface.call_get_display_device()
        return display_dev

    async def get_critical_action(self):
        """TBA"""
        interface: Any = await self._get_interface(
            self.UPOWER_PATH, self.UPOWER_MANAGER_IFACE
        )

        crit_action = await interface.call_get_critical_action()
        return crit_action

    async def get_manager_status(self):
        """Fetch global power manager status."""
        interface: Any = await self._get_interface(
            self.UPOWER_PATH, self.UPOWER_MANAGER_IFACE
        )

        on_battery = await interface.get_on_battery()
        lid_closed = await interface.get_lid_is_closed()
        daemon_ver = await interface.get_daemon_version()
        lid_present = await interface.get_lid_is_present()

        return {
            "on_battery": on_battery,
            "lid_closed": lid_closed,
            "daemon_ver": daemon_ver,
            "lid_present": lid_present,
        }

    async def get_device_percentage(self, obj):
        """Returns device remaining battery percentage"""
        interface: Any = await self._get_interface(obj, self.UPOWER_DEVICE_IFACE)
        return await interface.get_percentage()

    async def is_lid_present(self):
        """Check if lid is present"""
        interface: Any = await self._get_interface(
            self.UPOWER_PATH, self.UPOWER_MANAGER_IFACE
        )
        return bool(await interface.get_lid_is_present())

    async def is_lid_closed(self):
        """Check if lid is closed"""
        interface: Any = await self._get_interface(
            self.UPOWER_PATH, self.UPOWER_MANAGER_IFACE
        )
        return bool(await interface.get_lid_is_closed())

    async def on_battery(self):
        """Check if device is on battery"""
        interface: Any = await self._get_interface(
            self.UPOWER_PATH, self.UPOWER_MANAGER_IFACE
        )
        return bool(await interface.get_on_battery())

    async def has_wakeup_capabilities(self):
        """TBA"""
        interface: Any = await self._get_wakeups_interface()
        return await interface.get_has_capability() if interface else False

    async def get_wakeup_data(self):
        """TBA"""
        interface: Any = await self._get_wakeups_interface()
        return await interface.call_get_data() if interface else []

    async def get_wakeup_total(self):
        """TBA"""
        interface: Any = await self._get_wakeups_interface()
        return await interface.call_get_total() if interface else 0

    async def is_charging(self, obj):
        """Check if battery is charging"""
        interface: Any = await self._get_interface(obj, self.UPOWER_DEVICE_IFACE)
        if interface:
            state = await interface.get_state()
            return state == 1
        return False

    async def get_device_state(self, obj):
        """Returns battery state"""
        interface: Any = await self._get_interface(obj, self.UPOWER_DEVICE_IFACE)
        state = int(await interface.get_state())
        return self.STATE_MAP[state]

    async def get_full_device_information(self, obj):
        """Returns full device information as dict, takes in object path as string"""

        device_interface: Any = await self._get_interface(obj, self.UPOWER_DEVICE_IFACE)

        # Boolean Properties
        hasHistory = await device_interface.get_has_history()
        hasStatistics = await device_interface.get_has_statistics()
        isPresent = await device_interface.get_is_present()
        isRechargable = await device_interface.get_is_rechargeable()
        online = await device_interface.get_online()
        powersupply = await device_interface.get_power_supply()

        # Energy/Charge Properties
        capacity = await device_interface.get_capacity()
        energy = await device_interface.get_energy()
        energyempty = await device_interface.get_energy_empty()
        energyfull = await device_interface.get_energy_full()
        energyfulldesign = await device_interface.get_energy_full_design()
        energyrate = await device_interface.get_energy_rate()

        # Other Properties
        luminosity = await device_interface.get_luminosity()
        percentage = await device_interface.get_percentage()
        temperature = await device_interface.get_temperature()
        voltage = await device_interface.get_voltage()
        timetoempty = await device_interface.get_time_to_empty()
        timetofull = await device_interface.get_time_to_full()
        updatetime = await device_interface.get_update_time()

        # Identifier Properties
        iconname = await device_interface.get_icon_name()
        model = await device_interface.get_model()
        nativepath = await device_interface.get_native_path()
        serial = await device_interface.get_serial()
        vendor = await device_interface.get_vendor()

        # State/Enum Properties
        state = await device_interface.get_state()
        technology = await device_interface.get_technology()
        battype = await device_interface.get_type()
        warninglevel = await device_interface.get_warning_level()

        information_table = {
            "HasHistory": hasHistory,
            "HasStatistics": hasStatistics,
            "IsPresent": isPresent,
            "IsRechargeable": isRechargable,
            "Online": online,
            "PowerSupply": powersupply,
            "Capacity": capacity,
            "Energy": energy,
            "EnergyEmpty": energyempty,
            "EnergyFull": energyfull,
            "EnergyFullDesign": energyfulldesign,
            "EnergyRate": energyrate,
            "Luminosity": luminosity,
            "Percentage": percentage,
            "Temperature": temperature,
            "Voltage": voltage,
            "TimeToEmpty": timetoempty,
            "TimeToFull": timetofull,
            "IconName": iconname,
            "Model": model,
            "NativePath": nativepath,
            "Serial": serial,
            "Vendor": vendor,
            "State": state,
            "Technology": technology,
            "Type": battype,
            "WarningLevel": warninglevel,
            "UpdateTime": updatetime,
        }

        return information_table
