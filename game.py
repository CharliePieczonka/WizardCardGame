import cardDeck
import player
from random import randint
import pygame
#import gameClient
import time
import scoreCard
from network import network

class game:

    def __init__(self, numPlayers, playerNames, maxRound):
        self.round = 1
        self.dealer = randint(0, numPlayers-1)
        #self.dealer = 0 # testing purposes, make player 2 first to go
        self.players = []
        self.numPlayers = numPlayers
        self.totalBid = 0
        self.currentTrick = []
        self.leadingSuit = "none"

        # number of plays for 1 trick
        self.playCount = 0

        self.biddingPhase = True
        self.playPhase = False
        self.trickCompleted = False

        self.ready = False
        self.playersWent = []
        self.currentPlayer = (self.dealer + 1) % numPlayers
        self.globalMsg = []
        self.isDealt = False

        # number of bids per round
        self.bids = 0

        # number of tricks played per round
        self.tricks = 0

        self.scoreCard = scoreCard.scoreCard()

        self.maxRound = maxRound

        for i in range(numPlayers):
            self.players.append(player.player(i, playerNames[i]))
            self.playersWent.append(False)

    def connected(self):
        return self.ready

    def allPlayersGone(self):
        for went in self.playersWent:
            if went == False:
                return False

        return True

    def resetWent(self):
        for i in range(self.playersWent.__len__()):
            self.playersWent[i] = False

    # a function call to create a deck
    def createDeck(self):
        self.deck = cardDeck.cardDeck()
        self.trump = self.deck.randomCard()
        #self.trump = self.deck.cards[59] # wizard

    # Deal the "round number" of cards to each player randomly from the deck
    def deal(self):
        for i in range(self.round):
            for j in range(self.numPlayers):
                random = self.deck.randomCard()
                random.owner = self.players[j].playerID
                self.players[j].playerCards.append(random)

        # dealing means a new round has begun, thus make a new row on the score card
        self.scoreCard.addRow(self.round, self.numPlayers)

    def determineTrick(self, trump):
        winningCard = self.currentTrick[0]
        self.currentTrick.remove(winningCard)

        # if the first card played is a jester it cannot win, thus pick a new card
        while winningCard.value == 0:

            # try in case all players play a jester; in such a case, there will be no cards left so break
            try:
                winningCard = self.currentTrick[0]
                self.currentTrick.remove(winningCard)
            except:
                break

        for card in self.currentTrick:

            # if the first card of the trick is a wizard it wins
            if winningCard.value == 15:
                return winningCard

            # else if card is a wizard make it the winningCard
            elif card.value == 15:
                winningCard = card

            elif card.suit == trump.suit:
                if winningCard.suit != trump.suit:
                    # if the card is trump and the winning card is not
                    winningCard = card
                elif card.value > winningCard.value:
                    # of both cards are trump but winning card is lower
                    winningCard = card
            elif card.suit == self.leadingSuit:
                if winningCard.suit == self.leadingSuit and card.value > winningCard.value:
                    # if both cards are the leading suit and card is greater than winning card
                    winningCard = card
                elif winningCard.suit != self.leadingSuit and winningCard.suit != trump.suit:
                    # if the winning card is neither the leading suit nor trump
                    winningCard = card
            elif card.suit == winningCard.suit and card.value > winningCard.value:
                winningCard = card

        self.currentTrick.clear()
        return winningCard

    # determine the score for each player
    def determineScore(self):
        for person in self.players:
            if person.bid == person.tricksTaken:
                person.score += 20
                person.score += person.tricksTaken*10
            else:
                person.score -= abs(person.tricksTaken - person.bid) * 10

            # reset the persons bid and tricks taken
            person.bid = 0
            person.tricksTaken = 0
            person.playerCards.clear()

            if person.allScores.__len__() == 4:
                person.allScores.remove(person.allScores[0])
            person.allScores.append(person.score)

            self.scoreCard.rows[self.round - 1].scores.append(person.score)

    def playCard(self, card, player):
        # append the card being played to the current trick
        self.currentTrick.append(card)

        # remove the card being played from the player's hand
        self.players[player].playerCards.remove(card)

def PlayComputer():

    # TODO: implement a start up page
    print ("Welcome to Wizard!")

    #username = str(input("Please enter your name: "))
    username = "char"
    #numComp = int(input("Please enter the number of opponents: "))
    #print("Thank you " + username + "! Please wait while your game loads.")

    # create the game with a randomly chosen dealer
    #Game = game(numComp, username, randint(0, numComp))
    Game = game(3, "char", randint(0, 3))

    # create client window
    window = gameClient.gameClient()

    while True:

        # checking if user has quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        # update the display and redraw the window
        window.redrawWindow()

        # start up message
        window.updateMessages("Welcome to Wizard! press any key to start a game.")
        pygame.display.update()

        while True:
            pygame.event.clear()
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                break

        while Game.round <= (60/Game.numPlayers):


            print("\nRound " + str(Game.round) + ".")
            window.updateMessages("Round " + str(Game.round) + ".")
            pygame.display.update()
            time.sleep(1)

            # convey who the dealer is
            if (Game.players[Game.dealer].name == "comp"):
                print(str(Game.players[Game.dealer].name) + str(Game.players[Game.dealer].playerID)
                      + " is the dealer\n")
                window.updateMessages(str(Game.players[Game.dealer].name) + str(Game.players[Game.dealer].playerID)
                      + " is the dealer")
            else:
                print(str(Game.players[Game.dealer].name) + " is the dealer\n")
                window.updateMessages(str(Game.players[Game.dealer].name) + " is the dealer")

            pygame.display.update()
            time.sleep(1)

            window.updateMessages(" ")

            # create the deck and deal the first hand and determine trump
            Game.createDeck()
            Game.deal()
            trump = Game.deck.randomCard()

            # tell the user their hand
            print(username + ", your hand contains: ")
            for j in range(len(Game.players[0].playerCards)):
                print(str(Game.players[0].playerCards[j].value) + " of " + str(Game.players[0].playerCards[j].suit))

            # display the users cards
            window.displayCards(Game.players[0].playerCards)

            print("\nThe trump card is " + str(trump.value) + " of " + str(trump.suit) + "\n")
            window.displayTrump(trump)
            pygame.display.update()

            # BIDDING PHASE starting with player left of the dealer
            bidCount = 0
            bidderID = (Game.dealer+1) % Game.numPlayers
            while bidCount < Game.numPlayers:
                bidder = Game.players[bidderID]
                if bidder.playerID == 0:

                    # Game.players[0].bid = int(input("Enter the number of tricks you would like to bid: ")
                    window.updateMessages("Please enter your bid: ")
                    pygame.display.update()

                    # clear the events and wait for a keydown event
                    # TODO: check the user has typed in a number and make hitting enter necessary to continue
                    pygame.event.clear()
                    event = pygame.event.wait()
                    while event.type != pygame.KEYDOWN:
                        event = pygame.event.wait()

                    # obtain the key value of the event and make it the players bid and print it to the screen
                    Game.players[0].bid = int(chr(event.key))
                    window.messages.pop()
                    window.updateMessages("Please enter your bid: " + chr(event.key))
                    pygame.display.update()

                else:
                    Game.computerBid(bidder, trump)
                    msg = (str(bidder.name) + str(bidder.playerID) + " has bid " + str(Game.players[bidder.playerID].bid))
                    window.updateMessages(msg)
                    pygame.display.update()

                bidCount += 1
                bidderID = (bidder.playerID + 1) % Game.numPlayers
                time.sleep(1)

            # PLAY PHASE starting with player left of the dealer
            # number of tricks is determined by the round number
            numTricks = 0
            while numTricks < Game.round:

                if numTricks == 0:
                    Game.currentPlayer = Game.players[bidderID]

                # number of cards played per trick is determined by the number of players
                Game.playCount = 0
                print("\n")
                while Game.playCount < Game.numPlayers:

                    # if it is the human player's turn
                    if Game.currentPlayer.playerID == 0:
                        # print("What card would you like to play?") # this will change to a click and confirm method

                        window.updateMessages("Click the card you would like to play, then hit enter.")
                        pygame.display.update()

                        # wait for enter key to confirm selection
                        pygame.event.clear()
                        event = pygame.event.wait()

                        while event.type != pygame.KEYDOWN:
                            selection = False
                            event = pygame.event.wait()
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                if event.button == 1:
                                    selection = Game.players[0].cardSelection(event)

                            #if selection:
                                # window.redrawWindow()
                                # window.updateMessages()
                                # window.displayTrump(trump)
                                # window.displayCards(None, Game.players[0])
                                # pygame.display.update()
                            window.redrawAll(Game.currentTrick, Game.players, None, Game.players[0], trump)
                            pygame.display.update()

                        # remove the card from the players hand and add it to the current trick
                        for card in Game.players[0].playerCards:
                            if card.selected:
                                if Game.playCount == 0:
                                    Game.leadingSuit = card.suit

                                Game.players[0].playerCards.remove(card)
                                Game.currentTrick.append(card)

                                window.redrawAll(Game.currentTrick, Game.players, None, Game.players[0], trump)
                                pygame.display.update()

                    # if it is an NPC's turn
                    else:
                        Game.computerPlay(Game.currentPlayer)
                        window.redrawAll(Game.currentTrick, Game.players, None, Game.players[0], trump)
                        pygame.display.update()

                    Game.playCount += 1
                    Game.currentPlayer = Game.players[(Game.currentPlayer.playerID + 1) % 4]
                    time.sleep(1)

                winningCard = Game.determineTrick(trump)
                if winningCard.owner != 0:
                    print("The winner of the trick is " + str(Game.players[winningCard.owner].name)
                        + str(Game.players[winningCard.owner].playerID))
                    window.updateMessages("The winner of the trick is " + str(Game.players[winningCard.owner].name)
                        + str(Game.players[winningCard.owner].playerID))
                else:
                    print("The winner of the trick is " + str(Game.players[winningCard.owner].name))
                    window.updateMessages("The winner of the trick is " + str(Game.players[winningCard.owner].name))
                pygame.display.update()

                # update the current player for next hand as the winner of this hand and update their tricks taken
                Game.currentPlayer = Game.players[winningCard.owner]
                Game.currentPlayer.tricksTaken += 1

                numTricks += 1
                time.sleep(3)
                window.updateMessages(" ")
                window.redrawAll(None, None, None, Game.players[0], trump)

            print("\nThe round is over.")
            print("The scores are as follows: ")

            window.updateMessages("The round is over. Press Enter to continue.")
            pygame.display.update()

            pygame.event.clear()
            event = pygame.event.wait()
            while event.type != pygame.KEYDOWN:
                # do nothing
                event = pygame.event.wait()


            Game.determineScore()

            for person in Game.players:
                if person.playerID == 0:
                    print(str(person.name) + " has " + str(person.score))

                else:
                    print(str(person.name) + str(person.playerID) + " has " + str(person.score))

            # increment the round and dealer
            Game.round += 1
            Game.dealer = (Game.dealer + 1) % Game.numPlayers
            window.messages.clear()
