from script.actions import MixerBankChangeAttemptedAction, MixerBankChangedAction
from script.constants import Pots
from script.device_independent.util_view.scrolling_arrow_button_view import ScrollingArrowButtonView
from script.fl_constants import DockSide


class MixerBankView:
    tracks_per_bank = Pots.Num.value
    first_mixer_track_index = 1

    def __init__(self, action_dispatcher, button_led_writer, fl, product_defs, model):
        self.fl = fl
        self.model = model
        self.arrow_button_view = ScrollingArrowButtonView(action_dispatcher, button_led_writer, product_defs,
                                                          decrement_button="MixerBankLeft",
                                                          increment_button="MixerBankRight",
                                                          on_page_changed=self._on_page_changed,
                                                          on_page_change_attempt=self._on_page_change_attempt,
                                                          speed=ScrollingArrowButtonView.Speed.Slow.value)
        self.action_dispatcher = action_dispatcher
        self.action_dispatcher.subscribe(self)

    def show(self):
        self._handle_docked_tracks_changed()
        self.arrow_button_view.set_active_page(self.model.mixer_track_active_bank)
        self._update_mixer_bank_state(self.model.mixer_track_active_bank, self._get_tracks_for_center_dock())
        self.arrow_button_view.show()

    def hide(self):
        self.arrow_button_view.hide()

    def _on_page_changed(self):
        self.model.mixer_track_active_bank = self.arrow_button_view.active_page
        self._update_mixer_bank_state(self.model.mixer_track_active_bank, self._get_tracks_for_center_dock())
        self.action_dispatcher.dispatch(MixerBankChangedAction())

    def _on_page_change_attempt(self):
        self.action_dispatcher.dispatch(MixerBankChangeAttemptedAction())

    def _handle_docked_tracks_changed(self):
        tracks_in_center_dock = self._get_tracks_for_center_dock()
        self._update_num_banks(tracks_in_center_dock)

    def _update_mixer_bank_state(self, bank, tracks_in_center_dock):
        first_index = bank * self.tracks_per_bank
        last_index = first_index + self.tracks_per_bank - 1
        self.model.mixer_tracks_in_active_bank = tracks_in_center_dock[first_index:last_index + 1]

    def _update_num_banks(self, tracks_in_center_dock):
        num_pages = (len(tracks_in_center_dock) + self.tracks_per_bank - 1) // self.tracks_per_bank
        self.arrow_button_view.set_page_range(first_page=0, last_page=num_pages - 1)
        self._on_page_changed()

    def _get_tracks_for_center_dock(self):
        return [track for track in range(self.model.last_mixer_track_index + 1) if
                self.fl.get_dock_side_for_track(track) is DockSide.Center.value]

    def handle_AllMixerTracksChangedAction(self, action):
        self._handle_docked_tracks_changed()
