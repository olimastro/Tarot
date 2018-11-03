import math

class Round:
    modifier = {
        'p': 1,
        'g': 2,
        'gs': 4,
        'gc': 8}

    towin = {
        0: 56,
        1: 51,
        2: 41,
        3: 36}

    def __init__(self, players):
        assert len(players) == 5
        self.players = set(players)

    def run(self, contract, evil, coevil, score, nbbouts=None,
            petitaubout=False, manual_run=False):
        petitaubout = 10 if petitaubout else 0
        if not manual_run:
            assert contract in self.modifier, "Contract allowed '%s':" % self.modifier.keys()
            assert nbbouts in self.towin, "NB bouts allowed '%s':" % self.towin.keys()
            towin = self.towin[nbbouts]

            modifier = 1
            # drop 0.5
            score = math.floor(score) - towin
            if score < 0:
                modifier *= -1
            score += (petitaubout + 25) * modifier
            score *= self.modifier[contract]

        rval = {p: -score for p in self.players if p not in \
                [evil, coevil]}
        rval.update({evil: 2*score, coevil: score})

        return rval
