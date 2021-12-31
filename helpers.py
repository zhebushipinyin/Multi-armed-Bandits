import numpy as np
import pandas as pd
from psychopy import visual


def num2list(x, max_len=3):
    if max_len>0:
        if x>=0:
            s = list(map(int, str(x)))
            return [0]*(max_len-len(s))+s
        else:
            s = list(map(int, str(-x)))
            return [-1]+[0]*(max_len-1-len(s)) + s
    else:
        if x>=0:
            return list(map(int, str(x)))
        else:
            s = list(map(int, str(-x)))
            return [-1]+s


def generate(payoff_dists,trial=24
             ):
    """
    Generate exp data.
    Returns the DataFrame contains the stimulus

    Parameters
    ----------
    payoff_dists : list of 2-tuples of length `K`
                The parameters the distributions over payoff values for each of the
                `n` arms. Specifically, ``payoffs[k]`` is a tuple of (mean, std)
                for the Gaussian distribution over payoffs associated with arm `k`.
    trial : int
        number of trials per condition
    Returns
    -------
    df : pd.DataFrame
    """
    n_arms = len(payoff_dists)
    arm_evs = np.array([mu for (mu, std) in payoff_dists])
    arm_std = np.array([std for (mu, std) in payoff_dists])
    best_ev = np.max(arm_evs)
    best_arm = np.argmax(arm_evs)
    df = pd.DataFrame()
    df['n_arms'] = [n_arms]*trial
    pos = np.repeat([['L', 'M', 'R']], trial, axis=0)
    list(map(np.random.shuffle, pos))
    for i in range(n_arms):
        df['arm%s_mean'%i] = [arm_evs[i]]*trial
        df['arm%s_std'%i] = [arm_std[i]]*trial
        df['arm%s_pos'%i] = pos[:, i]
    return df


class Bandit:
    def __init__(self, pic0, pic1, text, units=1, size=300):
        self.pic0 = pic0
        self.pic1 = pic1
        self.text = text
        self.units = units
        self.size = size
        self.pic0.size = size*units
        self.pic1.size = size*units

    def set_pos(self, x, y):
        self.pic0.pos = (x*self.units, y*self.units)
        self.pic1.pos = (x*self.units, y*self.units)
        self.text.pos = ((x-50)*self.units, y*self.units)

    def draw(self, choose=False, reward=0):
        if not choose:
            self.pic0.draw()
            self.text.text = '?'
        else:
            self.pic1.draw()
            self.text.text = reward
            #self.text.text = "{:.0f}".format(reward)
        self.text.draw()


class Slots:
    def __init__(self, win, assets, units=1, ind=0, px=0, py=0):
        self.units = units
        self.px = px
        self.py = py
        self.slots = visual.ImageStim(win, image=assets['slot'][ind], pos=(px*units, py*units), size=(300*units, 300*units))
        #self.button = visual.ImageStim(win, image=assets['button'], pos=(px*units, (py-90)*units))
        self.digit = []
        assert len(assets['digit'])==10
        for i, each in enumerate(assets['digit']):
            self.digit.append(visual.ImageStim(win, image=assets['digit'][i], size=(80*units, 111*units)))
        self.null = visual.ImageStim(win, image=assets['null'], size=(80*units, 111*units))
        self.digit_n = visual.ImageStim(win, image=assets['digit-'], size=(80*units, 111*units))

    def set_pos(self, pos):
        self.px = pos[0]
        self.py = pos[1]
        self.slots.pos = (self.px*self.units, self.py*self.units)

    def draw(self, digit=None):
        self.slots.draw()
        if digit is None:
            for i in range(3):
                self.null.pos = ((self.px-80+i*80)*self.units, (self.py+50)*self.units)
                self.null.draw()
        elif digit[0]<0:
            self.digit_n.pos = ((self.px-80)*self.units, (self.py+50)*self.units)
            self.digit_n.draw()
            for i in range(2):
                d = digit[i+1]
                self.digit[d].pos = ((self.px+80*i)*self.units, (self.py+50)*self.units)
                self.digit[d].draw()
        else:
            for i in range(3):
                d = digit[i]
                self.digit[d].pos = ((self.px-80+80*i)*self.units, (self.py+50)*self.units)
                self.digit[d].draw()


class PointTotal:
    def __init__(self, win, assets, units=1, points=0, px=440, py=245):
        self.units = units
        self.px = px
        self.py = py
        self.points = points
        self.total = visual.ImageStim(win, image=assets['total'], pos=(px*units, py*units),
                                      size=(220*units, 48*units))
        self.digit = []
        for i, each in enumerate(assets['digit']):
            self.digit.append(visual.ImageStim(win, image=assets['digit'][i], size=(24*units, 33.4*units)))
        self.null = visual.ImageStim(win, image=assets['null'], size=(24*units, 33.4*units))
        self.digit_n = visual.ImageStim(win, image=assets['digit-'], size=(24*units, 33.4*units))

    def set_pos(self, pos):
        self.px = pos[0]
        self.py = pos[1]
        self.total.pos = (self.px*self.units, self.py*self.units)

    def draw(self, number=0):
        self.points += number
        self.total.draw()
        digit = num2list(self.points, 0)[::-1]
        for i, each in enumerate(digit):
            if each <0:
                self.digit_n.pos = ((self.px+35-24*(i-2))*self.units, self.py*self.units)
                self.digit_n.draw()
            else:
                self.digit[each].pos = ((self.px+35-24*(i-2))*self.units, self.py*self.units)
                self.digit[each].draw()


class PointWin:
    def __init__(self, win, assets, units=1, points=0, px=-140, py=-215):
        self.units = units
        self.px = px
        self.py = py
        self.points = points
        self.total = visual.ImageStim(win, image=assets['win'], pos=(px*units, py*units),
                                      size=(160*units, 130*units))
        self.digit = []
        for i, each in enumerate(assets['digit']):
            self.digit.append(visual.ImageStim(win, image=assets['digit'][i], size=(40*units, 55.5*units)))
        self.null = visual.ImageStim(win, image=assets['null'], size=(40*units, 55.5*units))
        self.digit_n = visual.ImageStim(win, image=assets['digit-'], size=(40*units, 55.5*units))

    def set_pos(self, pos):
        self.px = pos[0]
        self.py = pos[1]
        self.total.pos = (self.px*self.units, self.py*self.units)

    def draw(self, number=0):
        self.points = number
        self.total.draw()
        digit = num2list(self.points, 0)[::-1]
        for i, each in enumerate(digit):
            if each <0:
                self.digit_n.pos = ((self.px-40*(i-1)) * self.units, (self.py-25) * self.units)
                self.digit_n.draw()
            else:
                self.digit[each].pos = ((self.px-40*(i-1)) * self.units, (self.py-25) * self.units)
                self.digit[each].draw()

