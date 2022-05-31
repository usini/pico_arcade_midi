# Standard velocity
velocity_standard = 120

# midi notes are defined here
# Notes are display in serial monitor when you exit the note selection
midi_notes_default = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]
midi_notes_kong = [48,49,50,51,44,45,46,47,40,41,42,43,36,37,38,39]
midi_notes_zelda = [60, 62, 64, 67, 70, 61, 63, 65, 63, 65, 66, 68, 58, 53, 60, 62]
midi_notes_melody = [64, 63, 66, 59, 61, 63, 47, 46, 44, 51, 56, 58, 40, 47, 51, 58]
midi_notes = midi_notes_default

time_before_change_notes = 2

def changes_notes(note_selection):
    if note_selection == 0:
        note_selection += 1
        text = "Kong Kit"
        midi_notes = midi_notes_kong
    elif note_selection == 1:
        note_selection += 1
        text = "Zelda"
        midi_notes = midi_notes_zelda
    elif note_selection == 2:
        text = "Melody"
        note_selection +=1
        midi_notes = midi_notes_melody
    elif note_selection == 3:
        note_selection = 0
        text = "Default"
        midi_notes = midi_notes_default
    print("----------------")
    print("Preset:", text)
    print("id:", note_selection)
    print("Midi notes: ", midi_notes)
    print("----------------")
    return text, note_selection, midi_notes


