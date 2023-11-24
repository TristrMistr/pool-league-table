from ..schemas import Result
from ..models import Matches

def update_results(match: Matches, player1: Result, player2: Result) -> (Result, Result):
    if match.player1_score is None:
        return player1, player2
    player1.frames_for += match.player1_score
    player2.frames_for += match.player2_score
    if match.player1_score > match.player2_score:
        player1.won += 1
        player1.points += 1
        player2.lost += 1
    else:
        player1.lost += 1
        player2.won += 1
        player2.points += 1

    return player1, player2