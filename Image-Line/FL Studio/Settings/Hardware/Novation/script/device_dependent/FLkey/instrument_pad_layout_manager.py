from script.actions import ChannelRackNavigationModeChangedAction, FlGuiChannelSelectAction
from script.colours import Colours
from script.constants import ChannelNavigationMode
import script.device_independent.view as view
from script.fl_constants import InstrumentPlugin, RefreshFlags
from util.mapped_pad_led_writer import MappedPadLedWriter


class InstrumentPadLayoutManager:
    def __init__(self, action_dispatcher, pad_led_writer, button_led_writer, screen_writer, fl, product_defs, model):
        self.action_dispatcher = action_dispatcher
        self.button_led_writer = button_led_writer
        self.fl = fl
        self.product_defs = product_defs
        self.model = model
        self.pad_led_writer = MappedPadLedWriter(
            pad_led_writer, product_defs.Constants.NotesForPadLayout.value[product_defs.PadLayout.Instrument])
        self.channel_selection_dependent_views = {
            view.ChannelSelectNameHighlightView(self.action_dispatcher, self.fl, model),
            view.PresetButtonScreenView(action_dispatcher, screen_writer, fl),
            view.PresetButtonView(action_dispatcher, button_led_writer, fl, product_defs)
        }
        self.channel_selection_independent_views = {
            view.ChannelSelectView(self.action_dispatcher, self.button_led_writer, self.fl, product_defs),
            view.DefaultInstrumentLayoutScaledMappingController(self.action_dispatcher, model),
        }

        self.selected_channel = None
        self.selected_plugin = None
        self.active_instrument_view = None
        self.active_plugin_bank_view = None

    def show(self):
        self.model.channel_rack.navigation_mode = ChannelNavigationMode.Single
        self.action_dispatcher.dispatch(ChannelRackNavigationModeChangedAction())
        self.action_dispatcher.subscribe(self)
        if self.fl.is_any_channel_selected():
            self._handle_channel_selected()
            for global_view in self.channel_selection_dependent_views:
                global_view.show()

        for global_view in self.channel_selection_independent_views:
            global_view.show()

    def hide(self):
        self._hide_all_views()
        self.action_dispatcher.unsubscribe(self)

    def handle_OnRefreshAction(self, action):
        if self.fl.is_any_channel_selected():
            if action.flags & RefreshFlags.ChannelSelection.value or \
                    action.flags & RefreshFlags.ChannelGroup.value:
                self._handle_channel_selected()
                self.action_dispatcher.dispatch(FlGuiChannelSelectAction())

    def handle_ChannelSelectionToggleAction(self, action):
        if action.any_channel_selected:
            for view in self.channel_selection_dependent_views:
                view.show()
            self._update_instrument_view()
        else:
            self._handle_channel_unselected()

    def _handle_channel_selected(self):
        current_channel = self.fl.get_selected_global_channel()
        current_plugin = self.fl.get_instrument_plugin()

        if current_channel == self.selected_channel and current_plugin == self.selected_plugin:
            return

        self.selected_channel = current_channel
        self.selected_plugin = current_plugin
        self._handle_plugin_changed()

    def _handle_channel_unselected(self):
        self._hide_active_view_components()
        for global_view in self.channel_selection_dependent_views:
            global_view.hide()

        self.selected_plugin = None

    def _hide_active_view_components(self):
        if self.active_instrument_view:
            self.active_instrument_view.hide()
            self.active_instrument_view = None
        if self.active_plugin_bank_view:
            self.active_plugin_bank_view.hide()
            self.active_plugin_bank_view = None

    def _hide_all_views(self):
        for global_view in self.channel_selection_dependent_views:
            global_view.hide()
        for global_view in self.channel_selection_independent_views:
            global_view.hide()

        self._hide_active_view_components()

    def _handle_plugin_changed(self):
        self._hide_active_view_components()
        self._update_instrument_view()
        self._update_plugin_bank_view()

    def _update_instrument_view(self):
        if self.active_instrument_view:
            self.active_instrument_view.hide()
        self.active_instrument_view = self._create_instrument_view_for_plugin(self.selected_plugin)
        self.active_instrument_view.show()

    def _create_instrument_view_for_plugin(self, plugin):
        if plugin == InstrumentPlugin.Fpc.value:
            return view.Fpc(self.action_dispatcher, self.pad_led_writer, self.fl, self.model)
        if plugin == InstrumentPlugin.FruitySlicer:
            return view.SlicerPluginView(self.action_dispatcher, self.pad_led_writer, self.fl, self.model,
                                         available_colour=Colours.fruity_slicer_purple)
        if plugin == InstrumentPlugin.SliceX.value:
            return view.SlicerPluginView(self.action_dispatcher, self.pad_led_writer, self.fl, self.model,
                                         available_colour=Colours.slicex_pink)
        return view.Default(self.action_dispatcher, self.pad_led_writer, self.fl, self.model)

    def _update_plugin_bank_view(self):
        if self.active_plugin_bank_view:
            self.active_plugin_bank_view.hide()
        self.active_plugin_bank_view = self._create_bank_view_for_plugin(self.selected_plugin)
        self.active_plugin_bank_view.show()

    def _create_bank_view_for_plugin(self, plugin):
        if plugin == InstrumentPlugin.Fpc:
            return view.FpcBankView(self.action_dispatcher, self.button_led_writer, self.product_defs, self.model)
        if plugin == InstrumentPlugin.FruitySlicer:
            return view.SlicerPluginBankView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs,
                                             self.model)
        if plugin == InstrumentPlugin.SliceX:
            return view.SlicerPluginBankView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs,
                                             self.model)
        return view.DefaultBankView(self.action_dispatcher, self.button_led_writer, self.product_defs, self.model)
