from util.enum import Enum


def scale_colour(values, scalar):
    return tuple([int(value * scalar) for value in values])


class Colours(Enum):
    off = 0
    available = 1
    button_pressed = 3
    button_toggle_on = 3
    channel_rack_pad_selected = 3
    channel_rack_pad_pressed = 21
    fpc_orange = 108
    fpc_blue = 38
    fruity_slicer_purple = 43, 21, 127
    instrument_pad_pressed = 3
    pad_pressed = 127, 127, 127
    slicex_pink = 56
    exit_step_edit_latch_mode = 3
    step_pitch_step_latched = scale_colour((105, 127, 75), 1.0)
    step_pitch_step_on = scale_colour((87, 112, 60), 0.30)
    step_pitch_step_off = scale_colour((87, 112, 60), 0.05)
    step_velocity_step_latched = scale_colour((53, 116, 127), 1.0)
    step_velocity_step_on = scale_colour((57, 86, 103), 0.35)
    step_velocity_step_off = scale_colour((4, 54, 78), 0.05)
    step_release_step_latched = scale_colour((49, 127, 90), 1.0)
    step_release_step_on = scale_colour((24, 100, 59), 0.35)
    step_release_step_off = scale_colour((2, 75, 30), 0.05)
    step_pitch_fine_step_latched = scale_colour((127, 43, 57), 1.0)
    step_pitch_fine_step_on = scale_colour((108, 22, 31), 0.35)
    step_pitch_fine_step_off = scale_colour((102, 14, 23), 0.05)
    step_pan_step_latched = scale_colour((101, 60, 127), 1.0)
    step_pan_step_on = scale_colour((69, 36, 95), 0.35)
    step_pan_step_off = scale_colour((57, 24, 85), 0.05)
    step_mod_x_step_latched = scale_colour((63, 127, 28), 1.0)
    step_mod_x_step_on = scale_colour((37, 88, 12), 0.35)
    step_mod_x_step_off = scale_colour((24, 76, 1), 0.05)
    step_mod_y_step_latched = scale_colour((127, 105, 28), 1.0)
    step_mod_y_step_on = scale_colour((93, 74, 12), 0.35)
    step_mod_y_step_off = scale_colour((82, 62, 2), 0.025)
    step_shift_step_latched = scale_colour((127, 65, 28), 1.0)
    step_shift_step_on = scale_colour((114, 49, 14), 0.35)
    step_shift_step_off = scale_colour((100, 32, 1), 0.05)
