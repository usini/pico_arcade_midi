#https://github.com/todbot/plinkykeeb/blob/main/circuitpython/code_plinkykeeb_sampleplayer.py
#https://github.com/todbot/circuitpython-tricks/blob/main/larger-tricks/breakbeat_sampleplayer.py
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

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

wav_files = (
    # filename,           loop?
    ('wav/13.wav', False), # 137.72 bpm
    ('wav/14.wav', False),
    ('wav/14.wav', False),
    ('wav/13.wav', False),
    ('wav/13.wav', False),
    ('wav/14.wav', False),
    ('wav/15.wav', False),
    ('wav/14.wav', False),
    ('wav/5.wav', False),
    ('wav/6.wav', False),
    ('wav/7.wav', False),
    ('wav/8.wav', False),
    ('wav/1.wav', False),
    ('wav/2.wav', False),
    ('wav/3.wav', False),
    ('wav/4.wav', False)
)

audio = AudioOut( board.GP27)
mixer = audiomixer.Mixer(voice_count=len(wav_files), sample_rate=44100, channel_count=1,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer) # attach mixer to audio playback



from pins import *

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

def handle_sample(num, pressed):
    voice = mixer.voice[num]   # get mixer voice
    (wav_file, loopit) = wav_files[num]
    if pressed:
        if wav_file is not None:
            wave = audiocore.WaveFile(open(wav_file,"rb"))
            voice.play(wave,loop=loopit)
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
            #handle_sample(i, False)
            leds[i].value = False
            note_states[i] = False

