from tkinter import *
from PIL import Image, ImageTk
import pyautogui, colorsys, sys, math, threading, os, time, pyperclip
from pynput import keyboard, mouse

def map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def color(red, green, blue):
    red   = constrain(int(red)  , 0, 255) * 256 ** 2
    green = constrain(int(green), 0, 255) * 256
    blue  = constrain(int(blue) , 0, 255)
    return "#" + hex(red + green + blue)[2:].zfill(6)
    
def hsb(h, s, b):
    t = colorsys.hsv_to_rgb(h / 255, s / 255, b / 255)
    return color(t[0] * 255, t[1] * 255, t[2] * 255)

def dist(x1, y1, x2, y2):
	return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def mp(x1, y1, x2, y2):
	return [(x1 + x2) / 2, (y1 + y2) / 2]

def expand(c, s):
	return [c[0] - s, c[1] - s, c[2] + s, c[3] + s]

width = 500
height = 250

running = True

root = Tk()
def on_closing(*argv):
	global running
	running = False
root.protocol("WM_DELETE_WINDOW", on_closing)
root.bind("<Destroy>", on_closing)
root.title("Keyboard Overlay")
root.resizable(False, False)
LCPS, RCPS = 0, 0
centerX, centerY = width / 2, height / 2
mouseX, mouseY = pyautogui.position()
offsetX, offsetY = mouseX - centerX, mouseY - centerY
screenWidth, screenHeight = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry(f'{width}x{height}+{int(offsetX)}+{int(offsetY)}')
c = Canvas(root, bg = "#00ff00", width = width, height = height, bd = -2)

keys = {
	"up"        : [False, c.create_rectangle(width - 100, height - 100, width - 50 , height - 50), "🡅"   ],
	"down"      : [False, c.create_rectangle(width - 100, height - 50 , width - 50 , height     ), "🡇"   ],
	"left"      : [False, c.create_rectangle(width - 150, height - 50 , width - 100, height     ), "🡄"   ],
	"right"     : [False, c.create_rectangle(width - 50 , height - 50 , width      , height     ), "🡆"   ],
	"w"         : [False, c.create_rectangle(100        , height - 100, 50         , height - 50), "W"    ],
	"s"         : [False, c.create_rectangle(100        , height - 50 , 50         , height     ), "S"    ],
	"a"         : [False, c.create_rectangle(50         , height - 50 , 0          , height     ), "A"    ],
	"d"         : [False, c.create_rectangle(150        , height - 50 , 100        , height     ), "D"    ],
	"space"     : [False, c.create_rectangle(150        , height - 50 , width - 150, height     ), "Space"],
	"shift"     : [False, c.create_rectangle(0          , 0           , 100        , 50         ), "Shift"],
	"ctrl_l"    : [False, c.create_rectangle(0          , 50          , 100        , 100        ), "Ctrl" ],
	"mouseLeft" : [False, c.create_rectangle(width - 150, 0           , width - 75 , 50         ), "ML"   ],
	"mouseRight": [False, c.create_rectangle(width - 75 , 0           , width      , 50         ), "MR"   ]
}

for i in keys:
	a = keys[i]
	o = c.coords(a[1])
	mid = mp(o[0], o[1], o[2], o[3])
	c.itemconfig(a[1], outline = "white", width = 3)
	if a[2] != "":
		a.append(c.create_text(mid[0], mid[1], text = a[2], font = ("arial", 25)))

c.itemconfig(keys["mouseLeft" ][3], justify = 'center', font = ("arial", 15))
c.itemconfig(keys["mouseRight"][3], justify = 'center', font = ("arial", 15))

c.pack()

def detectKeys(key, s):
	if type(key) == keyboard.Key:
		t = str(key).split('.')[-1]
	else:
		t = chr(key.vk).lower()
	if t in keys:
		keys[t][0] = s

clickTable = [[],[]]

def detectMouse(button, s):
	global clickTable
	if button == mouse.Button.left:
		keys["mouseLeft" ][0] = s
		if s:
			clickTable[0].append(time.time())
	if button == mouse.Button.right:
		keys["mouseRight"][0] = s
		if s:
			clickTable[1].append(time.time())

def on_press(key):
	detectKeys(key, True )

def on_release(key):
	detectKeys(key, False)

def on_click(x, y, button, pressed):
	detectMouse(button, pressed)

def keyDetect():
    with keyboard.Listener(
            on_press   = on_press,
            on_release = on_release
           ) as h:
        h.join()

def mouseDetect():
    with mouse.Listener(on_click = on_click) as listener:
        listener.join()

t1 = threading.Thread(target = mouseDetect)
t2 = threading.Thread(target = keyDetect)
t1.daemon = True
t2.daemon = True
t1.start()
t2.start()

t = (1000 / 240) / 1000

while True:
	if not running:
		break
	for i in keys:
		arr = keys[i]
		c.itemconfig(arr[1], fill = ('white' if arr[0] else 'black'))
		if len(arr) > 3:
			c.itemconfig(arr[3], fill = ('black' if arr[0] else 'white'))
	c.itemconfig(keys["mouseLeft" ][3], text = f"LM\n{LCPS}")
	c.itemconfig(keys["mouseRight"][3], text = f"RM\n{RCPS}")
	root.update()
	LCPS = len(clickTable[0])
	RCPS = len(clickTable[1])
	for o in clickTable:
		for i in o:
			if time.time() > i + 1:
				o.remove(i)
	time.sleep(t)

root.destroy()
sys.exit(0)