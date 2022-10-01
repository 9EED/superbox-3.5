from random import *
from pyray import *

class Plastic:
    def __init__(self):
        self.color = Color(
            randint(30, 220),
            randint(30, 220),
            randint(30, 220),
            randint(230, 255)
        )
        self.vx = 0
        self.vy = 0
        self.gravity_effect = 1
        self.mass = .9
        self.bounce = .8
        self.liquidity = 0.5
        self.decay = 0

class Sand:
    def __init__(self):
        self.color = Color(
            randint(210, 220),
            randint(160, 175),
            randint(60, 65),
            255
        )
        self.vx = 0
        self.vy = 0
        self.gravity_effect = 1
        self.mass = 1
        self.bounce = 0.2
        self.liquidity = 0.1
        self.decay = 0

class Stone:
    def __init__(self):
        v = randint(75, 90)
        self.color = Color(
            v,
            v,
            v + randint(0, 10),
            255
        )
        self.vx = 0
        self.vy = 0
        self.gravity_effect = 0
        self.mass = 500
        self.bounce = 0.3
        self.liquidity = 0.6
        self.decay = 0

class Sky_Stone:
    def __init__(self):
            v = randint(5, 15)
            if random() > .9: v = randint(20, 25)
            self.color = Color(
                v,
                v,
                v + randint(0, 15),
                255
            )
            self.vx = 0
            self.vy = 0
            self.gravity_effect = 0
            self.mass = 100000000
            self.bounce = 1
            self.liquidity = 0
            self.decay = 0

class Water:
    def __init__(self):
        self.color = Color(
            randint(65, 70),
            randint(100, 110),
            randint(190, 200),
            200
        )
        self.vx = 0
        self.vy = 0
        self.gravity_effect = 1
        self.mass = 0.5
        self.bounce = 0.8
        self.liquidity = 1
        self.decay = 0

class Smoke:
    def __init__(self):
        v = randint( 180, 240)
        self.color = Color(
            v,
            v,
            v - randint(10 , 20),
            200
        )
        self.vx = 0
        self.vy = 0
        self.gravity_effect = -0.6
        self.mass = 0.3
        self.bounce = 0.05
        self.liquidity = .8
        self.decay = 0.2
