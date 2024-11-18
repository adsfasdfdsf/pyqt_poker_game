from enum import Enum
from card import Deck


class State(Enum):
    No = 0
    Check = 1
    Call = 2
    Raise = 3
    Pass = 4


class Card:
    #init a virtual 1v1 poker table
    def __init__(self, balance1, balance2):
        self.balance1 = balance1
        self.balance2 = balance2
        self.pot = 0
        self.bid1 = 0
        self.bid2 = 0 # bid of each player in this circle
        self.state1 = State.No
        self.state2 = State.No
        self.deck = Deck()

        self.open = [] #opened cards len <= 5

        self.cards1 = [self.deck.pick(), self.deck.pick()]
        self.cards2 = [self.deck.pick(), self.deck.pick()]

        self.turn = False # False - 1 turn True - 2 turn
        self.winner = -1

    def next_circle(self):
        if len(self.open) == 5:
            self.winner = self.results()
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
        self.turn = not self.turn #TODO check whos turn is now
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

    def second_raise(self, value): #TODO one of the players has zero balance than nobody can raise
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

    def results(self):
        pass #TODO who wins logic

# TODO get balance cards ... funcs if needed