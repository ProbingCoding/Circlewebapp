from script.constants import DeviceId
from script.product_defs.flkey37_product_defs import FLkey37ProductDefs
from script.product_defs.flkeymini_product_defs import FLkeyMiniProductDefs
from script.product_defs.launchkey88_product_defs import Launchkey88ProductDefs
from script.product_defs.launchkey_product_defs import LaunchkeyProductDefs
from script.product_defs.launchkeymini_product_defs import LaunchkeyMiniProductDefs

__all__ = [
    'make_product_defs',
]


def make_product_defs(device_id):
    """ Instantiates and returns the relevant implementation of ProductDefs.

            Args:
                device_id: Device for which to return an implementation of ProductDefs.

            Returns:
                Instance of a ProductDefs implementation.
    """
    if device_id == DeviceId.FLkey37:
        return FLkey37ProductDefs()
    elif device_id == DeviceId.FLkeyMini:
        return FLkeyMiniProductDefs()
    elif device_id == DeviceId.LaunchkeyMini:
        return LaunchkeyMiniProductDefs()
    elif device_id == DeviceId.Launchkey:
        return LaunchkeyProductDefs()
    elif device_id == DeviceId.Launchkey88:
        return Launchkey88ProductDefs()
    return
