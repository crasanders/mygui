import tkinter as tk
import csv
import os.path

while True:
    sid = input("Enter participant ID: ")
    data_file = f"{sid}.csv"
    if os.path.isfile(data_file):
        print(f"{data_file} already exists! Choose a different ID!")
    else:
        break

header = ["sid", "trial", "freq1", "amp1", "dur1", "ramp1", "freq2", "amp2", "dur2", "ramp2", "remote1", "remote2", "more_localized"]

with open(data_file, 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile)
    spamwriter.writerow(header)

INSTRUCTIONS_TEXT = "Use the buttons below to play each buzz and submit your responses.\nYou must play each buzz at least once to proceed.\nRemember to keep your hand in the correct pose."
N_ROWS = 3
N_COLS = 3
DEFAULT_PREF = '-1'

playing_haptics = False
trial = 1
haptic_signal_1 = {"freq": 0, "amp": 0, "dur": 0, "ramp": 0}
haptic_signal_2 = {"freq": 0, "amp": 0, "dur": 0, "ramp": 0}

def play_haptics(i):
    if i == 1:
        print(haptic_signal_1)

    if i == 2:
        print(haptic_signal_2)

def stop_haptics():
    print("Stopping Haptics")

def press_btn(i):
    CHECKS[i]["state"] = "normal"
    pressed_btns[i] = True
    for b in BUTTONS:
        btn = BUTTONS[b]
        if b == i:
            if "Play" in btn['text']:
                btn['text'] = f"Stop Buzz {i}"
                play_haptics(i)
            else:
                btn['text'] = f"Play Buzz {i}"
                stop_haptics()
        else:
            btn['text'] = f"Play Buzz {b}"

def press_chk():
    for j in remote_signals:
        if not remote_signals[j].get():
            for rdbtn in RADIO_BUTTONS:
                rdbtn["state"] = "disabled"
            return
    for rdbtn in RADIO_BUTTONS:
        rdbtn["state"] = "normal"

def check_can_submit():
    window.after(1, check_can_submit)
    if not all(pressed_btns.values()):
        btn_submit["state"] = "disabled"
        return

    else:
        all_remote = True
        for j in remote_signals:
            if not remote_signals[j].get():
                all_remote = False
                break

        if not all_remote:
            btn_submit["state"] = "normal"
        
        else:
            if var_pref.get() != DEFAULT_PREF:
                btn_submit["state"] = "normal"

            else:
                btn_submit["state"] = "disabled"
    
def reset():
    var_pref.set(DEFAULT_PREF)
    var_remote1.set(0)
    var_remote2.set(0)

    chk_remote1['state'] = "disabled"
    chk_remote2['state'] = "disabled"

    btn_submit["state"] = "disabled"
    for rdbtn in RADIO_BUTTONS:
        rdbtn["state"] = "disabled"
    for btn in pressed_btns:
        pressed_btns[btn] = False


def get_next_signals():
    for par in haptic_signal_1:
        haptic_signal_1[par] += 1

    for par in haptic_signal_2:
        haptic_signal_2[par] -= 1


def write_row():
    data = [sid, trial]
    data += [haptic_signal_1["freq"], haptic_signal_1["amp"], haptic_signal_1["dur"], haptic_signal_1["ramp"]]
    data += [haptic_signal_2["freq"], haptic_signal_2["amp"], haptic_signal_2["dur"], haptic_signal_2["ramp"]]
    data += [var_remote1.get(), var_remote2.get(), var_pref.get()]

    with open(data_file, 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(data)
        

def submit():
    write_row()
    reset()
    get_next_signals()
    global trial
    trial += 1
    

window = tk.Tk()
for r in range(N_ROWS):
    window.rowconfigure(r, weight=1, minsize=50)
for c in range(N_COLS):
    window.columnconfigure(r, weight=1, minsize=50)

FRAMES = {i:{} for i in range(N_ROWS)}
for r in range(N_ROWS):
    for c in range(N_COLS):
        frame = tk.Frame(master=window)
        frame.grid(row=r, column=c, padx=25, pady=5)
        FRAMES[r][c] = frame

lbl_intructions = tk.Label(text=INSTRUCTIONS_TEXT, master=FRAMES[0][1]).pack()

btn_buzz1 = tk.Button(text="Play Buzz 1", master=FRAMES[1][0], command=lambda: press_btn(1))
btn_buzz1.pack()

btn_buzz2 = tk.Button(text="Play Buzz 2", master=FRAMES[1][2], command=lambda: press_btn(2))
btn_buzz2.pack()

BUTTONS = {1: btn_buzz1, 2: btn_buzz2}
pressed_btns = {1: False, 2: False}


var_remote1 = tk.IntVar()
chk_remote1 = tk.Checkbutton(text="Buzz 1 is Remote", variable=var_remote1, master=FRAMES[1][0],
                             onvalue=1, offvalue=0, state="disabled", command=press_chk)
chk_remote1.pack()

var_remote2 = tk.IntVar()
chk_remote2 = tk.Checkbutton(text="Buzz 2 is Remote", variable=var_remote2, master=FRAMES[1][2],
                             onvalue=1, offvalue=0, state="disabled", command=press_chk)
chk_remote2.pack()

CHECKS = {1: chk_remote1, 2: chk_remote2}
remote_signals = {1: var_remote1, 2: var_remote2}


var_pref = tk.StringVar()
var_pref.set(DEFAULT_PREF)
values = {"Buzz 1 is more localized; Buzz 2 is more diffuse." : "1",
          "Buzz 2 is more localized; Buzz 1 is more diffuse." : "2",
        }

RADIO_BUTTONS = []
for (text, value) in values.items():
    rad_btn = tk.Radiobutton(master=FRAMES[1][1], text = text, variable = var_pref, state="disabled", value = value)
    rad_btn.pack(side=tk.LEFT)
    RADIO_BUTTONS.append(rad_btn)


btn_submit = tk.Button(text="Submit", master=FRAMES[2][1], command=submit, state="disabled")
btn_submit.pack()

get_next_signals()
window.after(1, check_can_submit)
window.mainloop()
