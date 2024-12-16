from script.device_independent.util_view.view import View
from script.constants import ChannelNavigationMode, ChannelNavigationSteps, HighlightDuration, Pots


class ChannelBankControlsHighlightView(View):

    def __init__(self, action_dispatcher, fl, model):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model

    def _on_show(self):
        if self.model.show_all_highlights_active:
            self._highlight_selected_channel_bank_controls()

    def _on_hide(self):
        self._highlight_selected_channel_bank_controls(duration_ms=0)

    @property
    def highlight_duration_ms(self):
        if self.model.show_all_highlights_active:
            return HighlightDuration.WithoutEnd.value
        return HighlightDuration.Default.value

    def handle_ShowHighlightsAction(self, action):
        self._highlight_selected_channel_bank_controls()

    def handle_HideHighlightsAction(self, action):
        self._highlight_selected_channel_bank_controls(duration_ms=0)

    def handle_ChannelBankChangeAttemptedAction(self, action):
        if self.model.channel_rack.navigation_mode == ChannelNavigationMode.Bank.value:
            self._highlight_selected_channel_bank_controls(duration_ms=self.highlight_duration_ms)

    def handle_ChannelRackNavigationModeChangedAction(self, action):
        self._highlight_selected_channel_bank_controls(duration_ms=self.highlight_duration_ms)

    def handle_ChannelSelectAttemptedAction(self, action):
        if self.model.channel_rack.navigation_mode == ChannelNavigationMode.Single.value:
            self._highlight_selected_channel_bank_controls(duration_ms=self.highlight_duration_ms)

    def handle_FlGuiChannelSelectAction(self, action):
        self._highlight_selected_channel_bank_controls(duration_ms=self.highlight_duration_ms)

    def _highlight_selected_channel_bank_controls(self, *, duration_ms=HighlightDuration.WithoutEnd.value):
        navigation_mode = self.model.channel_rack.navigation_mode

        if navigation_mode is None:
            return
        elif navigation_mode == ChannelNavigationMode.Bank.value:
            selected_channel = self.model.channel_rack.active_bank * ChannelNavigationSteps.Bank.value
        elif navigation_mode == ChannelNavigationMode.Single.value:
            selected_channel = self.fl.selected_channel()

        if selected_channel is None:
            self.fl.highlight_channelrack_controls(first_channel=0, num_channels=Pots.Num.value,
                                                   duration_ms=0)

        else:
            self.fl.highlight_channelrack_controls(first_channel=selected_channel, num_channels=Pots.Num.value,
                                                   duration_ms=duration_ms)
