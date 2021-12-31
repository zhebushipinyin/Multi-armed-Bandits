import time
from psychopy import visual, core, event, clock, monitors, gui
from psychopy.sound import Sound
import numpy as np
import pandas as pd
import helpers as hp
import trial as tr

# GUI
myDlg = gui.Dlg(title=u"实验")
myDlg.addText(u'被试信息')
myDlg.addField('姓名:')
myDlg.addField('性别:', choices=['male', 'female'])
myDlg.addField('年龄:', 21)

myDlg.addField('屏幕分辨率:', choices=['1920*1080', '3200*1800', '1280*720', '2048*1152', '2560*1440'])
ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
if not myDlg.OK:
    core.quit()
name = ok_data[0]
sex = ok_data[1]
age = ok_data[2]
resolution = ok_data[3]

w, h = resolution.split('*')
w = int(w)
h = int(h)
a = h/720

win = visual.Window(size=(w, h), fullscr=True, units='pix')
# Text
text = visual.TextStim(win, height=200*a, pos=(0, 0), wrapWidth=10000, color='black',bold=True)
feedback = visual.TextStim(win, height=64*a, pos=(0, -100*a), wrapWidth=10000)
progress = visual.TextStim(win, height=36*a, pos=(0, -320*a), wrapWidth=10000)
# image
box_left = visual.ImageStim(win, size=720*a/3, pos=(-200*a, 0))
box_right = visual.ImageStim(win, size=720*a/3, pos=(200*a, 0))
fix = visual.ImageStim(win, image='images/fix.png', size=720*a/20)
hand = visual.ImageStim(win, image='images/hand.png')
v_sound = Sound('sound/spin1.ogg')
slots = [hp.Bandit(visual.ImageStim(win, image='images/slot%sA.png'%(i+1)),
                   visual.ImageStim(win, image='images/slot%sB.png'%(i+1)),
                   visual.TextStim(win, height=80*a, wrapWidth=10000, color='black',bold=True),
                   units=a) for i in range(3)
         ]

df = hp.generate([[-10, 4], [0, 4], [10, 4]],trial=24)

for i in range(3):
    slots[i].set_pos(1280*(i-1)/3, 90)
pos = {
    'L':(1280*(0-1)/3, 90),
    'M':(1280*(1-1)/3, 90),
    'R':(1280*(2-1)/3, 90),
}
myMouse = event.Mouse()
myMouse.setVisible(0)
state = 'run'
clk = core.Clock()
clk.reset()
for i in range(5):
    clk.reset()
    re = tr.trial(i, win, df, slots, pos, myMouse, clk, hand)
    print(re)
    win.flip()
    reward = re['reward']
    if reward>0:
        v_sound.play()
        text.color='gold'
        text.text = "+{:.0f}".format(re['reward'])
    elif reward<0:
        text.color = 'red'
        text.text = "{:.0f}".format(re['reward'])
    else:
        text.color='black'
        text.text = "{:.0f}".format(0)
    text.draw()
    win.flip()
    core.wait(2)
    v_sound.stop()

win.flip()
win.close()
core.quit()