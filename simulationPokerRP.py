import random


def f(x, alpha):
    return 1-(1-x)*alpha


class Player:
    def __init__(self, number, strategie, initial_bankroll=0):
        self.number = number
        self.bankroll = initial_bankroll
        self.hand = 0
        self.cut_off_points = {}
        self.alpha = strategie["alpha"]
        self.beta = strategie["beta"]
        self.a = strategie["a"]
        self.b = strategie["b"]
        self.c = strategie["c"]

    def draw(self):
        self.hand = random.uniform(0, 1)


class Poker:
    def __init__(self, J1, J2, nb_max_raise):
        self.players = [J1, J2]
        self.nb_max_raise = nb_max_raise
        self.nb_raise = 0
        self.pot = 0
        self.isShowdown = False
        self.inBet = False
        self.inRaise = False
        self.check = False
        self.Fold = False
        self.num_round = 1
        self.winner = 0

    def initialize_game(self):
        self.pot = 0
        self.nb_raise = 0
        self.players[0].cut_off_points = {
            "bluff": (1-self.players[0].a)/2, "bet": self.players[0].a}
        self.players[1].cut_off_points = {}
        self.isShowdown = False
        self.inBet = False
        self.inRaise = False
        self.check = False
        self.Fold = False
        self.num_round = 1
        self.winner = 0

    def ante(self):
        for player in self.players:
            player.draw()
            player.bankroll -= 1
        self.pot += 2

    def bet(self, player):
        player.bankroll -= self.pot
        self.pot *= 2
        self.inRaise = True
        if self.print_play:
            print(f"Joueur {player.number} mise ")

    def Raise(self, player):
        player.bankroll -= self.pot
        self.pot *= 2
        self.nb_raise += 1
        self.inRaise = True
        alpha = self.players[2-player.number].alpha
        beta = self.players[2-player.number].beta
        a = self.players[2-player.number].a
        if self.num_round == 2:
            self.players[2-player.number].cut_off_points = {"bluff_raise": ((
                1-a)*alpha**2)/2, "call": 1-(1-a)*beta, "raise": 1-(1-a)*alpha**2}
        else:
            self.players[2-player.number].cut_off_points["bluff_raise"] = player.cut_off_points["bluff_raise"]*alpha
            self.players[2-player.number].cut_off_points["call"] = f(
                player.cut_off_points["call"], alpha)
            self.players[2-player.number].cut_off_points["raise"] = f(
                player.cut_off_points["raise"], alpha)

        if self.print_play:
            print(f"Joueur {player.number} raise")

    def fold(self, player):
        self.winner = 3-player.number
        self.Fold = True
        if self.print_play:
            print(f"Joueur {player.number} se couche")

    def call(self, player):
        player.bankroll -= self.pot/2
        self.pot += self.pot/2
        self.isShowdown = True
        if self.print_play:
            print(f"Joueur {player.number} suit, place au reveal")

    def round(self, player):
        if self.print_play:
            print(
                f"Les cut-off points du joueur {player.number} sont : ", player.cut_off_points,)
        oth_player = self.players[2-player.number]
        if self.num_round == 1:
            if player.cut_off_points['bluff'] <= player.hand and player.hand <= player.cut_off_points['bet']:
                self.check = True
                oth_player.cut_off_points = {
                    "bluff_bet": (1-oth_player.c)/2, "bet": oth_player.c}
                if self.print_play:
                    print(f"Joueur {player.number}  check")
            else:
                self.bet(player)
                oth_player.cut_off_points = {"bluff_raise": (
                    1-oth_player.a)*oth_player.alpha/2, "call": b, "raise": 1-(1-oth_player.a)*oth_player.alpha}

        elif self.num_round == 2:
            if self.check:
                if player.hand <= player.cut_off_points['bluff_bet'] or player.hand >= player.cut_off_points['bet']:
                    self.bet(player)
                    oth_player.cut_off_points = {"call": oth_player.b}
                else:
                    self.isShowdown = True
                    if self.print_play:
                        print(
                            f"Joueur {player.number} check aussi, place au reveal")
            else:
                if player.hand <= player.cut_off_points['bluff_raise'] or player.hand >= player.cut_off_points['raise']:
                    self.Raise(player)
                elif player.hand <= player.cut_off_points['call']:
                    self.fold(player)
                else:
                    self.call(player)

        elif self.num_round == 3 and self.check:
            if player.hand >= player.cut_off_points["call"]:
                self.call(player)
            else:
                self.fold(player)

        elif self.inRaise:
            if player.hand <= player.cut_off_points['bluff_raise'] or player.hand >= player.cut_off_points['raise']:
                self.Raise(player)
            elif player.hand <= player.cut_off_points['call']:
                self.fold(player)
            else:
                self.call(player)

    def showdown(self):
        if self.players[0].hand < self.players[1].hand:
            self.winner = 2
        elif self.players[1].hand < self.players[0].hand:
            self.winner = 1

    def last_round(self, player):
        if player.cut_off_points['bluff_raise'] <= player.hand and player.hand <= player.cut_off_points['call']:
            self.fold(player)
        else:
            self.call(player)

    def play(self, print_play=True):
        self.print_play = print_play
        self.initialize_game()
        self.ante()
        num_player = 0
        if self.print_play:
            print("Joueur 1 a pour main : ", self.players[0].hand)
            print("Joueur 2 a pour main : ", self.players[1].hand)
        while not self.isShowdown and not self.Fold and self.nb_raise <= self.nb_max_raise:
            self.round(self.players[num_player])
            num_player = (num_player+1) % 2
            self.num_round += 1
        if self.nb_raise == self.nb_max_raise:
            self.last_round(self.players[num_player])
        if self.isShowdown:
            self.showdown()
        self.players[self.winner-1].bankroll += self.pot
        if self.print_play:
            print(
                f"Le vainqueur est le joueur {self.winner}! On le félicite !")


if __name__ == "__main__":
    a = 0.874
    alpha = 0.215
    beta = 0.477
    b = 0.514
    c = 0.694
    nb_max_raise = 5
    eps = 0
    optimal_strat = {"a": a, "b": b, "c": c, "alpha": alpha, "beta": beta}
    conservative_strat = {
        "a": 1, "b": b, "c": 1, "alpha": 0, "beta": beta}
    bluffer_strat = {
        "a": 0, "b": 0, "c": 0, "alpha": 1, "beta": 1}
    J1 = Player(1, optimal_strat)
    J2 = Player(2, bluffer_strat)
    poker_game = Poker(J1, J2, nb_max_raise)
    # poker_game.play(True)
    N = 100
    for _ in range(N):
        poker_game.play(True)
    print(f"Le gain moyen du Joueur 1 est : ", J1.bankroll/N)
    print(f"Le gain moyen du Joueur 2 est : ", J2.bankroll/N)
