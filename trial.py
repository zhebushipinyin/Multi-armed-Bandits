from psychopy import visual, event, core
import numpy as np
import helpers as hp
import time


def trial(i, win, df, slots, pos, clk, sound, slots_point, hand, progress):
    """
    Run a trial of given data
    Returns the values recorded

    Parameters
    ----------
    i : int
        trial number
    win : visual.Window
        windows created by psychopy
    df : pd.DataFrame
        Exp data contains gambles and conditions
    slots: list
        slots
    pos: dict
    clk:
        clock
    sound: list
    slots_point: list
    hand:
    progress:

    Returns
    -------
    result : list
    """
    n = len(slots)
    arm_pos = np.array([df.loc[i, 'arm%s_pos'%j] for j in range(3)])
    for j, each in enumerate(slots):
        each.set_pos(pos[arm_pos[j]])
        each.draw()
    result = {
    }
    click = 0
    arm = df.loc[i, 'arm']
    drift = df.loc[i, 'drift']
    if arm>=0:
        state = 'force'
        p = pos[arm_pos[arm]]
        hand.pos = ((p[0]+30)*slots[0].units, (p[1]-150)*slots[0].units)
        if arm_pos[arm]=='L':
            keylist = ['left', 'q']
        elif arm_pos[arm]=='M':
            keylist = ['up', 'q']
        else:
            keylist = ['right', 'q']
    else:
        state = 'run'
    clk.reset()
    while True:
        if state == 'run':
            progress.draw()
            for each in slots:
                each.draw()
            slots_point.draw()
            win.flip()
            key = event.waitKeys(keyList=['left', 'up', 'right', 'q'])
            sound[0].play()
            if 'left' in key:
                click = 'L'
            elif 'up' in key:
                click = 'M'
            elif 'right' in key:
                click = 'R'
            else:
                win.close()
                core.quit()

            w_click = np.where(arm_pos==click)[0][0]
            mean_, std = df.loc[i, ['arm%s_mean'%w_click, 'arm%s_std'%w_click]].values
            mean = drift+mean_
            result['arm'] = w_click
            result['arm_pos'] = arm_pos[w_click]
            # reward = int(np.random.normal(mean, std))
            reward = df.loc[i, 'arm%s_payoff'%w_click]
            result['reward'] = reward
            result['rt'] = clk.getTime()
            clk.reset()
            state = 'draw'
        elif state == 'force':
            progress.draw()
            for each in slots:
                each.draw()
            slots_point.draw()
            hand.draw()
            win.flip()
            key = event.waitKeys(keyList=keylist)
            sound[0].play()
            if 'q' in key:
                win.close()
                core.quit()

            w_click = arm
            mean_, std = df.loc[i, ['arm%s_mean'%w_click, 'arm%s_std'%w_click]].values

            mean = drift+mean_
            result['arm'] = w_click
            result['arm_pos'] = arm_pos[w_click]
            # reward = int(np.random.normal(mean, std))
            reward = df.loc[i, 'arm%s_payoff' % w_click]
            # exclude extreme results
            while abs(reward-mean)>=3*std:
                reward = int(np.random.normal(mean, std))
            result['reward'] = reward
            result['rt'] = clk.getTime()
            clk.reset()
            state = 'draw'

        elif state == 'draw':
            for k in range(5):
                for j in range(3):
                    if j != w_click:
                        slots[j].draw(digit=None)
                    else:
                        slots[j].draw(digit=hp.num2list(np.random.randint(-99, 99)))
                time.sleep(0.1)
                slots_point.draw()
                progress.draw()
                win.flip()
            state = 'feedback'
            clk.reset()
            sound[0].stop()

        elif state == 'feedback':
            progress.draw()
            for j in range(3):
                if j != w_click:
                    slots[j].draw()
                else:
                    slots[j].draw(digit=hp.num2list(reward))
            slots_point.draw(reward)
            win.flip()
            sound[1].play()
            core.wait(1.2)
            sound[1].stop()
            state = 'quit'
        else:
            break
    return result

