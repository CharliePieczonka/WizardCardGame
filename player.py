import pygame

class player:
    def __init__(self, playerID, name):
        self.playerCards = []
        self.playerID = playerID
        self.name = name
        self.bid = -1
        self.tricksTaken = 0
        self.score = 0

        # lists of all previous scores, bids, and tricks taken for score sheet purposes
        self.allScores = []
        self.allBids = []
        self.alltricksTaken = []

