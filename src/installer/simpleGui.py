# simple_gui.py

import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Simple GUI")
    label = tk.Label(root, text="Hello, GUI World!")
    label.pack()
    root.mainloop()

if __name__ == "__main__":
    main()