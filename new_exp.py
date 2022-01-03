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

df = hp.generate()
win = visual.Window(size=(w, h), fullscr=True, units='pix')
text = visual.TextStim(win, height=36*a, pos=(0, 0), wrapWidth=10000, color='black',bold=True)
fix = visual.ImageStim(win, image='images/fix.png', size=720*a/20)
hand = visual.ImageStim(win, image='images/hand.png', size=100*a)
progress = visual.TextStim(win, height=32*a, pos=(0, 245*a), wrapWidth=10000, color='black')
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
    'stars': ['images/stars/star%s.png'%i for i in range(6)]
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
stars = visual.ImageStim(win, size=(690*a, 150*a))
clk = core.Clock()
clk.reset()
results = {
    'arm':[],
    'arm_pos':[],
    'reward':[],
    'rt':[]
}
blocks = np.unique(df.block)
score = 0
for block in blocks:
    len_trial = len(df.loc[df.block == block])
    slots_point.set_points(0)
    means = df.loc[df.block == block, ['arm0_mean', 'arm1_mean', 'arm2_mean']].values
    drift = df.loc[df.block == block, 'drift'].values.sum()
    vmax = means.max(axis=1).sum()+drift
    vmin = means.min(axis=1).sum()+drift
    for i_ in range(len_trial):
        i = i_+len_trial*block
        progress.text = u'第%s组: %s/%s' % (block+1, i_+1, len_trial)
        re = tr.trial(i, win, df, slots, pos, clk, [v_sound, v_gain], slots_point, hand,progress)
        print(i, re)
        results['arm'].append(re['arm'])
        results['arm_pos'].append(re['arm_pos'])
        results['reward'].append(re['reward'])
        results['rt'].append(re['rt'])
        slots_point.draw()
        progress.draw()
        win.flip()
        core.wait(0.8)
    points = slots_point.points
    star_points = hp.get_stars(points, vmax, vmin)
    score+=star_points
    print(points, vmax, vmin, star_points)
    win.flip()
    for j in range(star_points+1):
        stars.image = assets['stars'][j]
        stars.draw()
        win.flip()
        if j>0:
            v_gain.play()
            core.wait(0.4)
            v_gain.stop()
        else:
            core.wait(0.4)
    if block!=blocks[-1]:
        stars.draw()
        text.text = u'按【空格键】进入下一轮'
        text.pos = (0, -200*a)
        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])
text.text = u'实验结束, 按【空格键】退出'
text.pos = (0, 0)
text.draw()
win.flip()
print('实验得分: %s/%s'%(score, 5*len(blocks)))
event.waitKeys(keyList=['space'])
df['arm']=results['arm']
df['arm_pos']=results['arm_pos']
df['reward']=results['reward']
df['rt']=results['rt']
df['name']=name
df['age']=age
df['sex']=sex
df.to_csv('data/exp_%s_%s.csv' % (name, time.strftime("%y-%m-%d-%H-%M")))
win.close()
core.quit()
