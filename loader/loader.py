from typing import Protocol

from parsers.parser import Parser


class Loader(Protocol):

    def load(self):

