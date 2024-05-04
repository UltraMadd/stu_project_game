from __future__ import annotations
from abc import abstractproperty

from dataclasses import dataclass
from os.path import abspath, join
from typing import Callable, Dict, List, Tuple, Union

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
        (
            "Incognito",
            Tell(
                "You must first prove yourself by defeating four powerful creatures, each one representing a different aspect of this world's power"
            ),
        ),
        ("You", Tell("What do you mean? I don't understand")),
        (
            "Incognito",
            Tell(
                "You will soon enough. But for now, let me tell you about the atmosphere here. It's like... it's hard to explain. The air is thick with an otherworldly energy. Every step feels like a struggle against the forces of nature"
            ),
        ),
        ("You", Tell("That sounds ominous")),
        (
            "Incognito",
            Tell(
                "Ah, yes. You'll soon see what I mean. But for now, you must focus on your task at hand. Defeat those four bosses and then we can discuss... other matters"
            ),
        ),
        ("You", Tell("What tasks? Where am I")),
        (
            "Incognito",
            Tell(
                "Patience, my friend. All will be revealed in time. For now, let's just say that this world is full of mysteries waiting to be unraveled. And you're the one who'll do it"
            ),
        ),
        ("Player", Tell("But why? Why did you choose me for this task")),
        (
            "Incognito",
            Tell(
                "Because I saw something in you... Something that makes me believe you have what it takes to unlock the secrets of this world"
            ),
        ),
        ("Player", Tell("What are those secrets?")),
        ("Incognito", Tell("Ah, my friend. You'll soon see")),
    )
)


DIALOG_TEXT_MARGIN = 10


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
        dialog_height = min(self.camera.viewport_height // 4, 300)
        arcade.draw_rectangle_filled(
            self.camera.position.x + self.camera.viewport_width // 2,
            self.camera.position.y + dialog_height // 2,
            self.camera.viewport_width,
            dialog_height,
            arcade.color.ANTI_FLASH_WHITE,
        )
        character, action = self.dialog.actions[self.cur_action]
        if isinstance(action, Tell):
            text = action.text
        else:
            text = action.question

        arcade.draw_text(
            f"{character}: {text}",
            self.camera.position.x + DIALOG_TEXT_MARGIN,
            self.camera.position.y + dialog_height - DIALOG_TEXT_MARGIN,
            color=arcade.color.BLACK,
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
