import tkinter as tk
import csv
import os.path

HEADER = ["sid", "trial", "freq1", "amp1", "dur1", "ramp1", "freq2", "amp2", "dur2", "ramp2", "remote1", "remote2", "more_localized"]

INSTRUCTIONS = "Use the buttons below to play each buzz and submit your responses.\nYou must play each buzz at least once to proceed.\nRemember to keep your hand in the correct pose."
N_ROWS = 3
N_COLS = 3
DEFAULT_PREF = '-1'

haptic_signal_1 = {"freq": 0, "amp": 0, "dur": 0, "ramp": 0}
haptic_signal_2 = {"freq": 0, "amp": 0, "dur": 0, "ramp": 0}

RADIO_VALUES = {"Buzz 1 is more localized; Buzz 2 is more diffuse." : "1",
                "Buzz 2 is more localized; Buzz 1 is more diffuse." : "2",
                }

class Experiment():
    def __init__(self, instructions, n_rows, n_cols, default_pref, header, radio_values):
        self.instructions = instructions
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.default_pref = default_pref
        self.header = header
        self.radio_values = radio_values
        self.trial = 1

        self.create_data_file()
        self.init_tk()
        self.root.lift()
        self.root.attributes("-topmost", True)


    def init_tk(self):
        self.root = tk.Tk()
        for r in range(self.n_rows):
            self.root.rowconfigure(r, weight=1, minsize=50)
        for c in range(self.n_cols):
            self.root.columnconfigure(r, weight=1, minsize=50)

        self.frames = {i:{} for i in range(self.n_rows)}
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                frame = tk.Frame(master=self.root)
                frame.grid(row=r, column=c, padx=25, pady=5)
                self.frames[r][c] = frame

        self.lbl_trial = tk.Label(text=f"Trial: {self.trial}", master=self.frames[0][0])
        self.lbl_trial.pack()

        lbl_intructions = tk.Label(text=self.instructions, master=self.frames[0][1])
        lbl_intructions.pack()

        btn_buzz1 = tk.Button(text="Play Buzz 1", master=self.frames[1][0], command=lambda: self.press_btn(1))
        btn_buzz1.pack()

        btn_buzz2 = tk.Button(text="Play Buzz 2", master=self.frames[1][2], command=lambda: self.press_btn(2))
        btn_buzz2.pack()

        self.buttons = {1: btn_buzz1, 2: btn_buzz2}
        self.pressed_btns = {1: False, 2: False}


        self.var_remote1 = tk.IntVar()
        self.chk_remote1 = tk.Checkbutton(text="Buzz 1 is Remote", variable=self.var_remote1, master=self.frames[1][0],
                                    onvalue=1, offvalue=0, state="disabled", command=self.press_chk)
        self.chk_remote1.pack()

        self.var_remote2 = tk.IntVar()
        self.chk_remote2 = tk.Checkbutton(text="Buzz 2 is Remote", variable=self.var_remote2, master=self.frames[1][2],
                                    onvalue=1, offvalue=0, state="disabled", command=self.press_chk)
        self.chk_remote2.pack()

        self.checks = {1: self.chk_remote1, 2: self.chk_remote2}
        self.remote_signals = {1: self.var_remote1, 2: self.var_remote2}


        self.var_pref = tk.StringVar()
        self.var_pref.set(self.default_pref)

        self.radio_buttons = []
        for (text, value) in self.radio_values.items():
            rad_btn = tk.Radiobutton(master=self.frames[1][1], text = text, variable = self.var_pref, state="disabled", value = value)
            rad_btn.pack(side=tk.LEFT)
            self.radio_buttons.append(rad_btn)


        self.btn_submit = tk.Button(text="Submit", master=self.frames[2][1], command=self.submit, state="disabled")
        self.btn_submit.pack()


    def create_data_file(self):
        while True:
            self.sid = input("Enter participant ID: ")
            self.data_file = f"{self.sid}.csv"
            if os.path.isfile(self.data_file):
                print(f"{self.data_file} already exists! Choose a different ID!")
            else:
                break
            
        with open(self.data_file, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow(self.header)


    def play_haptics(self, i):
        if i == 1:
            print(haptic_signal_1)

        if i == 2:
            print(haptic_signal_2)


    def stop_haptics(self):
        print("Stopping Haptics")


    def press_btn(self, i):
        self.checks[i]["state"] = "normal"
        self.pressed_btns[i] = True
        for b in self.buttons:
            btn = self.buttons[b]
            if b == i:
                if "Play" in btn['text']:
                    btn['text'] = f"Stop Buzz {i}"
                    self.play_haptics(i)
                else:
                    btn['text'] = f"Play Buzz {i}"
                    self.stop_haptics()
            else:
                btn['text'] = f"Play Buzz {b}"


    def press_chk(self):
        for j in self.remote_signals:
            if not self.remote_signals[j].get():
                for rdbtn in self.radio_buttons:
                    rdbtn["state"] = "disabled"
                return
        for rdbtn in self.radio_buttons:
            rdbtn["state"] = "normal"


    def check_can_submit(self):
        self.root.after(1, self.check_can_submit)
        if not all(self.pressed_btns.values()):
            self.btn_submit["state"] = "disabled"
            return

        else:
            all_remote = True
            for j in self.remote_signals:
                if not self.remote_signals[j].get():
                    all_remote = False
                    break

            if not all_remote:
                self.btn_submit["state"] = "normal"
            
            else:
                if self.var_pref.get() != self.default_pref:
                    self.btn_submit["state"] = "normal"

                else:
                    self.btn_submit["state"] = "disabled"
        

    def reset(self):
        self.var_pref.set(self.default_pref)
        self.var_remote1.set(0)
        self.var_remote2.set(0)

        self.chk_remote1['state'] = "disabled"
        self.chk_remote2['state'] = "disabled"

        self.btn_submit["state"] = "disabled"
        for rdbtn in self.radio_buttons:
            rdbtn["state"] = "disabled"
        for btn in self.pressed_btns:
            self.pressed_btns[btn] = False


    def get_next_signals(self):
        for par in haptic_signal_1:
            haptic_signal_1[par] += 1

        for par in haptic_signal_2:
            haptic_signal_2[par] -= 1


    def write_row(self):
        data = [self.sid, self.trial]
        data += [haptic_signal_1["freq"], haptic_signal_1["amp"], haptic_signal_1["dur"], haptic_signal_1["ramp"]]
        data += [haptic_signal_2["freq"], haptic_signal_2["amp"], haptic_signal_2["dur"], haptic_signal_2["ramp"]]
        data += [self.var_remote1.get(), self.var_remote2.get(), self.var_pref.get()]

        with open(self.data_file, 'a', newline='') as csvfile:
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow(data)
            

    def update_trial(self):
        self.trial += 1
        self.lbl_trial["text"] = f"Trial: {self.trial}"


    def submit(self):
        self.write_row()
        self.reset()
        self.get_next_signals()
        self.update_trial()
    

    def run(self):
        self.get_next_signals()
        self.root.after(1, self.check_can_submit)
        self.root.mainloop()


exp = Experiment(INSTRUCTIONS, N_ROWS, N_COLS, DEFAULT_PREF, HEADER, RADIO_VALUES)
exp.run()
