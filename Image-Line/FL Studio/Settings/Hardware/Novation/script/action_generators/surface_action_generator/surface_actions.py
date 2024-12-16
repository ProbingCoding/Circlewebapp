from util.plain_data import PlainData
from util.enum import Enum


@PlainData
class PadLayoutChangedAction:
    layout: Enum


@PlainData
class ControlChangedAction:
    control: int
    position: float


@PlainData
class PotLayoutChangedAction:
    layout: Enum


@PlainData
class FaderLayoutChangedAction:
    layout: Enum


@PlainData
class PadPressAction:
    pad: int
    velocity: int


@PlainData
class PadReleaseAction:
    pad: int


@PlainData
class ButtonPressedAction:
    button: Enum


@PlainData
class ButtonReleasedAction:
    button: Enum


@PlainData
class ScaleEnabledAction:
    pass


@PlainData
class ScaleDisabledAction:
    pass


@PlainData
class ScaleTypeChangedAction:
    scale_index: int


@PlainData
class ScaleRootChangedAction:
    scale_root: int
