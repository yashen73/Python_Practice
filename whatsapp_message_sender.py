import os
import pyautogui
import time

os.system("start whatsapp:")
time.sleep(1)
os.system("taskkill /IM WhatsApp.exe /F")
time.sleep(1)
os.system("start whatsapp:")
time.sleep(1)


pyautogui.typewrite("765849600", interval=0)
time.sleep(1)
pyautogui.press('tab')
time.sleep(1)
pyautogui.press('enter')
time.sleep(1)

pyautogui.typewrite("hi, thadiyo", interval=0.1)
pyautogui.press("enter")
pyautogui.typewrite(" Mn yashenge automated bot..", interval=0.1)
pyautogui.press('enter')
pyautogui.typewrite(" ithin ithin mko wenne ? ", interval=0.1)
pyautogui.press('enter')
