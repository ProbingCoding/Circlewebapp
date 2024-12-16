from script.constants import Pots
from util.enum import Enum

__all__ = ['FLkey37ProductDefs']


class PadLayout(Enum):
    ChannelRack = 2
    Instrument = 9
    Sequencer = 11
    ScaleChord = 3
    UserChord = 4
    Custom = 5


class PotLayout(Enum):
    MixerVolume = 1
    Plugin = 2
    MixerPan = 3
    ChannelVolume = 4
    ChannelPan = 5

    Momentary = 10
    Revert = 127


class Constants(Enum):
    NovationProductId = 0x11

    LightingTargetNote = 0x40
    LightingTargetCC = 0x50
    LightingTypeStatic = 0x00
    LightingTypePulsing = 0x02
    LightingTypeRGB = 0x03

    Scales = {0: 'minor', 1: 'major', 2: 'dorian', 3: 'mixolydian', 4: 'phrygian',
              5: 'harmonic_minor', 6: 'minor_pentatonic', 7: 'major_pentatonic'}
    NotesForPadLayout = {
        PadLayout.ChannelRack: [96, 97, 98, 99, 100, 101, 102, 103,
                                112, 113, 114, 115, 116, 117, 118, 119],
        PadLayout.Instrument: [64, 65, 66, 67, 68, 69, 70, 71,
                               80, 81, 82, 83, 84, 85, 86, 87],
        PadLayout.Sequencer: [32, 33, 34, 35, 36, 37, 38, 39,
                              48, 49, 50, 51, 52, 53, 54, 55],
    }
    PadForLayoutNote = {**{note: pad for pad, note in enumerate(NotesForPadLayout[PadLayout.ChannelRack])},
                        **{note: pad for pad, note in enumerate(NotesForPadLayout[PadLayout.Instrument])},
                        **{note: pad for pad, note in enumerate(NotesForPadLayout[PadLayout.Sequencer])}}


class Button(Enum):
    Shift = 0
    MixerRight = 1
    MixerLeft = 2
    ChannelRackUp = 3
    ChannelRackDown = 4
    PresetUp = 5
    PresetDown = 6
    PageLeft = 7
    PageRight = 8
    TransportPlay = 9
    TransportStop = 10
    TransportRecord = 11
    ScoreLog = 12
    Quantise = 13
    Metronome = 14
    Undo = 15
    Redo = 16
    TapTempo = 17


class SurfaceEvent(Enum):
    EnterDawMode = 0x9F, 0x0C, 0x7F
    ExitDawMode = 0x9F, 0x0C, 0x00
    QueryScaleModeEnabled = 0xBF, 0x2E, 0x00
    QueryScaleType = 0xBF, 0x2F, 0x00
    QueryScaleRoot = 0xBF, 0x30, 0x00
    ScaleModeEnabled = 0xBF, 0x0E
    ScaleTypeChanged = 0xBF, 0x0F
    ScaleRootChanged = 0xBF, 0x10
    PadLayout = 0xBF, 0x03
    PotLayout = 0xBF, 0x09
    PotFirst = 0xBF, 0x15
    PotLast = 0xBF, 0x22
    ButtonMixerRight = 0xBF, 0x33
    ButtonMixerLeft = 0xBF, 0x34
    ButtonTransportPlay = 0xBF, 0x73
    ButtonTransportStop = 0xBF, 0x74
    ButtonTransportRecord = 0xBF, 0x75
    ButtonScoreLog = 0xBF, 0x76
    ButtonChannelRackUp = 0xB0, 0x68
    ButtonChannelRackDown = 0xB0, 0x69
    ButtonPresetUp = 0xBF, 0x6A
    ButtonPresetDown = 0xBF, 0x6B
    ButtonPageLeft = 0xBF, 0x67
    ButtonPageRight = 0xBF, 0x66
    ButtonShift = 0xB0, 0x6C
    ButtonQuantise = 0xBF, 0x4A
    ButtonMetronome = 0xBF, 0x4B
    ButtonUndo = 0xBF, 0x4C
    ButtonRedo = 0xBF, 0x4D
    ButtonTapTempo = 0xBF, 0x41


FunctionToButton = {
    "ExitStepEditLatchMode": Button.ChannelRackDown,
    "ChannelPluginPageLeft": Button.PageLeft,
    "ChannelPluginPageRight": Button.PageRight,
    "ChannelPluginOctaveDown": Button.PageLeft,
    "ChannelPluginOctaveUp": Button.PageRight,
    "SequencerStepsPageLeft": Button.PageLeft,
    "SequencerStepsPageRight": Button.PageRight,
    "MixerBankRight": Button.MixerRight,
    "MixerBankLeft": Button.MixerLeft,
    "SelectPreviousChannel": Button.ChannelRackUp,
    "SelectNextChannel": Button.ChannelRackDown,
    "SelectPreviousPreset": Button.PresetUp,
    "SelectNextPreset": Button.PresetDown,
    "TransportTogglePlayPause": Button.TransportPlay,
    "TransportStop": Button.TransportStop,
    "TransportToggleRecording": Button.TransportRecord,
    "Quantise": Button.Quantise,
    "ToggleMetronome": Button.Metronome,
    "Undo": Button.Undo,
    "Redo": Button.Redo,
    "DumpScoreLog": Button.ScoreLog,
    "ShowHighlights": Button.Shift,
    "TapTempo": Button.TapTempo
}

ButtonToLedIndex = {
    Button.ChannelRackUp: 0x68,
    Button.ChannelRackDown: 0x69,
    Button.PresetUp: 0x6A,
    Button.PresetDown: 0x6B,
}

PotIndexToControlIndex = {
    index: Pots.FirstControlIndex.value + control for index, control in enumerate(range(0, Pots.Num.value))
}


class FLkey37ProductDefs:

    def __init__(self):
        self.PadLayout = PadLayout
        self.PotLayout = PotLayout
        self.Constants = Constants
        self.Button = Button
        self.SurfaceEvent = SurfaceEvent
        self.FunctionToButton = FunctionToButton
        self.ButtonToLedIndex = ButtonToLedIndex
        self.PotIndexToControlIndex = PotIndexToControlIndex
        self.ControlIndexToPotIndex = {v: k for k, v in self.PotIndexToControlIndex.items()}

    def IsShiftButton(self, button):
        return False

    def ForwardButtonLedGivenShift(self, button, shift_pressed):
        return True
