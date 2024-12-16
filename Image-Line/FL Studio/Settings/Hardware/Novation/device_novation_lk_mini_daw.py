# name=Novation Launchkey Mini MK3

from script.action_generators.fl_action_generator import FLActionGenerator
from script.device_adapters.fl_setup import make_fl_setup
from script.device_dependent.LaunchkeyMini import Application
from script.firmware_version_validation_controller import FirmwareVersionValidationController
from util.action_dispatcher import ActionDispatcher
from script.device_adapters.device_setup import make_device_setup
from script.fl import FL
from script.fl_to_application_adapter import FLToApplicationAdapter
from script.sender import Sender
from script.device_adapters.screen_writer import make_screen_writer
from script.constants import DeviceId
from script.action_generators.surface_action_generator import make_surface_action_generator
from script.product_defs import make_product_defs
from script.device_adapters.led_writer import make_led_writer

device_id = DeviceId.LaunchkeyMini

# Get product definitions
product_defs = make_product_defs(device_id)

# Set up utilities
sender = Sender()

# Set up driven/secondary actors
fl = FL()
device_setup = make_device_setup(device_id, sender, product_defs)
fl_setup = make_fl_setup(device_id, fl)
led_writer = make_led_writer(device_id, sender, product_defs)
screen_writer = make_screen_writer(device_id, sender, product_defs)

# Set up application
action_dispatcher = ActionDispatcher()
firmware_version_validation_controller = FirmwareVersionValidationController(action_dispatcher, product_defs, fl,
                                                                             sender)
application = Application(led_writer, led_writer, fl, action_dispatcher, screen_writer, product_defs)

# Set up driver/primary actors
surface_action_generator = make_surface_action_generator(device_id, action_dispatcher, product_defs)
fl_action_generator = FLActionGenerator(action_dispatcher, fl)

# Set up fl to application adapter
fl_to_application_adapter = FLToApplicationAdapter(device_setup, fl_setup, application, led_writer, action_dispatcher,
                                                   surface_action_generator, fl_action_generator,
                                                   firmware_version_validation_controller)


def OnInit():
    fl_to_application_adapter.on_init()


def OnDeInit():
    fl_to_application_adapter.on_deinit()


def OnMidiIn(fl_event):
    fl_to_application_adapter.on_midi(fl_event)


def OnRefresh(flags):
    fl_to_application_adapter.on_refresh(flags)


def OnIdle():
    fl_to_application_adapter.on_idle()


def OnDirtyChannel(channel, update_type):
    fl_to_application_adapter.on_dirty_channel(channel, update_type)


def OnDirtyMixerTrack(index):
    fl_to_application_adapter.on_dirty_mixer_track(index)


def OnProjectLoad(status):
    fl_to_application_adapter.on_project_load(status)


def OnFirstConnect():
    fl_to_application_adapter.on_first_connect()
