from util.enum import Enum
from util.plain_data import PlainData


class DeviceId(Enum):
    FLkey37 = 0
    FLkeyMini = 1
    LaunchkeyMini = 2
    Launchkey = 3
    Launchkey88 = 4


class ValidationState(Enum):
    Idle = 0
    InProgress = 1
    Success = 2
    Failure = 3


class Pads(Enum):
    Num = 16


class Pots(Enum):
    FirstControlIndex = 0
    Num = 8


class Faders(Enum):
    FirstControlIndex = 100
    NumRegularFaders = 8
    MasterFaderIndex = 8
    Num = 9


class ChannelNavigationSteps(Enum):
    Bank = 8


class ChannelNavigationMode(Enum):
    Single = 0
    Bank = 1


class Notes(Enum):
    Default = 60
    Min = 0
    Max = 127


class HighlightDuration(Enum):
    WithoutEnd = -1
    Default = 3000


class ButtonFunction(Enum):
    Quantise = 0
    Undo = 1
    Redo = 2
    DumpScoreLog = 3


class LedLightingType(Enum):
    Static = 0
    Pulsing = 1


class SelectedSequencerStepState:
    def __init__(self, *, edited=False, toggled=False):
        self.edited = edited
        self.toggled = toggled


class SequencerStepEditGroup:
    def __init__(self):
        self.edited = False
        self._steps = []
        self.displayed_step_edit_parameter = StepEditParameters.Velocity.value.index

    def get_steps(self):
        return self._steps

    def add_step(self, step):
        self._steps.append(step)

    def remove_step(self, step):
        self._steps.remove(step)
        if len(self._steps) == 0:
            self.edited = False

    def remove_all_steps(self):
        self._steps.clear()
        self.edited = False


class SequencerStepEditState(Enum):
    EditIdle = 0
    EditWaiting = 1
    EditQuick = 2
    EditLatch = 3


class PluginPotParameterType(Enum):
    Plugin = 0
    Channel = 1


class StepEditParameters(Enum):
    @PlainData
    class Parameter:
        index: int
        min: int
        max: int
        is_bipolar: bool

    Pitch = Parameter(index=0, min=30, max=90, is_bipolar=False)
    Velocity = Parameter(index=1, min=0, max=128, is_bipolar=False)
    Release = Parameter(index=2, min=0, max=128, is_bipolar=False)
    PitchFine = Parameter(index=3, min=0, max=240, is_bipolar=True)
    Pan = Parameter(index=4, min=0, max=128, is_bipolar=True)
    ModX = Parameter(index=5, min=0, max=255, is_bipolar=True)
    ModY = Parameter(index=6, min=0, max=255, is_bipolar=True)
    Shift = Parameter(index=7, min=0, max=22, is_bipolar=False)


class SysEx(Enum):
    MessageHeader = [0x00, 0x20, 0x29, 0x02]
    DeviceEnquiryRequest = [0x7E, 0x7F, 0x06, 0x01]
    DeviceEnquiryResponseHeader = [0x7E, 0x00, 0x06, 0x02, 0x00, 0x20, 0x29]


PluginsWithExplicitlyDisabledPresetNavigation = {
    "Slicex"
}

Scales = {
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'major': [0, 2, 4, 5, 7, 9, 11],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
    'minor_pentatonic': [0, 3, 5, 7, 10],
    'major_pentatonic': [0, 2, 4, 7, 9],
}
