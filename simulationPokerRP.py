import random
a = 0.874
alpha = 0.215
beta = 0.477
b = 0.514
c = 0.694

initial_cut_off_points = {"bluff": (
    1-a)/2, "bluff_bet": (1-c)/2, "call": b, "bet": c,  "raise": a}


def f(x, alpha):
    return 1-(1-x)*alpha


class Player:
    def __init__(self, number, initial_bankroll=0):
        self.number = number
        self.bankroll = initial_bankroll
        self.hand = 0
        self.cut_off_points = {}

    def draw(self):
        self.hand = random.uniform(0, 1)


class Poker:
    def __init__(self, nb_max_raise, alpha=alpha, beta=beta):
        self.players = [Player(1), Player(2)]
        self.nb_max_raise = nb_max_raise
        self.alpha = alpha
        self.beta = beta
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
        self.players[0].cut_off_points = {"bluff": (1-a)/2, "bet": a}
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
        # print(f"Joueur {player.number} mise ")

    def Raise(self, player):
        player.bankroll -= self.pot
        self.pot *= 2
        self.nb_raise += 1
        self.inRaise = True
        if self.num_round == 2:
            self.players[2-player.number].cut_off_points = {"bluff_raise": ((
                1-a)*self.alpha**2)/2, "call": 1-(1-a)*self.beta, "raise": 1-(1-a)*self.alpha**2}
        else:
            self.players[2-player.number].cut_off_points["bluff_raise"] = player.cut_off_points["bluff_raise"]*self.alpha
            self.players[2-player.number].cut_off_points["call"] = f(
                player.cut_off_points["call"], self.alpha)
            self.players[2-player.number].cut_off_points["raise"] = f(
                player.cut_off_points["raise"], self.alpha)

        # print(f"Joueur {player.number} raise")

    def fold(self, player):
        self.winner = 3-player.number
        self.Fold = True
        # print(f"Joueur {player.number} se couche")

    def call(self, player):
        player.bankroll -= self.pot/2
        self.pot += self.pot/2
        self.isShowdown = True
        # print(f"Joueur {player.number} suit, place au reveal")

    def round(self, player):
        # print(
        # f"Les cut-off points du joueur {player.number} sont : ", player.cut_off_points)
        if self.num_round == 1:
            if player.cut_off_points['bluff'] <= player.hand and player.hand <= player.cut_off_points['bet']:
                self.check = True
                # print(f"Joueur {player.number}  check")
                self.players[2-player.number].cut_off_points = {
                    "bluff_bet": (1-c)/2, "bet": c}
            else:
                self.bet(player)
                self.players[2-player.number].cut_off_points = {"bluff_raise": (
                    1-a)*self.alpha/2, "call": b, "raise": 1-(1-a)*self.alpha}

        elif self.num_round == 2:
            if self.check:
                if player.hand <= player.cut_off_points['bluff_bet'] or player.hand >= player.cut_off_points['bet']:
                    self.bet(player)
                    self.players[2 -
                                 player.number].cut_off_points = {"call": b}
                else:
                    self.isShowdown = True
                    # print("Joueur 2 check aussi, place au reveal")
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
        if player.cut_off_points['bluff'] <= player.hand and player.hand <= player.cut_off_points['call']:
            self.fold(player)
        else:
            self.call(player)

    def play(self):
        self.initialize_game()
        self.ante()
        num_player = 0
        # print("Joueur 1 a pour main : ", self.players[0].hand)
        # print("Joueur 2 a pour main : ", self.players[1].hand)
        while not self.isShowdown and not self.Fold and self.nb_raise <= self.nb_max_raise:
            self.round(self.players[num_player])
            num_player = (num_player+1) % 2
            self.num_round += 1
        if self.nb_raise == self.nb_max_raise:
            self.last_round(self.players[num_player])
        if self.isShowdown:
            self.showdown()
        self.players[self.winner-1].bankroll += self.pot
        # print(f"Le vainqueur est le joueur {self.winner}! On le félicite !")


nb_max_raise = 5

poker_game = Poker(nb_max_raise)

N = 10**5
for _ in range(N):
    poker_game.play()


print(poker_game.players[0].bankroll/N)
print(poker_game.players[1].bankroll/N)
