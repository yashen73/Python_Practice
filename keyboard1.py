from pynput import keyboard
from sympy.polys.numberfields.galois_resolvents import generate_lambda_lookup

word = []
def on_press(key):

    try:
        word.append({key.char})
    except AttributeError:
        if key == key.backspace:
            if word == True:
                word.pop()
        elif key == key.space:
            if key == key.backspace:
                if key == key.backspace:
                    word.pop()
            else:
                print(word)
                word.clear()

        else:
            print(key)


with keyboard.Listener(on_press=on_press) as listner:
    listner.join()
