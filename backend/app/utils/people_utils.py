from ..models import Person

def check_everyone_exists(list_to_compare, db_people_list):
    for player in list_to_compare:
        found = False
        name_split = player.split(" ")
        firstname = name_split[0].lower()
        surname = name_split[1].lower()
        for person in db_people_list:
            if firstname == person.firstname and \
               surname == person.surname:
                found = True
        if found == False:
            return False
    return True

def create_player_lookup(result_list: list[Person]):
    name_to_id = {}
    id_to_name = {}
    for person in result_list:
        player_name = person.firstname + " " + person.surname
        player_id = person.id
        name_to_id[player_name] = player_id
        id_to_name[player_id] = player_name
    return name_to_id, id_to_name