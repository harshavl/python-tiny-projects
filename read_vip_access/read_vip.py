
import pyautogui
import pyperclip
import time
import os
import sys

print("Finding the MFC Token ")
os.startfile("C:\Program Files (x86)\Symantec\VIP Access Client\VIPUIManager.exe")
time.sleep(1)
#Get the position from the find_vip_position.py script
pyautogui.click( 1564, 739 )
token = pyperclip.paste()
print(f"MFC Token:{token}")

