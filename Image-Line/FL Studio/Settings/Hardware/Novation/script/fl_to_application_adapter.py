from script.fl_constants import ProjectLoadStatus
from util.decorators import cache_led_updates
import version


class FLToApplicationAdapter:

    def __init__(self, device_setup, fl_setup, application, led_update_cache, action_dispatcher,
                 surface_action_generator,
                 fl_action_generator, firmware_version_validation_controller):
        self.device_setup = device_setup
        self.fl_setup = fl_setup
        self.application = application
        self.led_update_cache = led_update_cache
        self.action_dispatcher = action_dispatcher
        self.surface_action_generator = surface_action_generator
        self.fl_action_generator = fl_action_generator
        self.firmware_version_validation_controller = firmware_version_validation_controller

    @property
    def led_cache(self):
        return self.led_update_cache

    @cache_led_updates
    def on_init(self):
        self._print_script_version()
        self.firmware_version_validation_controller.start_validation(on_success_callback=self._do_initialisation)

    def _do_initialisation(self):
        if self.firmware_version_validation_controller.validation_is_success():
            self.device_setup.init()
            self.application.init()

    @cache_led_updates
    def on_deinit(self):
        self.firmware_version_validation_controller.abort_validation()
        self._do_deinitialisation()

    def _do_deinitialisation(self):
        if self.firmware_version_validation_controller.validation_is_success():
            self.application.deinit()
            self.device_setup.deinit()

    @cache_led_updates
    def on_midi(self, fl_event):
        self.surface_action_generator.handle_midi_event(fl_event)
        self.firmware_version_validation_controller.handle_midi_event(fl_event)
        fl_event.handled = True

    @cache_led_updates
    def on_refresh(self, flags):
        self.fl_action_generator.handle_refresh_event(flags)

    @cache_led_updates
    def on_idle(self):
        self.fl_action_generator.handle_idle_event()

    @cache_led_updates
    def on_dirty_channel(self, channel, update_type):
        self.fl_action_generator.handle_dirty_channel_event(channel, update_type)

    @cache_led_updates
    def on_dirty_mixer_track(self, index):
        self.fl_action_generator.handle_dirty_mixer_track_event(index)

    def on_project_load(self, status):
        if status == ProjectLoadStatus.LoadStart:
            self._do_deinitialisation()
        if status == ProjectLoadStatus.LoadFinished:
            self._do_initialisation()

    @cache_led_updates
    def on_first_connect(self):
        self.fl_setup.handle_first_time_connected()

    @staticmethod
    def _print_script_version():
        print("version: {}".format(version.value))
