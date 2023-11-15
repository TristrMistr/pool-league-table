from ...app.schemas import Tournament
import pytest

def test_good_best_of():
    test_tournament = Tournament(id=1, name="test", type="best of", best_of=7, people=["Tristan Owen"])
    assert test_tournament.id == 1

def test_good_play_all():
    test_tournament = Tournament(id=1, name="test", type="play all", total_frames=7, people=["Tristan Owen"])
    assert test_tournament.id == 1

def test_no_such_type():
    with pytest.raises(Exception):
        Tournament(id=1, name="test", type="doesn't exist", total_frames=7, people=["Tristan Owen"])

def test_best_of_field_empty():
    with pytest.raises(ValueError):
        Tournament(id=1, name="test", type="best of", people=["Tristan Owen"])

def test_play_all_field_empty():
    with pytest.raises(ValueError):
        Tournament(id=1, name="test", type="play all", people=["Tristan Owen"])

def test_negative_best_of():
    with pytest.raises(ValueError):
        Tournament(id=1, name="test", type="best of", best_of=-9, people=["Tristan Owen"])

def test_negative_total_frames():
    with pytest.raises(ValueError):
        Tournament(id=1, name="test", type="play all", total_frames=-9, people=["Tristan Owen"])



