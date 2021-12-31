from psychopy import visual, core, event, clock, monitors, gui
from psychopy.sound import Sound
import time
import numpy as np
import helpers as hp
import trial as tr


# GUI
myDlg = gui.Dlg(title=u"实验")
myDlg.addText(u'被试信息')
myDlg.addField('姓名:')
myDlg.addField('性别:', choices=['male', 'female'])
myDlg.addField('年龄:', 21)
myDlg.addField('屏幕分辨率:', choices=['1280*720', '1920*1080', '2048*1152', '2560*1440','3200*1800'])
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
a = w/1280
df = hp.generate([[-8, 4], [0, 4], [8, 4]],trial=24)
win = visual.Window(size=(w, h), fullscr=True, units='pix')

fix = visual.ImageStim(win, image='images/fix.png', size=720*a/20)
v_sound = Sound('sound/spin1.ogg')
v_gain = Sound('sound/payout1.ogg')
# assets
assets = {
    'slot':['images/slot%s.png'%i for i in range(3)],
    'null': 'images/numbers/digitn.png',
    'digit-': 'images/numbers/digit-.png',
    'digit': ['images/numbers/digit%s.png'%i for i in range(10)],
    'total':'images/总分.png',
    'win':'images/win.png',
}
pos = {
    'L':(-400, 0),
    'M':(0, 0),
    'R':(400, 0),
}
slots = [
    hp.Slots(win, assets, units=a, ind=i) for i in range(3)
]
slots_point = hp.PointTotal(win, assets, units=a)
#slots_gain = hp.PointWin(win, assets, units=a)
clk = core.Clock()
clk.reset()

for i in range(len(df )):
    re = tr.trial_(i, win, df, slots, pos, clk, [v_sound, v_gain], slots_point)
    print(re)
    slots_point.draw()
    #slots_gain.draw(slots_gain.points)
    win.flip()
    core.wait(1)

win.close()
core.quit()
