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


def get_stars(points, vmax, vmin):
    p = np.clip(points, vmin, vmax)
    return int(np.round(5*((p-vmin)/(vmax-vmin))**0.7))


def generate_(payoff_mean, payoff_std, ban='Low', drift=0):
    """
    Generate exp data.
    Returns the DataFrame contains the stimulus

    Parameters
    ----------
    payoff_mean: np.array

    payoff_std : np.array

    ban: str

    drift: float

    Returns
    -------
    df : pd.DataFrame
    """
    assert payoff_mean.shape == payoff_std.shape
    n_arms = len(payoff_mean)
    trial = len(payoff_mean[0])
    df = pd.DataFrame()
    df['n_arms'] = [n_arms] * trial
    pos = np.repeat([['L', 'M', 'R']], trial, axis=0)
    list(map(np.random.shuffle, pos))
    s = np.arange(n_arms)
    np.random.shuffle(s)
    for i in range(n_arms):
        df['arm%s_mean' % i] = payoff_mean[s[i]]
        df['arm%s_std' % i] = payoff_std[s[i]]
        df['arm%s_pos' % i] = pos[:, s[i]]
        if payoff_mean[s[i]][0] == min(payoff_mean[:, 0]):
            i_min = i
        elif payoff_mean[s[i]][0] == max(payoff_mean[:, 0]):
            i_max = i
    df['drift'] = drift
    if ban == 'Low':
        s_ = np.repeat(s[s != i_min], 2)
        np.random.shuffle(s_)
        df['arm'] = list(s_) + [-1] * (len(df) - len(s_))
        df['ban'] = [ban] * len(s_) + [None] * (len(df) - len(s_))
        df['ban_arm'] = i_min
    elif ban == 'High':
        s_ = np.repeat(s[s != i_max], 2)
        np.random.shuffle(s_)
        df['arm'] = list(s_) + [-1] * (len(df) - len(s_))
        df['ban'] = [ban] * len(s_) + [None] * (len(df) - len(s_))
        df['ban_arm'] = i_max
    return df


def generate():
    '''
    Generate data:
    type 0, control;
    type 1, best option slowly decrease, test stickness;
    type 2, abrupt change of the best option to second best;
    type 3, abrupt change of the second best option to the best;
    '''
    mu0 = np.concatenate((
    10*np.ones((1, 20)),
    -10*np.ones((1, 20)),
    0*np.ones((1, 20))
    ))
    mu1 = np.concatenate((
        np.concatenate((np.array([10]*7), np.round(np.linspace(10, -11, 13)))).reshape(1, -1),
        -10*np.ones((1, 20)),
        0*np.ones((1, 20))
    ))
    mu2 = np.concatenate((
        np.reshape([10]*10+[-5]*10, (1, -1)),
        -10*np.ones((1, 20)),
        0*np.ones((1, 20))
    ))
    mu3 = np.concatenate((
        10*np.ones((1, 20)),
        -10*np.ones((1, 20)),
        np.reshape([0]*10+[15]*10, (1, -1)),
    ))
    mu = [mu0, mu1, mu2, mu3]
    std = 4*np.ones((3, 20))
    df = []
    HL = ['Low', 'High'] * 2
    HL_ = []
    for i in range(3):
        np.random.shuffle(HL)
        HL_ += HL
    for i, s, u in zip([0, 1, 2, 3]*3, HL_, np.repeat([-10, 0, 10], 4)):
        dfi = generate_(mu[i], std, s, u)
        dfi['type']=i
        df.append(dfi)
    np.random.shuffle(df)
    while (df[0]['type'][0]!=0)|(df[1]['type'][0]==0)|(df[0]['drift'][0]!=0):
        np.random.shuffle(df)
    df = pd.concat(df)
    df.index = range(len(df))
    df['block'] = df.index.values//len(mu0[0])
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

    def set_points(self, points=0):
        self.points = points

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
