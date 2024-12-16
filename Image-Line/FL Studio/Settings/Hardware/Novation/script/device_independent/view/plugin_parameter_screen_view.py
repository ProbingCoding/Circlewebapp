from math import isclose

from script.constants import PluginPotParameterType, Pots
from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags


class PluginParameterScreenView(View):

    def __init__(self, action_dispatcher, fl, screen_writer, native_plugin_parameters):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.screen_writer = screen_writer
        self.native_plugin_parameters = native_plugin_parameters

    def _on_show(self):
        self._handle_channel_selected()

    def _on_hide(self):
        self._set_primary_text_for_all_pots('')

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.ChannelSelection.value or action.flags & RefreshFlags.ChannelGroup.value:
            self._handle_channel_selected()

    def _handle_channel_selected(self):
        plugin_parameters = self.native_plugin_parameters.get(self.fl.get_instrument_plugin())
        if plugin_parameters is None:
            self._set_primary_text_for_all_pots('Not Used')
        else:
            for pot in range(Pots.Num.value):
                if pot >= len(plugin_parameters) or plugin_parameters[pot] is None:
                    self._set_primary_text_for_pot(pot, 'Not Used')

    def _set_primary_text_for_pot(self, pot, text):
        self.screen_writer.display_parameter(pot, name=text, value="")

    def _set_primary_text_for_all_pots(self, text):
        for pot in range(Pots.Num.value):
            self._set_primary_text_for_pot(pot, text)

    def _get_parameter_name_and_value(self, parameter, action_value):
        if parameter is None:
            return 'Not Used', '-'

        name = self.fl.get_parameter_name(parameter.index) if parameter.name is None else parameter.name

        if parameter.discrete_regions:
            value = self._get_region_name_for_value(parameter.discrete_regions, action_value)
        elif parameter.type is PluginPotParameterType.Channel:
            min, max = (0, 100) if parameter.deadzone_centre is None else (-100, 100)
            value = self._normalised_value_to_percentage_string(action_value, min=min, max=max)
        else:
            value = self.fl.get_parameter_value_as_string(parameter.index) or \
                    self._normalised_value_to_percentage_string(self.fl.get_parameter_value(parameter.index))

        return name, value

    def handle_PluginParameterValueChangedAction(self, action):
        name, value = self._get_parameter_name_and_value(action.parameter, action.value)
        self.screen_writer.display_parameter(action.control, name=name, value=value)

    def _get_region_name_for_value(self, discrete_regions, value):
        for lower_boundary, name in reversed(discrete_regions):
            if isclose(lower_boundary, value, abs_tol=1e-6) or lower_boundary < value:
                return name
        return ''

    def _normalised_value_to_percentage_string(self, normalised_value, *, min=0, max=100, num_decimals=0):
        value = (max - min) * normalised_value + min
        return f'{format(value, f".{num_decimals}f")}%'
