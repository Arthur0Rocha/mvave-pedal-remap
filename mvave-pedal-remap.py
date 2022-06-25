import time
from enum import Enum

import alsaseq

CLIENT_NAME = "MVAVE-PEDAL-REMAP"

CC_CODE = 10
PGM_CHANGE_CODE = 11

PGM_CHANGE_CHANNELS = 32

CC_Y2 = 2
CC_03 = 3
CC_PEDAL = 4
CC_VOLUME = 7
CC_USER_1 = 26
CC_USER_2 = 27
CC_USER_3 = 28
CC_USER_4 = 29
CC_PORTAMENTO_SW = 65
CC_FOOT_SW = 82

MVAVE_VALUE = 5
HIGH = 127
LOW = 0

VERBOSE = False

ABCD_CC_OFFSET = 32

EF_CC_OUT = [30, 31]

switch_states = [LOW] * PGM_CHANGE_CHANNELS
def get_switch_state_and_toggle(index: int):
    value = switch_states[index]
    switch_states[index] = HIGH - switch_states[index]
    return value

class SwitchBehaviour(Enum): # TODO include this functionality
    HIGH_ONLY = HIGH
    LOW_ONLY = LOW
    HIGH_AND_LOW = [HIGH, LOW]
    TOGGLE = get_switch_state_and_toggle

def create_CC_event(channel, param, value):
    return (CC_CODE, 0, 0, 253, (0, 0), (0, 0), (0, 0), (channel, 0, 0, 0, param, value))

def remap(event, invert_pedal = True, pedal_output_cc = CC_VOLUME, switch_behaviour : SwitchBehaviour = SwitchBehaviour.HIGH_ONLY):
    evtype = event[0]
    channel = event[7][0]

    if evtype not in [PGM_CHANGE_CODE, CC_CODE]:
        if VERBOSE:
            print("W0")
        return [event]
    param, value = event[7][4:]
    if evtype == PGM_CHANGE_CODE:
        if value in range(PGM_CHANGE_CHANNELS):
            if VERBOSE:
                label = ['A', 'B', 'C', 'D']
                print(f"{1+value//4}{label[value%4]}")
            return [create_CC_event(channel, ABCD_CC_OFFSET + value, HIGH)] # A, B, C, D
        else:
            if VERBOSE:
                print("W1")
            return [event] # Weird. This value shouldn't be accessible
    else:
        if param == CC_Y2:
            if VERBOSE:
                print("E")
            return [create_CC_event(channel, EF_CC_OUT[0], HIGH)] # E
        elif param == CC_03:
            if VERBOSE:
                print("F")
            return [create_CC_event(channel, EF_CC_OUT[1], HIGH)] # F
        elif param == CC_VOLUME:
            if invert_pedal:
                value = HIGH - value
            if VERBOSE:
                print(f"PEDAL - {value:03d}")
            return [create_CC_event(channel, pedal_output_cc, value)] # PEDAL
        else:
            if VERBOSE:
                print("W2")
            return [event] # Weird. This value shouldn't be accessible

def init():
    alsaseq.client(CLIENT_NAME, 1, 1, False)
    print(f"Started {CLIENT_NAME} Client.")

def loop():
    while True:
        time.sleep(0.001)
        while alsaseq.inputpending():
            out = remap(alsaseq.input())
            for o in out:
                alsaseq.output(o)

if __name__ == "__main__":
    init()
    loop()
