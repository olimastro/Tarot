import os
import pickle as pkl
from parser import (parse_players, parse_round, parse_user_bool_question,
                    RollUserInputUntilCondition)

TMPDBPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.tmp_db.pkl')

class Tournament:
    def __init__(self, date=None, players=None):
        self.date = date
        self.players = set([]) if players is None else set(players)
        self.rounds = []

    def add_player(self, player):
        self.players.add(player)

    def add_round(self, scores):
        for p in scores:
            self.add_player(p)
        self.rounds.append(scores)


class OSPath(RollUserInputUntilCondition):
    def __init__(self, *args, reverse=False):
        super().__init__(*args)
        self.reverse = reverse

    def check_condition(self, path):
        if self.reverse:
            return not os.path.isfile(path)
        return os.path.isfile(path)


class Database:
    def __init__(self, name):
        self.name = name
        self.tournaments = []
        self.path = None

    def add_tournament(self, t):
        self.tournaments.append(t)

    @property
    def players(self):
        players = set([])
        for t in self.tournaments:
            players = players | t.players
        return players

    def save_db(self, path=None):
        path = self.path if path is None else path
        with open(path, 'wb') as f:
            pkl.dump(self, f)

    def copy_to_tmp(self):
        self.save_db(TMPDBPATH)

    def finalize_db(self):
        print("Modified db at %s" % self.path)
        if parse_user_bool_question("Overwrite"):
            self.save_db()
            print("There is unmodified db at %s" % TMPDBPATH)
            if parse_user_bool_question("Erase"):
                os.remove(TMPDBPATH)
        else:
            path = OSPath('Gimme new path', 'There is something there',
                          reverse=True).roll_until_correct()
            self.save_db(path)
            # there is no need to ask the user to erase the tmp,
            # the user did not overwrite the original
            os.remove(TMPDBPATH)
        print("Done finalizing db")

    @staticmethod
    def load():
        path = OSPath('Gimme path', 'No file found').roll_until_correct()
        with open(path, 'rb') as f:
            db = pkl.load(f)
        db.path = path
        db.copy_to_tmp()
        return db


if __name__ == "__main__":
    from round import Round
    def add_manual(db):
        while True:
            players = db.players
            t = Tournament(players=players)
            while True:
                players = t.players
                p = parse_players(players)
                rinf = parse_round(p, manual_round=True)
                r = Round(p)
                s = r.run(rinf['contract'], rinf['evil'], rinf['coevil'], rinf['score'],
                          None, False, True)
                print(s)
                if not parse_user_bool_question('Correct'):
                    continue
                t.add_round(s)
                if parse_user_bool_question('Done adding rounds'):
                    break
            db.add_tournament(t)
            if parse_user_bool_question('Done adding tournaments'):
                break

    print("You are in the data file. You manually add runs to the db here")
    db = Database.load()
    while True:
        try:
            add_manual(db)
            break
        except KeyboardInterrupt:
            print("There was a KeyboardInterrupt")
            if parse_user_bool_question("Restart adding tournaments"):
                continue
            break
    db.finalize_db()
