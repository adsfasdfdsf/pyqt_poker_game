from enum import Enum
from random import choice


class State(Enum):
    No = 0
    Check = 1
    Call = 2
    Raise = 3
    Pass = 4


class Suit(Enum):
    Spears = 0
    Spades = 1
    Hearts = 2
    Diamonds = 3


suits = {Suit.Spades: "Spades", Suit.Spears: "Spears", Suit.Hearts: "Hearts", Suit.Diamonds: "Diamonds"}
to_suits = {"Spades": Suit.Spades, "Spears": Suit.Spears, "Hearts": Suit.Hearts, "Diamonds": Suit.Diamonds}


class Deck:
    def __init__(self):
        self.deck = []
        for i in [Suit.Spears, Suit.Spades, Suit.Hearts, Suit.Diamonds]:
            for j in range(2, 15):
                self.deck.append(Card(i, j))

    def pick(self):
        card = choice(self.deck)
        self.deck.remove(card)
        return card


class Card:
    def __init__(self, suit, value: int):
        if (value > 14) or (value < 2):
            raise Exception("No card found")
        self.suit = suit
        self.value = value
