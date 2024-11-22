from enum import Enum
from card import Deck
from collections import Counter
from itertools import combinations


class State(Enum):
    No = 0
    Check = 1
    Call = 2
    Raise = 3
    Pass = 4


class PokerTable:
    # init a virtual 1v1 poker table
    def __init__(self, balance1, balance2):
        self.balance1 = balance1
        self.balance2 = balance2
        self.pot = 0
        self.bid1 = 0
        self.bid2 = 0  # bid of each player in this circle
        self.state1 = State.No
        self.state2 = State.No
        self.deck = Deck()

        self.open = []  # opened cards len <= 5

        self.cards1 = [self.deck.pick(), self.deck.pick()]
        self.cards2 = [self.deck.pick(), self.deck.pick()]

        self.turn = False  # False - 1 turn True - 2 turn
        self.winner = -1

    def next_circle(self):
        if len(self.open) == 5:
            self.winner = result(self.open, self.cards1, self.cards2)
            if self.winner == 1:
                self.balance1 += self.pot
            elif self.winner == 2:
                self.balance2 += self.pot
            return
        self.bid2 = 0
        self.bid1 = 0
        self.turn = False
        self.state1 = State.No
        self.state2 = State.No
        if len(self.open) == 0:
            self.open.append(self.deck.pick())
            self.open.append(self.deck.pick())
        self.open.append(self.deck.pick())

    def first_check(self):
        self.turn = not self.turn  # TODO check whos turn is now
        if self.state2 == State.Raise:
            raise Exception("Imposible to check")
        self.state1 = State.Check
        if self.state2 == State.Check:
            self.next_circle()

    def second_check(self):
        self.turn = not self.turn
        if self.state1 == State.Raise:
            raise Exception("Imposible to check")
        self.state2 = State.Check
        if self.state1 == State.Check:
            self.next_circle()

    def first_raise(self, value):
        self.turn = not self.turn
        if self.bid1 + value < self.bid2:
            raise Exception("The sum is too low")
        if value < 0:
            raise Exception("value cannot be lower than zero")
        if value > self.balance1:
            raise Exception("bid is higher than the balance last")
        self.balance1 -= value
        self.bid1 += value
        self.pot += value
        self.state1 = State.Raise

    def second_raise(self, value):  # TODO one of the players has zero balance than nobody can raise
        self.turn = not self.turn
        if self.bid2 + value < self.bid1:
            raise Exception("The sum is too low")
        if value < 0:
            raise Exception("value cannot be lower than zero")
        if value > self.balance2:
            raise Exception("bid is higher than the balance last")
        self.balance2 -= value
        self.bid2 += value
        self.pot += value
        self.state2 = State.Raise

    def first_call(self):
        self.turn = not self.turn
        if self.bid2 < self.bid1:
            raise Exception("cannot call cause bid2 < bid1")
        self.balance1 -= self.bid2 - self.bid1  # TODO can be zero
        self.pot += self.bid2 - self.bid1
        self.bid1 = self.bid2
        self.state1 = State.Call
        self.next_circle()

    def second_call(self):
        self.turn = not self.turn
        if self.bid1 < self.bid2:
            raise Exception("cannot call cause bid1 < bid2")
        self.balance2 -= self.bid1 - self.bid2  # TODO can be zero
        self.pot += self.bid1 - self.bid2
        self.bid2 = self.bid1
        self.state2 = State.Call
        self.next_circle()

    def first_pass(self):
        self.turn = False
        self.balance2 += self.pot
        self.pot = 0
        self.bid1 = 0
        self.bid2 = 0
        self.state1 = State.Pass
        self.next_circle()

    def second_pass(self):
        self.turn = False
        self.balance1 += self.pot
        self.pot = 0
        self.bid1 = 0
        self.bid2 = 0
        self.state2 = State.Pass
        self.next_circle()


# TODO get balance cards ... funcs if needed
def evaluate_hand(hand):
    values = sorted([card.value for card in hand], reverse=True)
    suits = [card.suit for card in hand]
    value_counts = Counter(values)
    is_flush = len(set(suits)) == 1
    is_straight = len(set(values)) == 5 and (values[0] - values[-1] == 4 or values == [14, 5, 4, 3, 2])

    if is_flush and is_straight:
        return (8, values)  # Стрит-флэш
    if 4 in value_counts.values():
        four = max(k for k, v in value_counts.items() if v == 4)
        kicker = max(k for k, v in value_counts.items() if v < 4)
        return (7, [four, kicker])  # Каре
    if 3 in value_counts.values() and 2 in value_counts.values():
        three = max(k for k, v in value_counts.items() if v == 3)
        two = max(k for k, v in value_counts.items() if v == 2)
        return (6, [three, two])  # Фулл-хаус
    if is_flush:
        return (5, values)  # Флэш
    if is_straight:
        return (4, values)  # Стрит
    if 3 in value_counts.values():
        three = max(k for k, v in value_counts.items() if v == 3)
        kickers = sorted([k for k, v in value_counts.items() if v < 3], reverse=True)
        return (3, [three] + kickers)  # Сет
    if list(value_counts.values()).count(2) == 2:
        pairs = sorted((k for k, v in value_counts.items() if v == 2), reverse=True)
        kicker = max(k for k, v in value_counts.items() if v == 1)
        return (2, pairs + [kicker])  # Две пары
    if 2 in value_counts.values():
        pair = max(k for k, v in value_counts.items() if v == 2)
        kickers = sorted([k for k, v in value_counts.items() if v < 2], reverse=True)
        return (1, [pair] + kickers)  # Одна пара
    return (0, values)  # Старшая карта


def result(lst, first, second):
    # Все карты на столе + карты игроков
    community_cards = lst
    player1_cards = community_cards + first
    player2_cards = community_cards + second

    # Все комбинации из 5 карт для каждого игрока
    player1_hands = [hand for hand in combinations(player1_cards, 5)]
    player2_hands = [hand for hand in combinations(player2_cards, 5)]

    # Оцениваем каждую комбинацию
    player1_best = max([evaluate_hand(hand) for hand in player1_hands])
    player2_best = max([evaluate_hand(hand) for hand in player2_hands])

    # Сравнение комбинаций
    if player1_best > player2_best:
        return 1
    elif player1_best < player2_best:
        return 2
    else:
        return 0
