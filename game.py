import random
from classes import Board, Player
import click


def roll():
    d = [i + 1 for i in range(6)]
    d1 = random.choice(d)
    d2 = random.choice(d)
    return d1+d2, d1 == d2


def monopoly(games=1000, turns=500, player_count=4):

    board = Board()  # Initialise game board
    players = [Player() for i in range(player_count)]  # Initialise players
    # Play games, wrap in progressbar to display progress
    with click.progressbar(range(games), label="Running games") as bar:
        for _ in bar:
            board.reset_board(players)  # reset board after each game)
            for _ in range(turns):
                # each player rolls.
                for player in players:
                    double_count = 0
                    roll_eligible = True
                    # Keep track of doubles
                    while roll_eligible:
                        num, double = roll()
                        if double:
                            double_count += 1
                            roll_eligible = True
                        else:
                            roll_eligible = False
                        if double_count == 3:
                            board.three_double_jail(player)
                        board.move(player, num)
    # print the landing frequencies for each space
    landing = [(key, value) for key, value in board.space_log.items()]
    landing.sort(key=lambda x: x[1], reverse=True)
    denom = sum([x[1] for x in landing])
    landing = [(x[0], x[1]/denom) for x in landing]
    for l in landing:
        print(l)


if __name__ == "__main__":
    monopoly()
