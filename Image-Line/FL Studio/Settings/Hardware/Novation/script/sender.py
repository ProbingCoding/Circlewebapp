try:
    import device
except ImportError as e:
    print(e)


class Sender:

    def send_message(self, status, data1, data2):
        device.midiOutMsg(status | (data1 << 8) | (data2 << 16))

    def send_sysex(self, message):
        sysex = message
        sysex.insert(0, 0xF0)
        sysex.append(0xF7)
        device.midiOutSysex(bytes(sysex))
