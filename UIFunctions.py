import json
import pygame as pg

class ThemeColors:
    def __init__(self, url):
        self.colors = {}
        with open(url) as theme_colors:
            self.colors = json.load(theme_colors)
        for key in self.colors["colors"].keys():
            self.colors["colors"][key] = pg.Color((self.colors["colors"][key][0],
                                                   self.colors["colors"][key][1],
                                                   self.colors["colors"][key][2]))
    def getColor(self, color):
        try:
            return self.colors["colors"][color]
        except Exception:
            raise("Color is not within the theme colors provides")

class Button:
    def __init__(self, x, y, width, height, text):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = pg.font.SysFont("Arial", 20)
    def render(self, s):
        surface = pg.Surface((self.width, self.height))
        surface.fill(pg.Color((255, 255, 255)))
        text_surface = self.font.render(self.text, True, pg.Color((0, 0, 0)))
        surface.blit(text_surface,
                     ((self.width - text_surface.get_width())/2, (self.height - text_surface.get_height())/2))
                     
        s.blit(surface, (self.x, self.y))
    def check_hover(self, x, y):
        return x >= self.x and x <= (self.x + self.width) and y >= self.y and y <= (self.y + self.height)

class Slider:
    def __init__(self, max_val, min_val, width, height, default, x, y):
        self.handle_proportion = default
        self.min_val = min_val
        self.max_val = max_val
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.font = pg.font.SysFont("Arial", 12)
        self.isPressed = False
    def update(self, x) -> None:
        if self.isPressed:
            new_proportion = (x - self.x) / self.width
            self.handle_proportion = (0 if new_proportion < 0 else
                                      (new_proportion if new_proportion <= 1 else 1))
    def render(self, s):
        surface = pg.Surface((self.width* 1.05, self.height))
        pg.draw.rect(surface, pg.Color((255, 255, 255)),
                     pg.Rect(self.width * 0.025, self.height * (1/2 - 0.1), self.width, self.height * 0.2))
        handle = pg.Surface((self.width * 0.05, self.height))
        handle.fill(pg.Color((200, 200, 200)))
        surface.blit(handle, (self.width * (self.handle_proportion), 0))
        surface.blits(([self.font.render(str(self.min_val), True, pg.Color((255, 255, 255))),
                        (0, self.height * 0.7)],
                       [self.font.render(str(self.max_val), True, pg.Color((255, 255, 255))),
                        (self.width * 0.95, self.height * 0.7)]))
        s.blit(surface, (self.x, self.y))
    def check_hover(self, x, y):
        return ((x >= self.x + (self.width * (self.handle_proportion - 0.025))
                and x <= self.x + (self.width * (self.handle_proportion + 0.025))
                and y >= self.y and y <= (self.y + self.height)) or
                (x >= self.x and x <= (self.x + self.width * 1.05)
                 and y >= self.y + (self.height * (1/2 - 0.1))
                 and y <= self.y + (self.height * (1/2 + 0.1))))
    def get_value(self) -> float:
        return (self.handle_proportion * (self.max_val - self.min_val)) + self.min_val

class Label:
    def __init__(self, key, x, y, font_size, font, default_value):
        if type(default_value) == str:
            self.value = default_value
            self.key = key
            self.x = x
            self.y = y
            self.font_size = font_size
            self.font = pg.font.SysFont(font, self.font_size)
        else:
            raise("Given default value is not a string")
    def update_value(self, value):
        if type(value) == str:
            self.value = value
        else:
            raise("Given value is not a string")
    def render(self, s):
        s.blit(self.font.render(self.key + ": " + self.value,
                                True, pg.Color((255, 255, 255))), (self.x, self.y))