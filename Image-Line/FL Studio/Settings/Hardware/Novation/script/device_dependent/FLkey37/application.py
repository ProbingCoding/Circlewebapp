from script.device_independent.view import ButtonFunctionScreenView, ChannelSelectedScreenView, DumpScoreLogButtonView, \
    MetronomeButtonView, QuantiseButtonView, RedoButtonView, ScaleModelController, SequencerStepEditScreenView, \
    ShowHighlightsView, TapTempoButtonView, TransportPlayPauseButtonView, TransportRecordButtonView, \
    TransportStopButtonView, UndoButtonView
from script.device_dependent.FLkey import ChannelPanPotLayoutManager, ChannelRackPadLayoutManager, \
    ChannelVolumePotLayoutManager, CustomPadLayoutManager, InstrumentPadLayoutManager, MixerPanPotLayoutManager, \
    MixerVolumePotLayoutManager, MomentaryPotLayoutManager, PluginPotLayoutManager, SequencerPadLayoutManager
from util.command_dispatcher import CommandDispatcher
from .scale_chord_pad_layout_manager import ScaleChordPadLayoutManager
from .user_chord_pad_layout_manager import UserChordPadLayoutManager
from script.model import Model
from script.device_independent.fl_gui.fl_window_manager import FLWindowManager


class Application:

    def __init__(self, pad_led_writer, button_led_writer, fl, action_dispatcher, screen_writer,
                 device_manager,
                 product_defs):
        self.active_pad_layout_manager = None
        self.active_pot_layout_manager = None
        self.pad_led_writer = pad_led_writer
        self.button_led_writer = button_led_writer
        self.fl = fl
        self.action_dispatcher = action_dispatcher
        self.command_dispatcher = CommandDispatcher()
        self.screen_writer = screen_writer
        self.device_manager = device_manager
        self.product_defs = product_defs
        self.model = None

        self.global_views = set()
        self.fl_window_manager = FLWindowManager(action_dispatcher, fl)

    def init(self):
        self.active_pad_layout_manager = None
        self.active_pot_layout_manager = None
        self.model = Model()
        self.action_dispatcher.subscribe(self)

        self.global_views = {
            ButtonFunctionScreenView(self.action_dispatcher, self.screen_writer, self.fl),
            ChannelSelectedScreenView(self.action_dispatcher, self.screen_writer, self.fl),
            DumpScoreLogButtonView(self.action_dispatcher, self.fl, self.product_defs),
            MetronomeButtonView(self.action_dispatcher, self.fl, self.product_defs),
            QuantiseButtonView(self.action_dispatcher, self.fl, self.product_defs),
            RedoButtonView(self.action_dispatcher, self.fl, self.product_defs),
            ScaleModelController(self.action_dispatcher, self.product_defs, self.model),
            SequencerStepEditScreenView(self.action_dispatcher, self.screen_writer, self.fl),
            ShowHighlightsView(self.action_dispatcher, self.product_defs, self.model),
            TapTempoButtonView(self.action_dispatcher, self.fl, self.product_defs),
            TransportPlayPauseButtonView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs),
            TransportRecordButtonView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs),
            TransportStopButtonView(self.action_dispatcher, self.fl, self.product_defs),
            UndoButtonView(self.action_dispatcher, self.fl, self.product_defs),
        }
        for view in self.global_views:
            view.show()

    def deinit(self):
        for view in self.global_views:
            view.hide()

        if self.active_pad_layout_manager:
            self.active_pad_layout_manager.hide()

        if self.active_pot_layout_manager:
            self.active_pot_layout_manager.hide()

        self.action_dispatcher.unsubscribe(self)

    def handle_TempoChangedAction(self, action):
        self.device_manager.set_tempo(self.fl.get_tempo())
        if self.fl.get_master_sync_enabled():
            self.screen_writer.display_notification(primary_text="Tempo (External)")

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("TapTempo"):
            if self.fl.get_master_sync_enabled():
                self.screen_writer.display_notification(primary_text="Tempo (External)")

    def handle_PadLayoutChangedAction(self, action):
        if self.active_pad_layout_manager:
            self.active_pad_layout_manager.hide()

        self.active_pad_layout_manager = self._create_pad_layout_manager(action.layout)
        if self.active_pad_layout_manager:
            self.active_pad_layout_manager.show()

    def handle_PotLayoutChangedAction(self, action):
        skip_window_focusing = isinstance(self.active_pot_layout_manager, (MomentaryPotLayoutManager))

        if self.active_pot_layout_manager:
            self.active_pot_layout_manager.hide()

        self.active_pot_layout_manager = self._create_pot_layout_manager(action.layout)
        if self.active_pot_layout_manager:
            self.active_pot_layout_manager.show()
            if not skip_window_focusing:
                self.active_pot_layout_manager.focus_windows()

    def _create_pad_layout_manager(self, layout):
        if layout == self.product_defs.PadLayout.ChannelRack:
            return ChannelRackPadLayoutManager(self.action_dispatcher, self.pad_led_writer, self.button_led_writer,
                                               self.screen_writer, self.fl, self.product_defs, self.model,
                                               self.fl_window_manager)
        if layout == self.product_defs.PadLayout.Instrument:
            return InstrumentPadLayoutManager(self.action_dispatcher, self.pad_led_writer, self.button_led_writer,
                                              self.screen_writer, self.fl, self.product_defs, self.model)
        if layout == self.product_defs.PadLayout.Sequencer:
            return SequencerPadLayoutManager(self.action_dispatcher, self.command_dispatcher, self.pad_led_writer,
                                             self.button_led_writer, self.screen_writer, self.fl, self.product_defs,
                                             self.model, self.device_manager, self.fl_window_manager)
        if layout == self.product_defs.PadLayout.ScaleChord:
            return ScaleChordPadLayoutManager(self.action_dispatcher, self.button_led_writer, self.screen_writer,
                                              self.fl, self.product_defs, self.model)
        if layout == self.product_defs.PadLayout.UserChord:
            return UserChordPadLayoutManager(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs,
                                             self.model)
        if layout == self.product_defs.PadLayout.Custom:
            return CustomPadLayoutManager(self.action_dispatcher, self.button_led_writer, self.screen_writer, self.fl,
                                          self.product_defs, self.model)
        return None

    def _create_pot_layout_manager(self, layout):
        if layout == self.product_defs.PotLayout.MixerVolume:
            return MixerVolumePotLayoutManager(self.action_dispatcher, self.button_led_writer, self.fl,
                                               self.screen_writer, self.product_defs, self.model,
                                               self.fl_window_manager)
        if layout == self.product_defs.PotLayout.MixerPan:
            return MixerPanPotLayoutManager(self.action_dispatcher, self.button_led_writer, self.fl, self.screen_writer,
                                            self.product_defs, self.model, self.fl_window_manager)
        if layout == self.product_defs.PotLayout.ChannelVolume:
            return ChannelVolumePotLayoutManager(self.action_dispatcher, self.fl, self.screen_writer, self.model,
                                                 self.fl_window_manager)
        if layout == self.product_defs.PotLayout.ChannelPan:
            return ChannelPanPotLayoutManager(self.action_dispatcher, self.fl, self.screen_writer, self.model,
                                              self.fl_window_manager)
        if layout == self.product_defs.PotLayout.Plugin:
            return PluginPotLayoutManager(self.action_dispatcher, self.fl, self.screen_writer)
        if layout == self.product_defs.PotLayout.Momentary:
            return MomentaryPotLayoutManager(self.action_dispatcher, self.fl, self.model)
        return None
