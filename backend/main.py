from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import app.models as models
from app.database import engine, get_db
from app.schemas import Person, Tournament, Match
from app.utils.people_utils import check_everyone_exists, create_player_lookup
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

    # Add results to the results table
    results = db.query(models.Results).all()
    results_id = len(results) + 1
    for i in range(len(tournament_people)):
        results = models.Results(id=results_id,
                                 tournament_name=tournament.name,
                                 player_id=name_to_id[tournament_people[i]],
                                 played=0,
                                 won=0,
                                 lost=0,
                                 drawn=0,
                                 frames_for=0,
                                 frames_against=0)
        results_id += 1
        db.add(results)
        db.commit()
        db.refresh(results)

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

