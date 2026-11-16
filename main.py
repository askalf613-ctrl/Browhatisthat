import math

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle, Triangle
from kivy.uix.widget import Widget

Window.clearcolor = (0.07, 0.09, 0.12, 1)


class Game(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.px = None
        self.py = None
        self.vx = 0.0          # joystick vektoru (-1..1)
        self.vy = 0.0
        self.joy_uid = None
        self.facing = 1        # 1 sag, -1 sol
        self.t = 0.0
        self.moving = False
        Clock.schedule_interval(self.update, 1 / 60.0)

    # ---------- olcek / yerlesim ----------
    @property
    def u(self):
        return min(self.width, self.height) / 100.0

    @property
    def joy_center(self):
        return (self.u * 22, self.u * 22)

    @property
    def joy_radius(self):
        return self.u * 15

    # ---------- dokunma (joystick) ----------
    def _set_vec(self, touch):
        cx, cy = self.joy_center
        dx, dy = touch.x - cx, touch.y - cy
        dist = math.hypot(dx, dy)
        r = self.joy_radius
        if dist > r:
            dx, dy = dx / dist * r, dy / dist * r
        self.vx, self.vy = dx / r, dy / r
        # kucuk olu bolge
        if math.hypot(self.vx, self.vy) < 0.12:
            self.vx = self.vy = 0.0

    def on_touch_down(self, touch):
        if self.joy_uid is None and touch.x < self.width * 0.5 and touch.y < self.height * 0.6:
            self.joy_uid = touch.uid
            self._set_vec(touch)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.uid == self.joy_uid:
            self._set_vec(touch)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.uid == self.joy_uid:
            self.joy_uid = None
            self.vx = self.vy = 0.0
            return True
        return super().on_touch_up(touch)

    # ---------- oyun mantigi ----------
    def update(self, dt):
        if self.width < 10:
            return
        u = self.u
        if self.px is None:
            self.px, self.py = self.width / 2, self.height / 2

        speed = u * 48
        self.px += self.vx * speed * dt
        self.py += self.vy * speed * dt
        r = u * 6
        self.px = max(r, min(self.width - r, self.px))
        self.py = max(r, min(self.height - r, self.py))

        self.moving = (self.vx != 0 or self.vy != 0)
        if self.vx > 0.1:
            self.facing = 1
        elif self.vx < -0.1:
            self.facing = -1
        self.t += dt * (11 if self.moving else 3)
        self.draw()

    # ---------- cizim ----------
    def draw(self):
        self.canvas.clear()
        with self.canvas:
            self.draw_floor()
            self.draw_player()
            self.draw_joystick()

    def draw_floor(self):
        w, h, u = self.width, self.height, self.u
        Color(0.11, 0.15, 0.17, 1)
        Rectangle(pos=(0, 0), size=(w, h))
        # izgara
        Color(1, 1, 1, 0.05)
        step = u * 10
        x = 0
        while x <= w:
            Line(points=[x, 0, x, h], width=1)
            x += step
        y = 0
        while y <= h:
            Line(points=[0, y, w, y], width=1)
            y += step
        # sabit dekor (tas ve ot) - sabit desenle
        for i in range(26):
            gx = ((i * 7919) % 1000) / 1000.0 * w
            gy = ((i * 6271) % 1000) / 1000.0 * h
            if i % 3 == 0:
                Color(0.2, 0.24, 0.27, 1)
                Ellipse(pos=(gx, gy), size=(u * 3.2, u * 2.2))
                Color(0.27, 0.31, 0.34, 1)
                Ellipse(pos=(gx + u * 0.4, gy + u * 0.7), size=(u * 2, u * 1.2))
            else:
                Color(0.18, 0.32, 0.2, 1)
                for k in (-1, 0, 1):
                    Line(points=[gx, gy, gx + k * u * 0.9, gy + u * 2.2], width=1.2)
        # kenar karartma
        Color(0, 0, 0, 0.25)
        Line(rectangle=(0, 0, w, h), width=u * 1.2)

    def draw_player(self):
        u = self.u
        f = self.facing
        x = self.px
        bob = math.sin(self.t) * u * (0.5 if self.moving else 0.25)
        y = self.py + bob + u * 1.5

        # golge
        Color(0, 0, 0, 0.35)
        Ellipse(pos=(x - u * 5, self.py - u * 3.4), size=(u * 10, u * 3.2))

        # bacaklar (yururken sirayla)
        swing = math.sin(self.t) * u * 1.6 if self.moving else 0
        Color(0.25, 0.2, 0.18, 1)
        RoundedRectangle(pos=(x - u * 2.6 + swing, self.py - u * 2.6), size=(u * 2, u * 3.6), radius=[u * 0.6])
        RoundedRectangle(pos=(x + u * 0.6 - swing, self.py - u * 2.6), size=(u * 2, u * 3.6), radius=[u * 0.6])

        # pelerin (arkada)
        flap = math.sin(self.t * 0.9) * u * 0.8
        Color(0.75, 0.15, 0.2, 1)
        Triangle(points=[
            x - f * u * 2.2, y + u * 5.2,
            x - f * u * 6.2 - f * flap, y - u * 1.0,
            x - f * u * 0.8, y - u * 1.4,
        ])

        # govde (tunik)
        Color(0.2, 0.45, 0.85, 1)
        RoundedRectangle(pos=(x - u * 3.6, y), size=(u * 7.2, u * 6.2), radius=[u * 1.6])
        Color(0.9, 0.78, 0.25, 1)  # kemer
        Rectangle(pos=(x - u * 3.6, y + u * 1.6), size=(u * 7.2, u * 0.9))
        Color(0.12, 0.3, 0.6, 1)   # tunik golgesi
        Line(rounded_rectangle=(x - u * 3.6, y, u * 7.2, u * 6.2, u * 1.6), width=1.2)

        # kollar
        Color(0.95, 0.78, 0.62, 1)
        Ellipse(pos=(x - u * 5.2, y + u * 2.2), size=(u * 2, u * 2))
        Ellipse(pos=(x + u * 3.2, y + u * 2.2), size=(u * 2, u * 2))

        # kilic (on tarafta)
        sx = x + f * u * 5.2
        Color(0.85, 0.88, 0.95, 1)
        Line(points=[sx, y + u * 3.2, sx + f * u * 1.2, y + u * 9.2], width=u * 0.55)
        Color(0.9, 0.78, 0.25, 1)
        Line(points=[sx - u * 1.1, y + u * 3.6, sx + u * 1.1, y + u * 3.6], width=u * 0.4)

        # kafa
        hy = y + u * 6.2
        Color(0.95, 0.78, 0.62, 1)
        Ellipse(pos=(x - u * 3.4, hy), size=(u * 6.8, u * 6.4))

        # sac / miğfer
        Color(0.3, 0.2, 0.15, 1)
        Ellipse(pos=(x - u * 3.6, hy + u * 3.4), size=(u * 7.2, u * 3.6))
        Rectangle(pos=(x - u * 3.6, hy + u * 3.4), size=(u * 7.2, u * 0.8))

        # gozler
        ex = f * u * 0.9
        Color(1, 1, 1, 1)
        Ellipse(pos=(x - u * 2 + ex, hy + u * 2.0), size=(u * 1.7, u * 1.9))
        Ellipse(pos=(x + u * 0.4 + ex, hy + u * 2.0), size=(u * 1.7, u * 1.9))
        Color(0.05, 0.05, 0.1, 1)
        px_ = f * u * 0.35
        Ellipse(pos=(x - u * 1.6 + ex + px_, hy + u * 2.2), size=(u * 0.9, u * 1.2))
        Ellipse(pos=(x + u * 0.8 + ex + px_, hy + u * 2.2), size=(u * 0.9, u * 1.2))

        # agiz
        Color(0.6, 0.3, 0.3, 1)
        Line(points=[x - u * 0.7 + ex * 0.5, hy + u * 1.0, x + u * 0.7 + ex * 0.5, hy + u * 1.0], width=1.3)

    def draw_joystick(self):
        cx, cy = self.joy_center
        r = self.joy_radius
        u = self.u
        Color(1, 1, 1, 0.10)
        Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))
        Color(1, 1, 1, 0.30)
        Line(circle=(cx, cy, r), width=1.6)
        Color(1, 1, 1, 0.12)
        Line(circle=(cx, cy, r * 0.5), width=1.2)
        kr = r * 0.42
        kx = cx + self.vx * r
        ky = cy + self.vy * r
        Color(0.3, 0.6, 1, 0.55 if self.joy_uid is not None else 0.35)
        Ellipse(pos=(kx - kr, ky - kr), size=(kr * 2, kr * 2))
        Color(1, 1, 1, 0.5)
        Line(circle=(kx, ky, kr), width=1.5)


class CanavarApp(App):
    title = "Canavar Avcisi"

    def build(self):
        return Game()


if __name__ == "__main__":
    CanavarApp().run()
