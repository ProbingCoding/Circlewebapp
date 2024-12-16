from script.constants import DeviceId
from .flkey_device_manager import FLKeyDeviceManager

__all__ = ['make_device_manager']

from .launchkey_device_manager import LaunchkeyDeviceManager


def make_device_manager(device_id, sender, product_defs):
    """ Instantiates and returns the relevant implementation of DeviceManager.

        Args:
            device_id: Device for which to return an implementation of DeviceManager.
            sender: required by DeviceManager instance to control hardware.
            product_defs: required by DeviceManager to send device specific control messages.

        Returns:
            Instance of a DeviceManager implementation.
    """
    if device_id == DeviceId.FLkey37:
        return FLKeyDeviceManager(sender, product_defs)
    if device_id == DeviceId.FLkeyMini:
        return FLKeyDeviceManager(sender, product_defs)
    if device_id == DeviceId.Launchkey or device_id == DeviceId.Launchkey88:
        return LaunchkeyDeviceManager(sender, product_defs)
    return None
