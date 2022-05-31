import time
import board
import displayio
import terminalio
import adafruit_aw9523
import busio
import adafruit_ssd1327
import digitalio
from adafruit_display_text import label
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect
import usb_midi
import adafruit_midi
from adafruit_midi.note_on          import NoteOn
from adafruit_midi.note_off         import NoteOff
from presets import *
from pins import *

# Turn on LED on Pico
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

# Conversion between midi notes and american notation
NOTES = ["C-1", "C#-1", "D-1", "D#-1", "E-1", "F-1", "F#-1", "G-1", "G#-1", "A-1", "A#-1", "B-1",
        "C0", "C#0", "D0", "D#0", "E0", "F0", "F#0", "G0", "G#0", "A0", "A#0", "B0",
        "C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
        "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
        "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3",
        "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
        "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",
        "C6", "C#6", "D6", "D#6", "E6", "F6", "F#6", "G6", "G#6", "A6", "A#6", "B6",
        "C7", "C#7", "D7", "D#7", "E7", "F7", "F#7", "G7", "G#7", "A7", "A#7", "B7",
        "C8", "C#8", "D8", "D#8", "E8", "F8", "F#8", "G8", "G#8", "A8", "A#8", "B8",
        "C9", "C#9", "D9", "D#9", "E9", "F9", "F#9", "G9", "G#9", "A9", "A#9", "B9"
        ]

displayio.release_displays()

# i2c setup, higher frequency for display refresh
i2c = busio.I2C(board.GP1, board.GP0, frequency=1000000)
#  i2c display setup
display_bus = displayio.I2CDisplay(i2c, device_address=0x3d)
#  i2c AW9523 GPIO expander setup
aw = adafruit_aw9523.AW9523(i2c)
#  MIDI setup as MIDI out device
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

# display dimensions
WIDTH = 128
HEIGHT = 128
#  display setup
display = adafruit_ssd1327.SSD1327(display_bus, width=WIDTH, height=HEIGHT, brightness=1)

#  main display group, shows default GUI menu
splash = displayio.Group()
#  group for circle icons
circle_group = displayio.Group()
#  group for text labels on circles
text_group = displayio.Group()

#  list of circle positions
spots = (
    (16, 16),
    (48, 16),
    (80, 16),
    (112, 16),
    (16, 48),
    (48, 48),
    (80, 48),
    (112, 48),
    (16, 80),
    (48, 80),
    (80, 80),
    (112, 80),
    (16, 112),
    (48, 112),
    (80, 112),
    (112, 112),
    )

#  creating the circles & pulling in positions from spots
for spot in spots:
    circle = Circle(x0=spot[0], y0=spot[1], r=14, fill=0x888888)
    # adding circles to their display group
    circle_group.append(circle)
#  square to show position on menu
rect = Rect(0, 0, 33, 33, fill=None, outline=0x00FF00, stroke=3)

splash.append(circle_group)
splash.append(rect)

#  strings and positions for the MIDI note text labels
texts = [
    {'num': NOTES[midi_notes[0]], 'pos': (10, 16)},
    {'num': NOTES[midi_notes[1]], 'pos': (42, 16)},
    {'num': NOTES[midi_notes[2]], 'pos': (74, 16)},
    {'num': NOTES[midi_notes[3]], 'pos': (106, 16)},
    {'num': NOTES[midi_notes[4]], 'pos': (10, 48)},
    {'num': NOTES[midi_notes[5]], 'pos': (42, 48)},
    {'num': NOTES[midi_notes[6]], 'pos': (74, 48)},
    {'num': NOTES[midi_notes[7]], 'pos': (106, 48)},
    {'num': NOTES[midi_notes[8]], 'pos': (10, 80)},
    {'num': NOTES[midi_notes[9]], 'pos': (42, 80)},
    {'num': NOTES[midi_notes[10]], 'pos': (74, 80)},
    {'num': NOTES[midi_notes[11]], 'pos': (106, 80)},
    {'num': NOTES[midi_notes[12]], 'pos': (10, 112)},
    {'num': NOTES[midi_notes[13]], 'pos': (42, 112)},
    {'num': NOTES[midi_notes[14]], 'pos': (74, 112)},
    {'num':NOTES[midi_notes[15]], 'pos': (106, 112)},
    ]
text_labels = []

for text in texts:
    text_area = label.Label(terminalio.FONT, text=text['num'], color=0xFFFFFF)
    text_area.x = text['pos'][0]
    text_area.y = text['pos'][1]
    text_labels.append(text_area)
    text_group.append(text_area)
splash.append(text_group)

#  secondary display group, shows large circle when button is selected
big_splash = displayio.Group()
#  large circle to fill display
big_circle = Circle(x0=64, y0=64, r=62, fill=0x888888)
big_splash.append(big_circle)
#  large text to fill circle
big_text = label.Label(terminalio.FONT, text='   ', color=0xFFFFFF)
big_text.x = 38
big_text.y = 60
big_text.scale = 4
big_splash.append(big_text)

selection_splash = displayio.Group()
selection_text = label.Label(terminalio.FONT, text='   ', color=0xFFFFFF)
selection_text.x = 0
selection_text.y = 60
selection_text.scale = 2
selection_splash.append(selection_text)

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

#  coordinates for navigating main GUI
select_x = [0, 32, 64, 96]
select_y = [0, 32, 64, 96]

#  y coordinate for 5-way switch navigation
y_pos = 0
#  x coordinate for 5-way switch navigation
x_pos = 0
sub_state = False
#  default midi number
midi_num = 60
#  default MIDI button
button_num = 0
#  default MIDI button position
button_pos = 0
#  check for blinking LED
led_check = None

#  time.monotonic() device
clock = time.monotonic()

clock_select_long = time.monotonic()
select_long_counter = 0

clock_button_repeat = time.monotonic_ns()
button_repeat = 0
note_selection = 0

#  coordinates for tracking location of 5-way switch
up_scroll = 0
down_scroll = 0
left_scroll = 0
right_scroll = 0
switch_coordinates = [(0, 0), (1, 0), (2, 0), (3, 0),
                    (0, 1), (1, 1), (2, 1), (3, 1),
                    (0, 2), (1, 2), (2, 2), (3, 2),
                    (0, 3), (1, 3), (2, 3), (3, 3)]

#  show main display GUI
display.show(splash)

pressed = False


while True:
    #  debouncing for 5-way switch positions
    if up.value and up_state == "pressed":
        up_state = None
        pressed = False
    if down.value and down_state == "pressed":
        down_state = None
        pressed = False
    if left.value and left_state == "pressed":
        left_state = None
        pressed = False
    if right.value and right_state == "pressed":
        right_state = None
        pressed = False
    if select.value and select_state == "pressed":
        select_state = None

    #  MIDI input
    for i in range(16):
        buttons = note_buttons[i]
        if not buttons.value and note_states[i] is False:
            #  send the MIDI note and light up the LED
            leds[i].value = True
            midi.send(NoteOn(midi_notes[i], velocity_standard))
            note_states[i] = True
        #  if the button is released...
        if buttons.value and note_states[i] is True:
            #  stop sending the MIDI note and turn off the LED
            midi.send(NoteOff(midi_notes[i], velocity_standard))
            leds[i].value = False
            note_states[i] = False

    #  if we're on the main GUI page
    if not sub_state:
        #  if you press up on the 5-way switch...
        if not up.value and up_state is None:

            up_state = "pressed"
            #  track the switch's position
            up_scroll -= 1
            if up_scroll < 0:
                up_scroll = 3
            y_pos = up_scroll
            down_scroll = up_scroll
        #  if you press down on the 5-way switch...
        if not down.value and down_state is None:

            down_state = "pressed"
            #  track the switch's position
            down_scroll += 1
            if down_scroll > 3:
                down_scroll = 0
            y_pos = down_scroll
            up_scroll = down_scroll
        #  if you press left on the 5-way switch...
        if not left.value and left_state is None:

            # print("scroll", down_scroll)
            left_state = "pressed"
            #  track the switch's position
            left_scroll -= 1
            if left_scroll < 0:
                left_scroll = 3
            x_pos = left_scroll
            right_scroll = left_scroll
        #  if you press right on the 5-way switch...
        if not right.value and right_state is None:
            # print("scroll", down_scroll)
            right_state = "pressed"
            #  track the switch's position
            right_scroll += 1
            if right_scroll > 3:
                right_scroll = 0
            x_pos = right_scroll
            left_scroll = right_scroll

        #  update square's position on the GUI
        rect.y = select_y[y_pos]
        rect.x = select_x[x_pos]

        #  update the currently highlighted button on the GUI
        for coords in switch_coordinates:
            if x_pos == coords[0] and y_pos == coords[1]:
                button_pos = switch_coordinates.index(coords)
                #  print(button_pos)
        button_num = midi_notes[button_pos]

        #  if you press select on the 5-way switch...
        if not select.value and select_state is None:
            select_state = "pressed"
            #  grab the selected button's MIDI note
            midi_num = button_num
            #  change into the secondary GUI menu
            sub_state = True

    #  if an arcade button is selected to change the MIDI note...
    if sub_state:
        #  display the secondary GUI menu
        display.show(big_splash)
        #  display the selected button's MIDI note
        big_text.text = NOTES[midi_num]

        #  blink the selected button's LED without pausing the loop

        if (time.monotonic() > (clock + 1)) and led_check is None:
            leds[button_pos].value = True
            led_check = True
            clock = time.monotonic()
        if (time.monotonic() > (clock + 1)) and led_check is True:
            leds[button_pos].value = False
            led_check = None
            clock = time.monotonic()

        if (time.monotonic() > (clock_select_long + 1)):
            if not select.value:
                #print(select_long_counter)
                select_long_counter += 1
            else:
                if select_long_counter != 0:
                    select_long_counter = 0
            clock_select_long = time.monotonic()

            # Change note if select pressed for 3 seconds
            if select_long_counter == time_before_change_notes:
                selection_text.text, note_selection, midi_notes = changes_notes(note_selection)
                display.show(selection_splash)

                # Leds show!
                for led in leds:
                    led.value = True
                    time.sleep(0.03)
                for led in leds:
                    led.value = False
                    time.sleep(0.03)

                # Reset oled interface
                select_long_counter = 0
                sub_state = False
                # Reset text on OLED
                for i in range(16):
                    text_labels[i].text = NOTES[midi_notes[i]]

                #  show main GUI display
                display.show(splash)
                #  turn off blinking LED
                leds[button_pos].value = False

        #  blocks the MIDI number from being set above 128
        if midi_num >= 128:
            midi_num = 128
        #  blocks the MIDI number from being set below 0
        if midi_num <= 0:
            midi_num = 0

        #  if you press right on the 5-way switch...
        if not right.value and right_state is None:
            #  increase the MIDI number
            midi_num += 1
            right_state = "pressed"
        #  if you press up on the 5-way switch...
        if not up.value and up_state is None:
            #  increase the MIDI number
            midi_num += 1
            up_state = "pressed"
        #  if you press left on the 5-way switch...
        if not left.value and left_state is None:
            #  decrease the MIDI number
            midi_num -= 1
            left_state = "pressed"
        #  if you press down on the 5-way switch...
        if not down.value and down_state is None:
            #  decrease the MIDI number
            midi_num -= 1
            down_state = "pressed"

        #  update arcade button's MIDI note
        #  allows you to check note while you're adjusting it
        midi_notes[button_pos] = midi_num

        #  if you press select on the 5-way switch...
        if not select.value and select_state is None:
            print(midi_notes)
            select_state = "pressed"
            #  change back to main menu mode
            sub_state = False
            #  update new MIDI number text label
            text_labels[button_pos].text = NOTES[midi_num]
            #  show main GUI display
            display.show(splash)
            #  turn off blinking LED
            leds[button_pos].value = False
