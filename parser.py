import round
CONTRACT = list(round.Round.modifier.keys())

def available_players(players):
    pdict= dict(zip(range(len(players)), players))
    print("Available players: %s" % pdict)
    return pdict

def parse_players(players):
    pdict = available_players(players)
    print("Input 5 players with space between their alias")
    print("A string will be interpreted as new player")
    while True:
        p = input("---> ")
        psplit = p.split(' ')
        new_players = []
        requested_players = []

        for p in psplit:
            if p.isdigit():
                p = int(p)
                if p not in pdict:
                    print("Not recognized %s" % p)
                    break
                requested_players.append(p)
            else:
                new_players.append(p)
        rval = [pdict[x] for x in requested_players] + new_players
        if len(rval) != 5:
            print("Did not find 5 players, restart")
            continue

        print("Found %s" % rval)
        if not parse_user_bool_question('Correct'):
            continue
        return rval

def parse_user_bool_question(q):
    c = input(q+"? ")
    if c in ['', 'y', 'Y']:
        return True
    return False

def parse_round(players, manual_round=False):
    print(" ------ NEW ROUND ------ ")
    pdict = available_players(players)
    msg = "Unrecognized "
    cp = ListParser("Contract?", msg + "contract", CONTRACT)
    ep = DictIntString("Evil?", msg + "players", pdict)
    coep = DictIntString("CoEvil?", msg + "players", pdict)
    sp = StringDigiCondition("Score?", msg + "digit")
    rval = {
        'contract': cp.roll_until_correct(),
        'evil': ep.roll_until_correct(),
        'coevil': coep.roll_until_correct(),
        'score': sp.roll_until_correct(),
    }
    if not manual_round:
        nbp = StringDigiCondition("How many bouts?", msg + "digit")
        pp = BoolCondition("Small at the bout?", 'Only [y/n]')
        rval.update(
            {'nbbouts': nbp.roll_until_correct(),
             'petitaubout': pp.roll_until_correct()})
    return rval


class RollUserInputUntilCondition:
    def __init__(self, msg, errormsg, obj=None):
        self.msg = msg
        self.errormsg = errormsg
        self.obj = obj

    def check_condition(self, s):
        raise NotImplementedError

    def parse(self, s):
        return s

    def roll_until_correct(self):
        while True:
            answer = input(self.msg + " ---> ")
            if self.check_condition(answer):
                answer = self.parse(answer)
                print("(Chosen '%s')" % answer)
                return answer
            print(self.errormsg)

class BoolCondition(RollUserInputUntilCondition):
    def check_condition(self, s):
        if s in ['y', 'n']:
            return True
        return False

    def parse(self, s):
        if s == 'y':
            return True
        return False

class StringDigiCondition(RollUserInputUntilCondition):
    def check_condition(self, s):
        if s[0] == '-':
            s = s[1:]
        if s.isdigit():
            return True
        return False

    def parse(self, s):
        return int(s)

# obj is a list of str
class ListParser(RollUserInputUntilCondition):
    def check_condition(self, s):
        return s in self.obj

# obj is a dict of {int: str}
class DictIntString(RollUserInputUntilCondition):
    def check_condition(self, s):
        if s.isdigit() and int(s) in self.obj:
            return True
        return False

    def parse(self, s):
        return self.obj[int(s)]
