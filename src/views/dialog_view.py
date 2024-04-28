from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Union

import arcade



class Npc(arcade.Sprite):  # Move into entities? (requires some refactoring cause of circular imports
    def __init__(self, texture, dialog: Dialog, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 1.5
        self.texture = texture


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

TEST = Dialog(())


class DialogView(arcade.View):
    def __init__(self, prev_view, dialog: Dialog, chars: Dict[Character, Npc]):
        super().__init__()
        self.prev_view = prev_view
        self.dialog = dialog
        self.cur_action = 0

    def on_draw(self):
        self.clear()
        self.prev_view.on_draw()
    
    def on_update(self, delta_time: float):
        pass

