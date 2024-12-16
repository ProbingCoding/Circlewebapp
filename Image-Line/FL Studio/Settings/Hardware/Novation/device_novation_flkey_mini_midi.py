# name=Novation FLkey Mini MIDI
# supportedHardwareIds=00 20 29 3B 01 00 00
# url=https://forum.image-line.com/viewtopic.php?f=1914&t=277142
import util.math
from script.fl import FL

fl = FL()


def OnPitchBend(eventData):
    eventData.handled = True

    if not fl.is_any_channel_selected():
        return

    value = (eventData.data1 | eventData.data2 << 7)
    normalised_pitch = util.math.normalise(value=value, lower_bound=0, upper_bound=1 << 14)
    fl.channel.set_pitch(normalised_pitch)
