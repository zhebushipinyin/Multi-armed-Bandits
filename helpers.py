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


def get_stars(points, scores):
    base = scores[:5].mean()*5
    v_max = scores[5:].max(axis=1).sum()+base
    v_min = scores[5:].min(axis=1).sum()+base
    v_random = scores.mean()*len(scores)-30
    p = np.clip((points-v_random)/(v_max-v_random),0, 1)
    if points<=v_random:
        return  np.round(1*((points-v_min)/(v_random-v_min))**0.7)
    else:
        return np.round(4*p+1)


def generate_(mu, std, drift, reward, exp):
    trial=len(mu[0][0])
    n_arms=len(mu[0])
    dfs = []
    dic = [[0,1,2]+[each]*2 for each in range(3)]+[[0]*3+[1]*2]+[[1]*3+[2]*2]+[[2]*3+[0]*2]
    dic+=dic
    list(map(np.random.shuffle, dic))
    np.random.shuffle(dic)
    for i in range(len(exp)):
        payoff_mean = mu[i]
        payoff_std = std[i]
        drift_i = drift[i][0][0]
        payoff = reward[i]
        df = pd.DataFrame()
        df['trial']=range(trial)
        pos = np.repeat([['L', 'M', 'R']], trial, axis=0)
        list(map(np.random.shuffle, pos))
        s = np.arange(n_arms)
        np.random.shuffle(s)
        for j in range(n_arms):
            df['arm%s_mean'%j] = payoff_mean[s[j]]
            df['arm%s_std'%j] = payoff_std[s[j]]
            df['arm%s_payoff'%j] = payoff[s[j]]
            df['arm%s_pos'%j] = pos[:, s[j]]
        df['drift'] = drift_i
        df['exp'] = exp[i]
        df['force_arm'] = list(dic[i])+[None]*(trial-5)
        df['arm'] = list(dic[i]) + [-1] * (trial - 5)
        dfs.append(df)
    dfs = pd.concat(dfs)
    dfs.index = range(len(dfs))
    dfs['block'] = dfs.index.values//trial
    return dfs


def generate(rng):
    mu0 = np.repeat([[10], [0], [-10]], 22, axis=1)
    mu1 = np.concatenate((
        np.concatenate((np.array([10]*8), np.round(np.linspace(10, -10, 14)))).reshape(1, -1),
        np.repeat([[0], [-10]], 22, axis=1)
    ))
    mu2 = np.concatenate((np.repeat([[10], [0], [-10]], 11, axis=1), np.repeat([[-6], [0], [-10]], 11, axis=1)), axis=1)
    mu3 = np.concatenate((np.repeat([[10], [0], [-10]], 11, axis=1), np.repeat([[10], [16], [-10]], 11, axis=1)), axis=1)
    mus = np.concatenate([mu0, mu1, mu2, mu3]).reshape(4, 3, -1)
    mu = np.repeat(mus, 3, axis=0)
    drift = np.tile([-10, 0, 10], 4).reshape(len(mu), 1, 1)
    std = 4*np.ones(mu.shape)
    index = np.arange(len(mu))
    reward = rng.normal(mu+drift, std).astype('int')
    exp = np.repeat([1,2,3,4], 3)
    np.random.shuffle(index)
    while (exp[index[0]]!=1)|(exp[index[1]]!=4)|(drift[index[0]][0][0]!=0)|(exp[index[2]]==4):
        np.random.shuffle(index)
    return generate_(mu[index], std[index], drift[index], reward[index], exp[index])


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
