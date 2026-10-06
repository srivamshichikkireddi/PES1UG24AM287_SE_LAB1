import pygame
import random
from .hole import Hole
from .sound import SoundManager

# Game Engine

DARK_BROWN = (60, 40, 20)
MOLE_BROWN = (140, 95, 55)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)

# name -> (spawn_chance per hole per frame, frames a mole stays up)
DIFFICULTIES = {
    "Easy":   (0.012, 70),
    "Medium": (0.020, 45),
    "Hard":   (0.035, 28),
}


class GameEngine:
    def __init__(self, width, height, rows=3, cols=3):
        self.width = width
        self.height = height

        self.holes = []
        spacing_x = width // (cols + 1)
        spacing_y = (height - 80) // (rows + 1)
        for r in range(rows):
            for c in range(cols):
                cx = spacing_x * (c + 1)
                cy = 80 + spacing_y * (r + 1)
                self.holes.append(Hole(cx, cy))

        self.sound = SoundManager()
        self.round_seconds = 30
        self.difficulty = "Medium"
        self.menu_open = False      # True while choosing a difficulty
        self._build_menu_buttons()
        self.start_round(self.difficulty)
        self.font = pygame.font.SysFont("Arial", 28)
        self.big_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.should_quit = False   # main loop exits when this becomes True

    def _build_menu_buttons(self):
        w, h = 220, 50
        x = self.width // 2 - w // 2
        self.menu_buttons = {}
        for i, name in enumerate(DIFFICULTIES):
            self.menu_buttons[name] = pygame.Rect(x, 215 + i * 65, w, h)
        self.exit_button = pygame.Rect(x, 215 + len(DIFFICULTIES) * 65 + 15, w, h)

    def start_round(self, difficulty):
        """(Re)start a round with the chosen difficulty."""
        self.difficulty = difficulty
        self.spawn_chance, self.mole_up_frames = DIFFICULTIES[difficulty]
        self.time_left_frames = self.round_seconds * 60
        self.score = 0
        self.misses = 0
        self.game_over = False
        self.menu_open = False
        for hole in self.holes:
            hole.active = False
            hole.timer = 0

    def handle_event(self, event):
        if self.game_over:
            self._handle_game_over_event(event)
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    def _handle_game_over_event(self, event):
        if self.menu_open:
            self._handle_menu_event(event)
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                self.menu_open = True          # go to difficulty selection
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.should_quit = True

    def _handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            keys = {pygame.K_1: "Easy", pygame.K_2: "Medium", pygame.K_3: "Hard"}
            if event.key in keys:
                self.start_round(keys[event.key])
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.should_quit = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in self.menu_buttons.items():
                if rect.collidepoint(event.pos):
                    self.start_round(name)
                    return
            if self.exit_button.collidepoint(event.pos):
                self.should_quit = True

    def _handle_click(self, pos):
        # Task 1 fix: one click can whack at most ONE hole.
        # Hit areas are circles that match the drawn holes (radius 40),
        # which never overlap because the grid spacing is > 2 * radius.
        # As a safety net, if several areas ever did contain the click,
        # only the closest hole is considered.
        candidates = [h for h in self.holes if h.contains(pos)]
        target = min(candidates, key=lambda h: h.distance_to(pos), default=None)

        if target is not None and target.whack():
            self.score += 1
            self.sound.play("whack")
        else:
            self.misses += 1
            self.sound.play("miss")

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        self.time_left_frames -= 1
        if self.time_left_frames <= 0:
            self.game_over = True
            self.sound.play("gameover")
            return

        for hole in self.holes:
            hole.update()
            if not hole.active and random.random() < self.spawn_chance:
                hole.pop_up(self.mole_up_frames)

    def render(self, screen):
        for hole in self.holes:
            pygame.draw.circle(screen, DARK_BROWN, (hole.center_x, hole.center_y), hole.radius)
            if hole.active:
                pygame.draw.circle(screen, MOLE_BROWN, (hole.center_x, hole.center_y), 32)

        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        seconds_left = max(0, self.time_left_frames // 60)
        timer_text = self.font.render(f"Time: {seconds_left}s", True, BLACK)
        screen.blit(timer_text, (self.width - 140, 10))

        mode_text = self.small_font.render(self.difficulty, True, BLACK)
        screen.blit(mode_text, mode_text.get_rect(midtop=(self.width // 2, 18)))

        if self.game_over:
            self._render_game_over(screen)

    def _draw_centered(self, screen, font, text, y, color):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(self.width // 2, y)))

    def _render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        if self.menu_open:
            self._render_menu(screen)
            return

        self._draw_centered(screen, self.big_font, "TIME'S UP!", 170, WHITE)
        self._draw_centered(screen, self.font, f"Final Score: {self.score}", 250, GOLD)
        self._draw_centered(screen, self.font, f"Missed Clicks: {self.misses}", 295, WHITE)
        self._draw_centered(screen, self.font, "Press R to play again", 380, WHITE)
        self._draw_centered(screen, self.font, "Press ESC or Q to exit", 425, WHITE)

    def _render_menu(self, screen):
        self._draw_centered(screen, self.big_font, "Play Again?", 130, WHITE)
        self._draw_centered(screen, self.font, "Choose difficulty (click or press 1/2/3)", 180, GOLD)
        mouse = pygame.mouse.get_pos()
        for i, (name, rect) in enumerate(self.menu_buttons.items(), start=1):
            self._draw_button(screen, rect, f"{i}. {name}", mouse)
        self._draw_button(screen, self.exit_button, "Exit", mouse)

    def _draw_button(self, screen, rect, label, mouse):
        color = (90, 140, 70) if rect.collidepoint(mouse) else (60, 100, 45)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=8)
        self._draw_centered(screen, self.font, label, rect.centery, WHITE)
