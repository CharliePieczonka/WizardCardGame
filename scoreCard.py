class scoreCard:
    def __init__(self):
        self.rows = []

    def addRow(self, round, numPlayers):

        self.rows.append(row(round, numPlayers))

class row:
    def __init__(self, round, numPlayers):
        self.round = round
        self.scores = []
        self.bids = []
        self.tricksTaken = []

        for i in range(numPlayers):
            self.tricksTaken.append(-1)
            self.bids.append(-1)
