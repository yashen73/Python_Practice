import tkinter as tk

root = tk.Tk()
root.title("Hunt mouse")

label = tk.Label(root, text="Hello")
label.pack(pady=20, padx=20)


def get_input():
    user_input = entry.get()
    print("You Entered : " , user_input )

def destroy():
    root.destroy()

label1 = tk.Label(root, text="DO YOU WANT TO FORMAT YOUR HARD DISK")
label1.pack(padx=10, pady=10)


entry = tk.Entry(root, font=("sanserif", 14))
entry.pack(pady=10, padx=10)

btn = tk.Button(root, text ="Submit", command=get_input)
btn.pack(padx =0)


root.mainloop()