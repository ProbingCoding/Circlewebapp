from script.actions import PluginParameterValueChangedAction
from script.constants import PluginPotParameterType, Pots
from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags

from util.deadzone_value_converter import DeadzoneValueConverter


class PluginParameterView(View):

    def __init__(self, action_dispatcher, fl, native_plugin_parameters, *, control_to_index):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.native_plugin_parameters = native_plugin_parameters
        self.control_to_index = control_to_index
        self.parameters_for_index = []
        self.deadzone_converters_for_index = []
        self.action_dispatcher = action_dispatcher
        self.reset_pickup_on_first_movement = False

    def _on_show(self):
        self.action_dispatcher.subscribe(self)
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True

    def handle_ChannelSelectAction(self, action):
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.ChannelSelection.value or action.flags & RefreshFlags.ChannelGroup.value:
            self._update_plugin_parameters()

    def _update_plugin_parameters(self):
        plugin = self.fl.get_instrument_plugin()
        if plugin in self.native_plugin_parameters:
            parameters = self.native_plugin_parameters[plugin]
            self.parameters_for_index = parameters[:Pots.Num.value]
            self.deadzone_converters_for_index = [None] * len(self.parameters_for_index)
            for index, parameter in enumerate(self.parameters_for_index):
                if parameter and parameter.deadzone_centre:
                    self.deadzone_converters_for_index[index] = DeadzoneValueConverter(max=1.0,
                                                                                       centre=parameter.deadzone_centre,
                                                                                       width=parameter.deadzone_width)
        else:
            self.parameters_for_index = []
            self.deadzone_converters_for_index = []

    def handle_ControlChangedAction(self, action):
        index = self.control_to_index.get(action.control)
        if index is None or index >= len(self.parameters_for_index):
            return

        if self.reset_pickup_on_first_movement:
            self.reset_pickup_on_first_movement = False
            self._reset_pickup()

        parameter = self.parameters_for_index[index]

        if parameter is not None:
            position = action.position
            deadzone = self.deadzone_converters_for_index[index]
            if deadzone:
                position = deadzone(action.position)
            self._update_value_for_plugin_parameter(index, position, parameter)

    def _update_value_for_plugin_parameter(self, index, position, parameter):
        if parameter.type == PluginPotParameterType.Channel:
            self.fl.channel.set_parameter_value(parameter.index, position)
        elif parameter.type == PluginPotParameterType.Plugin:
            self.fl.plugin.set_parameter_value(parameter.index, position)

        self.action_dispatcher.dispatch(
            PluginParameterValueChangedAction(parameter=parameter, control=index, value=position))

    def _reset_pickup(self):
        for parameter in self.parameters_for_index:
            if parameter is not None and parameter.type is PluginPotParameterType.Plugin:
                self.fl.reset_parameter_pickup(parameter.index)
