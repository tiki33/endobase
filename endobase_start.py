# Outline of program to replace anaesthetist in endobase


import pyautogui as pya
import pyperclip
import time

ANAESTHETISTS = {'tt': 'Dr T Thompson',
                     'sv': 'Dr S Vuong',
                     'cb': 'Dr C Brown',
                     'jr': 'Dr J Riley',
                     'js': 'Dr J Stevens',
                     'db': 'Dr D Bowring',
                     'gos': "Dr G O'Sullivan",
                     'jt': 'Dr J Tester',
                     'rw': 'Dr Rebecca Wood',
                     'mm': 'Dr M Moyle',
                     'mon': "Dr Martine O'Neill",
                     'ni': 'Dr N Ignatenko',
                     'ns': 'Dr N Steele',
                     'tr': 'Dr Timothy Robertson',
                     'ms': 'Dr M Stone',
                     'fd': 'Dr Felicity Doherty',
                     'bm': 'Dr B Manasiev',
                     'eoh': "Dr E O'Hare",
                     'locum': 'locum',
                     'jrt': 'Dr J Tillett'}


					 
def change_anaesthetist(anaesthetist):
	"""one loop of pasting new anaesthetist"""
	pya.PAUSE = 0.4
	pya.click(700, 50)
	pya.hotkey('alt', 'e')			
	pya.typewrite(['tab'] * 16)
	# pya.hotkey('ctrl','v')
	pya.typewrite(anaesthetist)
	time.sleep(2)
	#pya.typewrite(['enter'] * 6, interval=0.3)
	#time.sleep(2)
	# pya.press('enter')
	pya.typewrite(['tab'] * 7)
	pya.hotkey('alt','o')
	pya.typewrite(['enter'] * 1)
# Input anaesthetists initials


# Get anaesthetist surname from dictionary ( endobase only uses surname
anaesthetist =  'Tillett'
pyperclip.copy(anaesthetist)


# Use pyautogui to tab through to anaesthetist
for i in range(16):
	pya.press('down')
	time.sleep(1)
	change_anaesthetist(anaesthetist)

# Use pyperclip to replace anaesthetist


# Use pyautogui to exit and save


# Work out how to cycle through patients