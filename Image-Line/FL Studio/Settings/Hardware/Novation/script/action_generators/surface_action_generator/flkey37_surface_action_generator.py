from script.action_generators.surface_action_generator.keyboard_controller_common import \
    KeyboardControllerCommonPadActionGenerator, KeyboardControllerCommonPadLayoutActionGenerator, \
    KeyboardControllerCommonPotActionGenerator, KeyboardControllerCommonPotLayoutActionGenerator, \
    KeyboardControllerCommonScaleActionGenerator
from script.action_generators.surface_action_generator.surface_actions import ButtonPressedAction, ButtonReleasedAction


class FLkey37SurfaceActionGenerator:

    def __init__(self, product_defs):
        self.product_defs = product_defs
        self.common_action_generators = [
            KeyboardControllerCommonPotActionGenerator(product_defs),
            KeyboardControllerCommonScaleActionGenerator(product_defs),
            KeyboardControllerCommonPotLayoutActionGenerator(product_defs),
            KeyboardControllerCommonPadLayoutActionGenerator(product_defs),
            KeyboardControllerCommonPadActionGenerator(product_defs),
        ]

        self.event_type_to_button = {
            self.product_defs.SurfaceEvent.ButtonMixerRight.value: self.product_defs.Button.MixerRight,
            self.product_defs.SurfaceEvent.ButtonMixerLeft.value: self.product_defs.Button.MixerLeft,
            self.product_defs.SurfaceEvent.ButtonChannelRackUp.value: self.product_defs.Button.ChannelRackUp,
            self.product_defs.SurfaceEvent.ButtonChannelRackDown.value: self.product_defs.Button.ChannelRackDown,
            self.product_defs.SurfaceEvent.ButtonPresetUp.value: self.product_defs.Button.PresetUp,
            self.product_defs.SurfaceEvent.ButtonPresetDown.value: self.product_defs.Button.PresetDown,
            self.product_defs.SurfaceEvent.ButtonPageLeft.value: self.product_defs.Button.PageLeft,
            self.product_defs.SurfaceEvent.ButtonPageRight.value: self.product_defs.Button.PageRight,
            self.product_defs.SurfaceEvent.ButtonTransportPlay.value: self.product_defs.Button.TransportPlay,
            self.product_defs.SurfaceEvent.ButtonTransportStop.value: self.product_defs.Button.TransportStop,
            self.product_defs.SurfaceEvent.ButtonTransportRecord.value: self.product_defs.Button.TransportRecord,
            self.product_defs.SurfaceEvent.ButtonScoreLog.value: self.product_defs.Button.ScoreLog,
            self.product_defs.SurfaceEvent.ButtonShift.value: self.product_defs.Button.Shift,
            self.product_defs.SurfaceEvent.ButtonQuantise.value: self.product_defs.Button.Quantise,
            self.product_defs.SurfaceEvent.ButtonMetronome.value: self.product_defs.Button.Metronome,
            self.product_defs.SurfaceEvent.ButtonUndo.value: self.product_defs.Button.Undo,
            self.product_defs.SurfaceEvent.ButtonRedo.value: self.product_defs.Button.Redo,
            self.product_defs.SurfaceEvent.ButtonTapTempo.value: self.product_defs.Button.TapTempo}

    def handle_midi_event(self, fl_event):

        for action_generator in self.common_action_generators:
            if actions := action_generator.handle_midi_event(fl_event):
                return actions

        event_type = fl_event.status, fl_event.data1
        if button := self.event_type_to_button.get(event_type, None):
            if fl_event.data2 == 0:
                return [ButtonReleasedAction(button=button)]
            else:
                return [ButtonPressedAction(button=button)]
