from ..schemas import Result, ScoringSystem
from ..models import Matches

def update_results(match: Matches, player1: Result, player2: Result, scoring_system: ScoringSystem) -> (Result, Result):
    if match.player1_score is None:
        return player1, player2
    player1.frames_for += match.player1_score
    player2.frames_for += match.player2_score
    player1.frames_against += match.player2_score
    player2.frames_against += match.player1_score
    if match.player1_score > match.player2_score:
        player1.won += 1
        player2.lost += 1
    else:
        player1.lost += 1
        player2.won += 1

    player1.points = (player1.won*scoring_system.win_points)+(player1.frames_for*scoring_system.frame_points)
    player2.points = (player2.won*scoring_system.win_points)+(player2.frames_for*scoring_system.frame_points)

    return player1, player2