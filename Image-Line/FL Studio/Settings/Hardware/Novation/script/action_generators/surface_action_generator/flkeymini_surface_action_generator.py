from script.action_generators.surface_action_generator.surface_actions import ButtonPressedAction, ButtonReleasedAction
from util.enum import Enum
from .keyboard_controller_common import KeyboardControllerCommonPadActionGenerator, \
    KeyboardControllerCommonPadLayoutActionGenerator, KeyboardControllerCommonPotActionGenerator, \
    KeyboardControllerCommonPotLayoutActionGenerator, KeyboardControllerCommonScaleActionGenerator


class FLkeyMiniSurfaceActionGenerator:
    class ButtonState(Enum):
        Released = 0
        Pressed = 1

    class HeldButton:
        def __init__(self, button):
            self.button = button
            self.released_early = False
            self.shift_state = FLkeyMiniSurfaceActionGenerator.ButtonState.Released

    def __init__(self, product_defs):
        self.product_defs = product_defs
        self.shift_state = self.ButtonState.Released
        self.held_buttons = {}
        self.common_action_generators = [
            KeyboardControllerCommonPotActionGenerator(product_defs),
            KeyboardControllerCommonScaleActionGenerator(product_defs),
            KeyboardControllerCommonPotLayoutActionGenerator(product_defs),
            KeyboardControllerCommonPadLayoutActionGenerator(product_defs),
            KeyboardControllerCommonPadActionGenerator(product_defs),
        ]
        self.event_type_to_button = {
            self.product_defs.SurfaceEvent.ButtonChannelRackUp.value: self.product_defs.Button.ChannelRackUp,
            self.product_defs.SurfaceEvent.ButtonChannelRackDown.value: self.product_defs.Button.ChannelRackDown,
            self.product_defs.SurfaceEvent.ButtonTapTempo.value: self.product_defs.Button.TapTempo,
            self.product_defs.SurfaceEvent.ButtonTransportPlay.value: self.product_defs.Button.TransportPlay,
            self.product_defs.SurfaceEvent.ButtonTransportRecord.value: self.product_defs.Button.TransportRecord}
        self.event_type_to_shift_button = {
            self.product_defs.SurfaceEvent.ButtonMixerRight.value: self.product_defs.Button.MixerRightShift,
            self.product_defs.SurfaceEvent.ButtonMixerLeft.value: self.product_defs.Button.MixerLeftShift,
            self.product_defs.SurfaceEvent.ButtonChannelRackUp.value: self.product_defs.Button.ChannelRackUpShift,
            self.product_defs.SurfaceEvent.ButtonChannelRackDown.value: self.product_defs.Button.ChannelRackDownShift,
            self.product_defs.SurfaceEvent.ButtonPresetUp.value: self.product_defs.Button.PresetUpShift,
            self.product_defs.SurfaceEvent.ButtonPresetDown.value: self.product_defs.Button.PresetDownShift}

    def handle_midi_event(self, fl_event):
        for action_generator in self.common_action_generators:
            if actions := action_generator.handle_midi_event(fl_event):
                return actions

        event_type = fl_event.status, fl_event.data1

        if event_type == self.product_defs.SurfaceEvent.ButtonShift.value:
            button = self.product_defs.Button.Shift
        elif self.shift_state == self.ButtonState.Released:
            button = self.event_type_to_button.get(event_type, None)
        else:
            button = self.event_type_to_shift_button.get(event_type, None)

        # If shift is pressed or released, first generate release actions for all held buttons
        if button == self.product_defs.Button.Shift:
            actions = self.generate_release_actions_for_all_held_buttons(self.held_buttons)
            if fl_event.data2 == 0:
                self.shift_state = self.ButtonState.Released
                actions.append(ButtonReleasedAction(button=button))
            else:
                self.shift_state = self.ButtonState.Pressed
                actions.append(ButtonPressedAction(button=button))
            return actions

        # For any other buttons generate a press or release action
        if button:
            if fl_event.data2 == 0:
                held_button = self.held_buttons.pop(event_type)
                if not held_button.released_early:
                    return [ButtonReleasedAction(button=button)]
            else:
                self.held_buttons[event_type] = FLkeyMiniSurfaceActionGenerator.HeldButton(button)
                return [ButtonPressedAction(button=button)]

    @staticmethod
    def generate_release_actions_for_all_held_buttons(held_buttons):
        actions = []
        for held_button in held_buttons.values():
            if not held_button.released_early:
                actions.append(ButtonReleasedAction(button=held_button.button))
            held_button.released_early = True

        return actions
