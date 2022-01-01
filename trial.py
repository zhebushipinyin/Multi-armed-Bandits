from psychopy import visual, event, core
import numpy as np
import helpers as hp
import time


def trial(i, win, df, pic, pos, myMouse, clk, hand):
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
    pic: list
        image
    pos: dict
    myMouse: event.Mouse
        mouse
    clk:
        clock
    hand:
        hand image
    Returns
    -------
    result : list
    """
    n = len(pic)
    arm_pos = [df.loc[i, 'arm%s_pos'%j] for j in range(3)]
    for j, each in enumerate(pic):
        each.set_pos(pos[arm_pos[j]][0], pos[arm_pos[j]][1])
        each.draw()
    result = {
    }
    click = 0
    state = 'run'
    clk.reset()
    while True:
        if state == 'run':
            for j in range(n):
                pic[j].draw()
                if myMouse.isPressedIn(pic[j].pic0):
                    click = j
                    mean, std = df.loc[i, ['arm%s_mean'%j, 'arm%s_std'%j]].values
                    result['arm'] = j
                    result['arm_pos'] = arm_pos[j]
                    reward = np.round(np.random.normal(mean, std))
                    result['reward'] = reward
                    state = 'feedback'
                    result['rt'] = clk.getTime()
                    clk.reset()
            hand.pos = myMouse.getPos()
            hand.draw()
            win.flip()
        elif state == 'feedback':
            for j in range(3):
                if j != click:
                    pic[j].draw()
                else:
                    pic[j].draw(choose=True, reward='?')
            hand.pos = myMouse.getPos()
            hand.draw()
            win.flip()
            if clk.getTime()>0.5:
                state = 'quit'
        else:
            break
    return result


def trial_(i, win, df, slots, pos, clk, sound, slots_point):
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
    state = 'run'
    clk.reset()
    while True:
        if state == 'run':
            for each in slots:
                each.draw()
            slots_point.draw()
            #slots_gain.draw(slots_gain.points)
            win.flip()
            key = event.waitKeys(keyList=['left', 'up', 'right', 'q'])
            if 'left' in key:
                click = 'L'
            elif 'up' in key:
                click = 'M'
            elif 'right' in key:
                click = 'R'
            else:
                win.close()
                core.quit()
            sound[0].play()
            w_click = np.where(arm_pos==click)[0][0]
            mean, std = df.loc[i, ['arm%s_mean'%w_click, 'arm%s_std'%w_click]].values
            result['arm'] = w_click
            result['arm_pos'] = arm_pos[w_click]
            reward = int(np.random.normal(mean, std))
            result['reward'] = reward
            result['rt'] = clk.getTime()
            clk.reset()
            state = 'draw'
        elif state == 'draw':
            for k in range(10):
                for j in range(3):
                    if j != w_click:
                        slots[j].draw(digit=None)
                    else:
                        slots[j].draw(digit=hp.num2list(np.random.randint(-99, 99)))
                time.sleep(0.1)
                slots_point.draw()
                #slots_gain.draw(slots_gain.points)
                win.flip()
            state = 'feedback'
            clk.reset()
            sound[0].stop()

        elif state == 'feedback':
            for j in range(3):
                if j != w_click:
                    slots[j].draw()
                else:
                    slots[j].draw(digit=hp.num2list(reward))
            slots_point.draw(reward)
            #slots_gain.draw(reward)
            win.flip()
            sound[1].play()
            core.wait(1.2)
            sound[1].stop()
            state = 'quit'
        else:
            break
    return result
