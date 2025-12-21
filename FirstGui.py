import tkinter as tk

def run_code():
    label.config(text="Button Clicked!")

root = tk.Tk()
root.title("My Python GUI")
root.geometry("300x200")

btn = tk.Button(root, text="Run", command=run_code)
btn.pack(pady=20)

label = tk.Label(root, text="")
label.pack()

root.mainloop()
