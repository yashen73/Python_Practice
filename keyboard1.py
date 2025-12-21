from pynput import keyboard

word = []
def on_press(key):

    try:
        word.append({key.char})
    except AttributeError:
        if key == key.backspace:
            word.pop()
        elif key == key.space:
            print(word)
            word.clear()
        else:
            print(key)



with keyboard.Listener(on_press=on_press) as listner:
    listner.join()