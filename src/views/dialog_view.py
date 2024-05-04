from __future__ import annotations

from dataclasses import dataclass
from abc import abstractproperty
from os.path import abspath, join
from typing import Callable, Dict, List, Optional, Tuple, Union

import arcade

from entities.animated import AnimatedSprite, load_default_animated
from entities.player import Goto, Player


class Npc(
    AnimatedSprite,
):  # Move into entities? (requires some refactoring cause of circular imports)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 1.5

    def on_update(self, delta_time: float = 1 / 60):
        self.update_animation(delta_time)

    @abstractproperty
    def name(self) -> str: ...


class Incognito(Npc):
    def __init__(
        self, *args, player: Player, **kwargs
    ):  # TODO Only pass what's needed?
        super().__init__(*args, **kwargs)
        self.player = player

        self.player.add_goto(Goto("incognito_start", self.center_x, self.center_y))

        self.walking_textures, self.staying_textures = load_default_animated(
            abspath(join("textures", "male", "Male 17-3.png"))
        )
        self._name = "Incognito"

    @property
    def name(self) -> str:
        return self._name


@dataclass
class Tell:
    text: str
    display_image: Optional[str] = None


@dataclass
class Ask:
    question: str
    answers: List[Tuple[str, Callable]]


Character = str


@dataclass
class Dialog:
    actions: Tuple[Tuple[Character, Union[Tell, Ask]], ...]
    time_show: int = 2


INCOGNITO_START = Dialog(
    (
        ("Оболтус", Tell("Ого! Вы сейчас в игре, а это презентация по этой же игре.")),
        (
            "Оболтус",
            Tell(
                "Это же такой необычный ход, сделать презентацию по игре в ней же? Right? Right?"
            ),
        ),
        (
            "Оболтус",
            Tell(
                "Вы представляете, у нас настолько кастомизабильные диалоги, что в них можно делать презентации"
            ),
        ),
        (
            "",
            Tell(
                "И вставлять комиксы с xkcd...\nСледующий слайд, пожалуйста",
                display_image=abspath(join("textures", "comics.png")),
            ),
        ),
        (
            "Оболтус",
            Tell(
                "А в чем смысл диалогов, если у игры нет смысла? (*Рассказать про смысл игры*, да, вы это видите, где же мне еще оставлять заметки)"
            ),
        ),
        (
            "Оболтус",
            Tell(
                "Вот на все это у нас ушло 3 недели (На самом деле мы все сделали за три дня. *Рассказать про организацию процесса разработки*)"
            ),
        ),
        ("Оболтус", Tell("Кто за что отвечал?")),
        ("Оболтус", Tell("Что у нас получилось в итоге?")),
    )
)


DIALOG_TEXT_MARGIN = 10
DIALOG_FONT_SIZE = 40


class DialogView(arcade.View):
    def __init__(self, prev_view, dialog: Dialog, chars: Dict[Character, Npc]):
        super().__init__()
        self.prev_view = prev_view
        self.dialog = dialog
        self.camera = self.prev_view.camera
        self.cur_action = 0
        self.skip_next = False

    def on_draw(self):
        self.clear()
        self.prev_view.on_draw()
        self.camera.use()
        dialog_height = min(self.camera.viewport_height // 3, 400)
        arcade.draw_rectangle_filled(
            self.camera.position.x + self.camera.viewport_width // 2,
            self.camera.position.y + dialog_height // 2,
            self.camera.viewport_width,
            dialog_height,
            arcade.color.ANTI_FLASH_WHITE,
        )
        character, action = self.dialog.actions[self.cur_action]
        if isinstance(action, Tell):
            if action.display_image is not None:
                image_texture = arcade.load_texture(action.display_image)
                arcade.draw_texture_rectangle(
                    self.camera.position.x
                    + self.camera.viewport_width
                    - 10
                    - image_texture.width // 2,
                    self.camera.position.y
                    + self.camera.viewport_height
                    - image_texture.height // 2
                    - 10,
                    image_texture.width,
                    image_texture.height,
                    image_texture,
                )
            text = action.text
        else:
            text = action.question

        arcade.draw_text(
            f"{character}: {text}",
            self.camera.position.x + DIALOG_TEXT_MARGIN,
            self.camera.position.y + dialog_height - DIALOG_TEXT_MARGIN,
            color=arcade.color.BLACK,
            font_size=DIALOG_FONT_SIZE,
            anchor_y="top",
            multiline=True,
            width=self.camera.viewport_width - DIALOG_TEXT_MARGIN * 2,
        )

    def on_update(self, delta_time: float):
        if self.skip_next:
            self.cur_action += 1
            self.skip_next = False
            if self.cur_action >= len(self.dialog.actions):
                self.window.show_view(self.prev_view)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            self.skip_next = True
