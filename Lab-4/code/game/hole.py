import math

HOLE_RADIUS = 40  # drawn radius of a hole; also used as the hit radius


class Hole:
    def __init__(self, center_x, center_y, radius=HOLE_RADIUS):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.active = False
        self.timer = 0

    def pop_up(self, duration_frames):
        self.active = True
        self.timer = duration_frames

    def update(self):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False

    def whack(self):
        was_active = self.active
        if was_active:
            self.active = False
            self.timer = 0
        return was_active

    def distance_to(self, pos):
        """Distance from a point to the centre of this hole."""
        return math.hypot(pos[0] - self.center_x, pos[1] - self.center_y)

    def contains(self, pos):
        """True if the point lies inside this hole's circular hit area."""
        return self.distance_to(pos) <= self.radius
