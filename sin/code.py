import time
import board
import busio
import digitalio
import random
import supervisor
import audiocore
import audiomixer
from audiopwmio import PWMAudioOut as AudioOut
import adafruit_aw9523
import array
import time
import math
from pins import *

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

audio = AudioOut( board.GP27)
mixer = audiomixer.Mixer(voice_count=16, sample_rate=8000, channel_count=1,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer) # attach mixer to audio playback



# i2c setup, higher frequency for display refresh
i2c = busio.I2C(board.GP1, board.GP0, frequency=1000000)
#  i2c AW9523 GPIO expander setup
aw = adafruit_aw9523.AW9523(i2c)

#  array for LEDs on AW9523
leds = []
led_pins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
#  setup to create the AW9523 outputs for LEDs
for led in led_pins:
    led_pin = aw.get_pin(led)
    led_pin.direction = digitalio.Direction.OUTPUT
    leds.append(led_pin)

note_buttons = []

for pin in note_pins:
    note_pin = digitalio.DigitalInOut(pin)
    note_pin.direction = digitalio.Direction.INPUT
    note_pin.pull = digitalio.Pull.UP
    note_buttons.append(note_pin)

#  note states
note0_pressed = False
note1_pressed = False
note2_pressed = False
note3_pressed = False
note4_pressed = False
note5_pressed = False
note6_pressed = False
note7_pressed = False
note8_pressed = False
note9_pressed = False
note10_pressed = False
note11_pressed = False
note12_pressed = False
note13_pressed = False
note14_pressed = False
note15_pressed = False
#  array of note states
note_states = [note0_pressed, note1_pressed, note2_pressed, note3_pressed,
            note4_pressed, note5_pressed, note6_pressed, note7_pressed,
            note8_pressed, note9_pressed, note10_pressed, note11_pressed,
            note12_pressed, note13_pressed, note14_pressed, note15_pressed]

#  array for 5-way switch
joystick = [select, up, down, left, right]

for joy in joystick:
    joy.direction = digitalio.Direction.INPUT
    joy.pull = digitalio.Pull.UP

#  states for 5-way switch
select_state = None
up_state = None
down_state = None
left_state = None
right_state = None
midi_state = None

#  check for blinking LED
led_check = None

#  time.monotonic() device
clock = time.monotonic()
clock_select_long = time.monotonic()
select_long_counter = 0

clock_button_repeat = time.monotonic_ns()
button_repeat = 0

pressed = False


freq = [32,36,41,43,46,48,52,55,61,65,69,73,79,82,87,92]

def handle_sample(num, pressed):
    voice = mixer.voice[num]   # get mixer voice
    if pressed:
        length = 8000 // freq[num]
        print(freq[num])
        sine_wave = array.array("h", [0] * length)
        for i in range(length):
            sine_wave[i] = int(math.sin(math.pi * 2 * i / length) * (2 ** 15))
        wave = audiocore.RawSample(sine_wave)
        voice.play(wave,loop=True)
    else: # released
        voice.stop()  # only stop looping samples, others one-shot

while True:
    #  MIDI input
    for i in range(16):
        buttons = note_buttons[i]
        if not buttons.value and note_states[i] is False:
            leds[i].value = True
            handle_sample(i, True)
            note_states[i] = True

        #  if the button is released...
        if buttons.value and note_states[i] is True:
            #  stop sending the MIDI note and turn off the LED
            handle_sample(i, False)
            leds[i].value = False
            note_states[i] = False

