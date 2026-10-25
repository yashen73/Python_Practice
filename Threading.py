import threading
import time

def task(name):
    while True:
        print(f"{name}: starting....")
        time.sleep(2)
        print(f"thread finished")


thread_1 = threading.Thread(target=task, args=("A",))

thread_1.start()
print("Main thread : doing other work concurrently.")

thread_1.join()

print("main thread:  all done")