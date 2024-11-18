from enum import Enum
from random import choice


class Suit:
    Spears = 0
    Spades = 1
    Hearts = 2
    Diamonds = 3


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
