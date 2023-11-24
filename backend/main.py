from fastapi import FastAPI, Depends, HTTPException
from typing import Dict
from sqlalchemy.orm import Session
import app.models as models
from app.database import engine, get_db
from app.schemas import Person, Tournament, Match, Result
from app.utils.people_utils import check_everyone_exists, create_player_lookup
from app.utils.data_merging_utils import update_results
from app.enums import TournamentType

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/players")
async def get_players(db: Session = Depends(get_db)):
    players = db.query(models.Person).all()
    return players

@app.get("/player/{name}")
async def get_player(name: str, db: Session = Depends(get_db)):
    name_split = name.split(" ")
    firstname = name_split[0].lower()
    surname = name_split[1].lower()
    player = db.query(models.Person).filter(models.Person.firstname == firstname, models.Person.surname == surname).all()
    if len(player) > 0:
        return player
    else:
        raise HTTPException(status_code=404,
                                detail=f'{firstname} {surname} does not exist')

@app.post("/player")
async def add_person(person: Person, db: Session = Depends(get_db)):
    results = db.query(models.Person).all()
    person.id = len(results)+1
    person.firstname = person.firstname.lower()
    person.surname = person.surname.lower()
    for result in results:
        if result.firstname == person.firstname and \
           result.surname == person.surname:
            raise HTTPException(status_code=409,
                                detail=f'{person.firstname} {person.surname} already exists')

    new_person = models.Person(**person.__dict__)
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    return new_person

@app.get("/tournament/{name}")
async def get_tournament(name: str, db: Session = Depends(get_db)):
    tournaments = db.query(models.Tournament).filter(models.Tournament.name == name).all()
    if len(tournaments) > 0:
        return tournaments
    else:
        raise HTTPException(status_code=404,
                                detail=f'{name} does not exist')

@app.post("/tournament")
async def add_tournament(tournament: Tournament, db: Session = Depends(get_db)):
    # Check people already exist in the system
    people_list = db.query(models.Person).all()
    tournament_people = tournament.people
    everyone_exists = check_everyone_exists(tournament.people, people_list)
    if not everyone_exists:
        raise HTTPException(status_code=404,
                            detail=f'Not all players are registered in the app')
        
    # Add tournament to tournament table
    tournaments = db.query(models.Tournament).filter(models.Tournament.name == tournament.name).all()
    if len(tournaments) != 0:
        raise HTTPException(status_code=409,
                            detail=f'{tournament.name} already exists')
    
    else:
        tourney_dict = tournament.__dict__
        del tourney_dict["people"]
        new_tourney = models.Tournament(**tourney_dict)
        db.add(new_tourney)
        db.commit()
        db.refresh(new_tourney)

    # Add matches to matches table
    matches = db.query(models.Matches).all()
    match_id = len(matches) + 1

    # Create player ID lookup
    people = db.query(models.Person).all()
    name_to_id, id_to_name = create_player_lookup(people)
    for i in range(len(tournament_people)):
        for j in range(i+1,len(tournament_people)):
            match = models.Matches(id=match_id,
                                   tournament_name=tournament.name,
                                   player1=name_to_id[tournament_people[i]],
                                   player2=name_to_id[tournament_people[j]])
            match_id += 1
            db.add(match)
            db.commit()
            db.refresh(match)

    return new_tourney


@app.post("/result")
async def add_tournament(match: Match, db: Session = Depends(get_db)):

    # Look up tournament and extract format
    print(f'Extracting {match.tournament_name} format info')
    tournament = db.query(models.Tournament).filter(models.Tournament.name == match.tournament_name).all()
    format = tournament[0].type
    if format == TournamentType.BEST_OF:
        if match.player1_score + match.player2_score > tournament[0].best_of:
            raise HTTPException(status_code=400, detail=("The amount of frames exceeds best of score"))
        if max(match.player1_score, match.player2_score) != (tournament[0].best_of + 1)/2:
            raise HTTPException(status_code=400, detail=("No one won enough frames to win the game"))
    elif format == TournamentType.PLAY_ALL:
        if match.player1_score + match.player2_score != tournament[0].best_of:
            raise HTTPException(status_code=400, detail=("The amount of frames doesn't equal the total frames for each match"))
    else:
        pass
    
    print("Updating row in match table")
    # Update match table
    db.query(models.Matches).\
       filter(models.Matches.tournament_name == match.tournament_name,
              models.Matches.player1.in_([match.player1, match.player2]),
              models.Matches.player2.in_([match.player1, match.player2])).\
       update({'player1_score': match.player1_score,
               'player2_score': match.player2_score})
    db.commit()
    
    return {"message": "Updated result successfully"}

@app.get("/results/{tournament_name}")
async def add_tournament(tournament_name: str, scoring_system: str = "Default", db: Session = Depends(get_db)):
    print("I HAVE GOT HERE IN RESULTS")
    matches = db.query(models.Matches).filter(models.Matches.tournament_name == tournament_name).all()
    people = db.query(models.Person).all()
    results: Dict(Result) = {}
    players_found = []
    _, id_to_name = create_player_lookup(people)
    for match in matches:
        # Check if player 1 and 2 already exist
        print(id_to_name[match.player1])
        if match.player1 not in players_found:
            players_found.append(match.player1)
            results[match.player1] = Result(player_name=id_to_name[match.player1])
        if match.player2 not in players_found:
            players_found.append(match.player2)
            results[match.player2] = Result(player_name=id_to_name[match.player2]) 
        
        print(results)
        # Calculate the result delta for each player in the match
        player1, player2 = update_results(match, results[match.player1], results[match.player2])
        results[match.player1] = player1
        results[match.player2] = player2
    
    result_list = list(results.values())
    return result_list