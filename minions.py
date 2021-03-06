import random

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.uix.widget import Widget

import champion
from shooting import Shoot


frames_per_second = 60.0
minion_size = Window.size[1] * .12

class Minions:

    minions = []

    def __init__(self, main_widget, champion_missile):
        self.main_screen = main_widget

        self.champion_missiles = champion_missile
        self.champion_bullets = champion_missile.player_bullets

        self.init_minions_list()
        self.window_sizes = Window.size

        Clock.schedule_interval(self.delete_minions, 1/60)

    def init_single_minion(self, dt):
        self.minions.insert(0, Minion(self.main_screen,
                                        self.champion_missiles,
                                        self.champion_bullets))
        print(len(self.minions))

    def init_minions_list(self):
        for i in range(0, 30):
            Clock.schedule_once(self.init_single_minion, random.random() * 60)

    def delete_minions(self, dt):
        for i, minion in enumerate(self.minions):
            x, y = minion.get_cords()
            if x > self.window_sizes[0] * 2:
                minion.remove_widget()
                self.minions.pop(i)
            if not minion.current_minion_state:
                minion.remove_widget()

    def full_minion_delete(self):
        for minion in self.minions:
            Animation.cancel_all(minion)
            minion.minion_missile.stop()
            for process in minion.process:
                process.cancel()

class Minion:
    def __init__(self, main_widget, champion_missiles, champion_bullets):

        self.window_sizes = Window.size
        self.main_screen = main_widget
        self.process = []

        self.current_minion_state = True
        self.current_minion_level = None
        self.minion_missile = Shoot(main_widget, False)
        self.init_minion()

        self.champion_missiles = champion_missiles
        self.champion_bullets = champion_bullets

        self.process.append(Clock.schedule_once(self.shot, random.random()))
        self.process.append(Clock.schedule_interval(self.shot, self.minion_missile.rate))
        Clock.schedule_interval(self.collide_champion_bullet, 1/60)

    def init_minion(self):
        self.current_minion_level = random.randint(0, 2)
        startX = - minion_size
        staticY = ((self.current_minion_level + .05) / 3 * self.window_sizes[1])
        borderX = self.window_sizes[0]

        self.this = Image(source = "assets/Minions/minion.png",
                            size = (minion_size, minion_size),
                            pos = (startX, staticY))
        self.main_screen.add_widget(self.this)

        self.animate = Animation(x = borderX * 1.2, y = staticY,t = "out_quart", duration = 20)
        self.animate2 = Animation(x = borderX * 2.2, y=staticY, t="out_quart", duration = 20)
        self.animate.start(self.this)

    def shot(self, dt):
        self.minion_missile.minion_shoot(self.this.pos, minion_size)

    def get_cords(self):
        return self.this.pos

    def collide_champion_bullet(self, dt):
        for i, bullet in enumerate(self.champion_bullets):
            if bullet.collide_widget(self.this):
                self.champion_missiles.player_destroy(i)
                self.remove_behind_border()
                self.current_minion_state = False
                champion.score += 1
                break

    def remove_widget(self):
        self.main_screen.remove_widget(self.this)

    def remove_behind_border(self):
        self.this.pos[0] = self.window_sizes[0]
        self.animate.cancel(self.this)
        self.animate2.start(self.this)
