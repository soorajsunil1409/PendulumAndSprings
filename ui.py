import pygame
from utils import *

UNSELECTED = "red"
SELECTED = "white"
BUTTONSTATES = {
    True:SELECTED,
    False:UNSELECTED
}

class UI:
    @staticmethod
    def init(app):
        UI.font = pygame.font.Font(None, 30)
        UI.sfont = pygame.font.Font(None, 20)
        UI.lfont = pygame.font.Font(None, 40)
        UI.xlfont = pygame.font.Font(None, 50)
        UI.center = (app.screen.get_size()[0]//2, app.screen.get_size()[1]//2)
        UI.half_width = app.screen.get_size()[0]//2
        UI.half_height = app.screen.get_size()[1]//2

        UI.fonts = {
            'sm':UI.sfont,
            'm':UI.font,
            'l':UI.lfont,
            'xl':UI.xlfont
        }

class Menu:
    def __init__(self, app, bg="gray") -> None:
        self.app = app
        self.bg = bg

        self.sliders = {
            "width": Slider((100, 55), (140,30), 0, 10, W_SIZE / self.app.spacing - 2),
            "height": Slider((290, 55), (140,30), 0, 2, 40),
            "space": Slider((480, 55), (140,30), 0, 2, 50),
            "spring": Slider((670, 55), (140,30), 0, 1, 4),
            "damp": Slider((100, 135), (140,30), 0, 0, 5),
        }

    def run(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()

        pygame.draw.rect(self.app.screen, (50, 50, 50), pygame.Rect(0, 0, W_SIZE, CLOTH_Y - 20))

        for type, slider in self.sliders.items():
            if slider.container_rect.collidepoint(mouse_pos):
                if mouse[0]:
                    slider.grabbed = True
            if not mouse[0]:
                slider.grabbed = False
            if slider.button_rect.collidepoint(mouse_pos):  
                slider.hover()
            if slider.grabbed:
                slider.move_slider(mouse_pos)
                if type == "width": 
                    self.app.change_xpoints(slider.get_value())
                    self.sliders["width"].max = W_SIZE / self.app.spacing - 2
                elif type == "height": self.app.change_ypoints(slider.get_value())
                elif type == "space": self.app.change_spacing(slider.get_value())
                elif type == "spring": self.app.change_spring_constant(slider.get_value())
                elif type == "damp": self.app.change_damp_constant(slider.get_value())
                slider.hover()
            else:
                slider.hovered = False
            slider.render(self.app)
            slider.display_value(self.app, type)

class Label:
    def __init__(self, font: str, content: str, pos: tuple, value = "blue", selected: bool = False) -> None:
        self.font = font
        self.selected = selected
        self.content = content

        self.value = value

        self.text = UI.fonts[self.font].render(content, True, BUTTONSTATES[self.selected], None)
        self.text_rect = self.text.get_rect(center = pos)
    def render(self, app):
        app.screen.blit(self.text, self.text_rect)

        

class Slider:
    def __init__(self, pos: tuple, size: tuple, initial_val: float, min: int, max: int) -> None:
        self.pos = pos
        self.size = size
        self.hovered = False
        self.grabbed = False

        self.slider_left_pos = self.pos[0] - (size[0]//2)
        self.slider_right_pos = self.pos[0] + (size[0]//2)
        self.slider_top_pos = self.pos[1] - (size[1]//2)

        self.min = min
        self.max = max
        self.initial_val = (self.slider_right_pos-self.slider_left_pos)*initial_val # <- percentage

        self.container_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size[0], self.size[1])
        self.button_rect = pygame.Rect(self.slider_left_pos + self.initial_val - 5, self.slider_top_pos, 10, self.size[1])

        # label
        self.text = UI.fonts['m'].render(f"Width: {int(self.get_value())}", True, "white", None)
        self.label_rect = self.text.get_rect(center = (self.pos[0], self.slider_top_pos + (self.text.get_rect()[3] // 2) + 5))
        
    def move_slider(self, mouse_pos):
        pos = mouse_pos[0]
        if pos < self.slider_left_pos:
            pos = self.slider_left_pos
        if pos > self.slider_right_pos:
            pos = self.slider_right_pos
        self.button_rect.centerx = pos
    def hover(self):
        self.hovered = True
    def render(self, app):
        pygame.draw.rect(app.screen, "darkgray", self.container_rect)
        pygame.draw.rect(app.screen, BUTTONSTATES[self.hovered], self.button_rect)
    def get_value(self):
        val_range = self.slider_right_pos - self.slider_left_pos - 1
        button_val = self.button_rect.centerx - self.slider_left_pos

        return (button_val/val_range)*(self.max-self.min)+self.min

    def get_float_value(self):
        val_range = self.slider_right_pos - self.slider_left_pos - 1
        button_val = self.button_rect.centerx - self.slider_left_pos

        return (button_val/val_range)*(self.max-self.min)+self.min

    def display_value(self, app, type):
        self.text = UI.fonts['m'].render(f"{type.capitalize()}: {self.get_value():.1f}", True, BLACK, None)
        app.screen.blit(self.text, self.label_rect)









