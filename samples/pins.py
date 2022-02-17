import board
import digitalio
#  Button pins, all pins in order skipping GP15
note_pins = [board.GP7, board.GP8, board.GP9, board.GP10,
            board.GP11,board.GP12, board.GP13, board.GP14,
            board.GP20, board.GP21, board.GP22, board.GP26,
            board.GP16, board.GP17, board.GP18, board.GP19
            ]

# 5 Way Joystick Pins
select = digitalio.DigitalInOut(board.GP6)
up = digitalio.DigitalInOut(board.GP2)
down = digitalio.DigitalInOut(board.GP4)
left = digitalio.DigitalInOut(board.GP5)
right = digitalio.DigitalInOut(board.GP3)
