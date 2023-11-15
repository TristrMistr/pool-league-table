from enum import Enum


class TournamentType(Enum):
    BEST_OF = "best of"
    PLAY_ALL = "play all"

# class ValueEnum(db.TypeDecorator):
#     """
#     Enables passing in a Python enum and storing the enum's *value* in the db.
#     The default would have stored the enum's *name* (ie the string).
#     """
#     impl = db.Integer

#     def __init__(self, enumtype, *args, **kwargs):
#         super(IntEnum, self).__init__(*args, **kwargs)
#         self._enumtype = enumtype

#     def process_bind_param(self, value, dialect):
#         if isinstance(value, int):
#             return value

#         return value.value

#     def process_result_value(self, value, dialect):
#         return self._enumtype(value)