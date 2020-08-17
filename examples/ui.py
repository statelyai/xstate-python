#!/usr/bin/env python3

import tkinter
from xstate.machine import Machine


class ApplicationBasic():
    def __init__(self):
        self.init_ui()
        self.init_FSM()
    
    def init_FSM(self):
        # Trafic light example
        # green -> yellow -> red -> green ..
        self.fsm = Machine(
            {
                "id": "lights",
                "initial": "green",
                "states": {
                    "green": {"on": {"TIMER": "yellow"},},
                    "yellow": {"on": {"TIMER": "red"}},
                    "red": {"on": {"TIMER": "green"}},
                },
            }
        )
        
        self.state = self.fsm.initial_state
        self.update_label()
        
    def init_ui(self):
        self.fen = tkinter.Tk()
        self.label = tkinter.Label(self.fen, text="")
        self.label.pack()
        self.button = tkinter.Button(self.fen, text="TIMER", command=self.action)
        self.button.pack()
    
    def action(self):
        print("action")
        self.state = self.fsm.transition(self.state, "TIMER")
        self.update_label()
    
    def update_label(self):
        self.label["text"] = self.state.value

    def run(self):
        self.fen.mainloop()



if __name__ == "__main__":
    app = ApplicationBasic()
    app.run()