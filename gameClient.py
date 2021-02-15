import pygame
import cardDeck
import os
from network import network
import pickle
import copy
import time

pygame.font.init()

class gameClient:

    def __init__(self):
        self.width = 1000
        self.height = 600
        self.tbWidth = 350
        self.tbHeight = 155
        self.messages = []
        self.gameWindow = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Wizard")
        pygame.init()

        self.userCards = []
        self.trick = []
        self.suits = []
        self.numGlobal = 0

    # display the users cards to them
    # doesnt attach a "cardPic" to each card; pickle can send pygame surfaces
    def displayCards(self):
        for card in self.userCards:
            card.cardPic.draw(self.gameWindow)

    def createCardPic(self, playerCards):
        offset = 0
        localCards = copy.deepcopy(playerCards)
        for card in localCards:
            card.cardPic = cardDeck.cardGraphic((380+offset, 430), (100, 151), card.cardID, 'CARDS')
            self.userCards.append(card)
            offset += 18

    # checks all player cards to see if one has been selected
    def cardSelection(self, event):

        cardSelected = False
        for card in self.userCards:

            # don't allow any greyed out cards to be selected
            if "G" not in card.cardID:

                # if a card is already selected
                if card.selected == True:

                    # if the card has not been clicked again, unselect it
                    # if not card.cardPic._rect.collidepoint(event.pos):
                    card.cardPic.position = (card.cardPic.position[0], card.cardPic.position[1] + 50)
                    card.cardPic._rect = pygame.Rect(card.cardPic.position, card.cardPic.size)
                    card.selected = False

                # if a card has been clicked, select it
                elif card.cardPic._rect.collidepoint(event.pos):
                    card.selected = True

        # in the case of cards overlapping multiple cards will be selected
        # by going through in reverse order we can select the actual card clicked
        for card in self.userCards.__reversed__():
            if card.selected == True and cardSelected == False:
                card.cardPic.position = (card.cardPic.position[0], card.cardPic.position[1] - 50)
                card.cardPic._rect = pygame.Rect(card.cardPic.position, card.cardPic.size)
                cardSelected = True

            elif card.selected:
                card.selected = False

        return cardSelected

    # display all cards in the current trick in the center of the screen
    def displayTrick(self, currentTrick, players):
        trickSize = currentTrick.__len__()
        myfont = pygame.font.SysFont("Times New Roman", 20)

        if trickSize != 1:
            if trickSize % 2 == 0:
                offset = -65 * (trickSize - 1)
            else:
                offset = -130

        else:
            offset = 0

        for card in currentTrick:
            card.cardPic = cardDeck.cardGraphic((450 + offset, 200), (100, 151), card.cardID, 'CARDS')
            card.cardPic.draw(self.gameWindow)

            message = players[card.owner].name  # + str(card.owner)
            textsurface = myfont.render(message, False, (255, 255, 255))
            self.gameWindow.blit(textsurface, (450 + offset, 175))

            offset += 130

    def displayTrump(self, trumpCard):
        myfont = pygame.font.SysFont("Times New Roman", 20)
        text = myfont.render("Trump", False, (255, 255, 255))
        self.gameWindow.blit(text, (900, 20))

        trumpPNG = pygame.image.load(os.path.join('CARDS', trumpCard.cardID + ".png"))
        newPNG = pygame.transform.scale(trumpPNG, (60, 90))
        self.gameWindow.blit(newPNG, (900, 45))

    def displaySelectTrump(self):

        myfont = pygame.font.SysFont("Times New Roman", 20)
        offset = -195
        S = cardDeck.card("spade", -1, "0")
        C = cardDeck.card("club", -1, "1")
        H = cardDeck.card("heart", -1, "2")
        D = cardDeck.card("diamond", -1, "3")

        for i in range(4):
            if i == 0:
                suit = "spade"
            elif i == 1:
                suit = "club"
            elif i == 2:
                suit = "heart"
            else:
                suit = "diamond"

            newCard = cardDeck.card(suit, -1, str(i))

            newCard.cardPic = cardDeck.cardGraphic((450 + offset, 200), (100, 151), newCard.cardID, 'CARDS')
            newCard.cardPic.draw(self.gameWindow)

            text = myfont.render(str(i + 1), False, (255, 255, 255))
            self.gameWindow.blit(text, (455 + offset, 175))

            newCard.cardPic = None
            self.suits.append(newCard)

            offset += 130


    def addMessages(self, message):
        self.messages.append(message)
        if self.messages.__len__() > 10:
            self.messages.remove(self.messages[0])

    def changeMessages(self, message):
        self.messages.pop()
        self.messages.append(message)

    def displayMessages(self):

        baseHeight = 580
        pygame.draw.rect(self.gameWindow, (0, 0, 0), self.rect)

        myfont = pygame.font.SysFont("Times New Roman", 15)

        for message in self.messages.__reversed__():
            textsurface = myfont.render(message, False, (255, 255, 255))
            self.gameWindow.blit(textsurface, (5, baseHeight))
            baseHeight -= 15

    def updateScoreCard(self, gameScoreCard):
        regFont = pygame.font.SysFont("Times New Roman", 18)
        smallFont = pygame.font.SysFont("Times New Roman", 11)

        baseHeight = 140
        for row in gameScoreCard.rows[-4:].__reversed__():
            baseWidth = 305

            # display the round number
            rnd = regFont.render(str(row.round), False, (0, 0, 0))
            self.gameWindow.blit(rnd, (263, baseHeight))

            # display the bids
            bidHeight = baseHeight - 2
            bidWidth = baseWidth + 45
            for bid in row.bids:
                if bid != -1:
                    bidtxt = smallFont.render(str(bid), False, (0, 0, 0))
                    self.gameWindow.blit(bidtxt, (bidWidth, bidHeight))
                bidWidth += 77

            # display the tricks taken
            trickHeight = baseHeight + 14
            trickWidth = baseWidth + 45
            for trick in row.tricksTaken:
                if trick != -1:
                    tricktxt = smallFont.render(str(trick), False, (0, 0, 0))
                    self.gameWindow.blit(tricktxt, (trickWidth, trickHeight))
                trickWidth += 77

            # display the scores
            for score in row.scores:
                scoretxt = regFont.render(str(score), False, (0, 0, 0))
                self.gameWindow.blit(scoretxt, (baseWidth, baseHeight))
                baseWidth += 77

            baseHeight -= 31

    def redrawWindow(self, game, player):
        # draw the background of the client
        tablepng = pygame.image.load("table.jpg")
        tableModified = pygame.transform.scale(tablepng, (self.width, self.height))
        self.gameWindow.blit(tableModified, (0, 0))

        # draw the text box
        self.rect = (0, self.height - self.tbHeight, self.tbWidth, self.tbHeight)
        pygame.draw.rect(self.gameWindow, (0, 0, 0), self.rect)

        # display the score card
        score2png = pygame.image.load("scoreBox.png")
        self.gameWindow.blit(score2png, (250, 5))

        # display the player name
        pFont = pygame.font.SysFont("Times New Roman", 30)
        # message = "You are player " + str(player)
        message = "You are " + game.players[player].name
        pDescription = pFont.render(message, False, (255, 255, 255))
        self.gameWindow.blit(pDescription, (5, 5))

        # display the player names on the scorecard
        pFont = pygame.font.SysFont("Times New Roman", 18)
        baseWidth = 298
        for i in range(game.numPlayers):
            # message = "Player " + str(i)
            message = game.players[i].name
            pDescription = pFont.render(message, False, (0, 0, 0))
            self.gameWindow.blit(pDescription, (baseWidth, 10))
            baseWidth += 77

        # if 3 players are not yet connected
        if not(game.connected()):
            myfont = pygame.font.SysFont("Times New Roman", 80)
            text = myfont.render("Waiting for more players...", False, (255, 255, 255))
            self.gameWindow.blit(text, (100, 200))

    def displayWinner(self, game):
        winner = game.players[0]
        for player in game.players[1:]:
            if player.score > winner.score:
                winner = player

        myfont = pygame.font.SysFont("Times New Roman", 80)
        message = winner.name + " is the winner!"
        text = myfont.render(message, False, (255, 255, 255))
        self.gameWindow.blit(text, (100, 200))



def main():
    run = True
    dispOnce = 0
    clock = pygame.time.Clock()
    n = network()
    player = int(n.getP())
    print("You are player", player)

    window = gameClient()

    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False

        # get game from server
        try:
            game = n.send("get")
        except Exception as e:
            run = False
            print("Couldn't get game")
            print(e)
            break

        # if the max number of round have been completed, end the game
        if game.round > game.maxRound:
            run = False
            break

        if game.connected():

            # check player so the deck is only created and dealt once
            # otherwise each player would create and deal a deck
            # should happen once per hand i.e. each time cards are dealt
            if not game.isDealt and player == 1:
                game.createDeck()
                game.deal()
                game.isDealt = True

                # send the game to the server so other players can pull the dealt deck
                game = n.send(game)

            if game.isDealt:

                if game.round == 1:
                    window.addMessages("Welcome to Wizard!")

                window.addMessages("Commencing Round " + str(game.round) + "...")
                window.redrawWindow(game, player)
                window.displayMessages()
                window.updateScoreCard(game.scoreCard)
                pygame.display.update()
                time.sleep(1)
                window.addMessages(game.players[game.dealer].name + " is dealer.")
                window.displayMessages()
                pygame.display.update()
                time.sleep(2)

                window.createCardPic(game.players[player].playerCards)

                # if trump is a wizard, a suit needs to be chosen for trump
                if game.trump.cardID == "W":
                    if player == game.dealer:
                        window.addMessages("Please select a suit to be trump (1 - 4)")
                        window.displayTrump(game.trump)
                        window.displaySelectTrump()
                        window.displayCards()
                        window.displayMessages()
                        pygame.display.update()

                        # wait for a key to be pressed corresponding to the trump selection
                        pygame.event.clear()
                        event = pygame.event.wait()
                        while event.type != pygame.KEYDOWN:
                            event = pygame.event.wait()

                        key = int(chr(event.key))
                        game.trump = window.suits[key - 1]
                        game = n.send(game)

                    else:
                        window.addMessages("Please wait while the dealer selects trump.")
                        window.displayMessages()
                        window.displayTrump(game.trump)
                        window.displayCards()
                        pygame.display.update()
                        while game.trump.cardID == "W":
                            game = n.send("get")

                # display to users who's turn it is to bid
                if game.currentPlayer != player:
                    window.addMessages("Waiting for " + game.players[game.currentPlayer].name + " to bid...")

                #window.createCardPic(game.players[player].playerCards)

                # one time display's after cards have been dealt
                window.redrawWindow(game, player)
                window.displayCards()
                window.displayTrump(game.trump)
                window.displayMessages()
                window.updateScoreCard(game.scoreCard)
                pygame.display.update()

                # BIDDING PHASE
                while game.biddingPhase:

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            run = False

                    # once each person bids the game will need updating for the other players
                    try:
                        game = n.send("get")
                    except Exception as e:
                        run = False
                        print("Couldn't get game")
                        print(e)
                        break

                    window.redrawWindow(game, player)
                    window.displayCards()
                    window.displayTrump(game.trump)
                    window.displayMessages()
                    window.updateScoreCard(game.scoreCard)
                    pygame.display.update()

                    # update global messages
                    while game.globalMsg.__len__() != window.numGlobal:
                        message = game.globalMsg[window.numGlobal]
                        if message[1] != player:
                            window.addMessages(message[0])
                        window.numGlobal += 1

                        window.displayMessages()
                        pygame.display.update()

                    # player's that don't bid last will be inside loop even after bidding phase ends
                    if not game.biddingPhase:
                        break

                    # if it is this player client's turn
                    if game.currentPlayer == player:
                        # ask them to enter their bid
                        window.addMessages("Please enter your bid: ")
                        window.displayMessages()
                        pygame.display.update()

                        # clear the events and wait for a keydown event
                        # TODO: make hitting enter necessary to continue (as of now only single digit bids are possible)
                        pygame.event.clear()
                        event = pygame.event.wait()
                        while event.type != pygame.KEYDOWN:
                            event = pygame.event.wait()

                        # try in case a non-number is entered in which case the user is warned to enter a number
                        try:
                            # obtain the key value of the event and make it the players bid and print it to the screen
                            game.players[player].bid = int(chr(event.key))
                            game.scoreCard.rows[game.round - 1].bids[player] = (int(chr(event.key))) # NEW
                            game.scoreCard.rows[game.round - 1].tricksTaken[player] = 0 # NEW
                            window.changeMessages("Please enter your bid: " + chr(event.key))
                            window.displayMessages()
                            pygame.display.update()
                            game.bids += 1

                            game.currentPlayer = (game.currentPlayer + 1) % game.numPlayers

                            # check here because we need the last player to bid to update the server
                            if game.bids == game.numPlayers:
                                game.biddingPhase = False
                                game.playPhase = True

                            else:
                                game.globalMsg.append(("Waiting for " + game.players[game.currentPlayer].name + " to bid...",
                                                          game.currentPlayer))

                            game.globalMsg.append(
                                (game.players[player].name + " has bid " + str(game.players[player].bid), player))

                            game.currentTrick.clear()
                            game = n.send(game)

                        except:
                            window.addMessages("Please enter a number.")
                            window.displayMessages()
                            pygame.display.update()

                if game.currentPlayer != player:
                    window.addMessages("Waiting for " + game.players[game.currentPlayer].name + " to play...")
                    window.displayMessages()
                    pygame.display.update()

                # *********** PLAY PHASE ************
                while game.playPhase:

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            run = False

                    # once each person bids the game will need updating for the other players
                    try:
                        game = n.send("get")
                    except Exception as e:
                        run = False
                        print("Couldn't get game")
                        print(e)
                        break

                    # if a card has been added to the current trick copy it to the client side
                    if game.currentTrick.__len__() != window.trick.__len__():
                        window.trick = copy.deepcopy(game.currentTrick)

                    # if the first play has been made, update users hands to show which cards can be played
                    # i.e. by following suit
                    if game.playCount != 0 and game.leadingSuit != "none":
                        haveSuit = False
                        for card in window.userCards:
                            if card.suit == game.leadingSuit:
                                haveSuit = True

                        if haveSuit:
                            for card in window.userCards:
                                if not card.suit == game.leadingSuit and card.suit != "none" and "G" not in card.cardID:
                                    card.cardID = card.cardID + "G"
                                    card.cardPic = cardDeck.cardGraphic(card.cardPic.position, card.cardPic.size,
                                                                        card.cardID, 'CARDS_GREY')

                    # TODO: fix, currently crashes game
                    # reset any grey cards if its a new trick
                    elif game.playCount == 0:
                        for card in window.userCards:
                            if "G" in card.cardID:
                                card.cardID = card.cardID[:-1]
                                card.cardPic = cardDeck.cardGraphic(card.cardPic.position, card.cardPic.size,
                                                                    card.cardID, 'CARDS')

                    window.redrawWindow(game, player)
                    window.displayTrump(game.trump)
                    window.displayTrick(window.trick, game.players)
                    window.displayCards()
                    window.displayMessages()
                    window.updateScoreCard(game.scoreCard)
                    pygame.display.update()

                    # update global messages
                    while game.globalMsg.__len__() != window.numGlobal:
                        message = game.globalMsg[window.numGlobal]
                        if message[1] != player:
                            window.addMessages(message[0])
                        window.numGlobal += 1

                        window.displayMessages()
                        pygame.display.update()

                    # if the trick is completed, determine who won and
                    if game.trickCompleted:
                        winningCard = game.determineTrick(game.trump)

                        if player == 1:

                            game.tricks += 1

                            # display who won to everyone
                            window.addMessages("The winner of the trick is " + game.players[winningCard.owner].name)
                            window.displayMessages()
                            pygame.display.update()

                            # change the current player to the winner of the trick
                            game.currentPlayer = game.players[winningCard.owner].playerID

                            if game.tricks != game.round:
                                game.globalMsg.append(
                                    ("Waiting for " + game.players[game.currentPlayer].name + " to play...",
                                     game.currentPlayer))

                            game.players[game.currentPlayer].tricksTaken += 1
                            game.scoreCard.rows[game.round - 1].tricksTaken[game.currentPlayer] += 1 # NEW

                            game.trickCompleted = False
                            game.currentTrick.clear()

                            game = n.send(game)

                            time.sleep(3)

                        elif dispOnce == 0:
                            window.addMessages("The winner of the trick is " + game.players[winningCard.owner].name)
                            window.displayMessages()
                            pygame.display.update()
                            dispOnce = 1
                            time.sleep(3)

                        window.trick.clear()
                        window.redrawWindow(game, player)
                        window.displayTrump(game.trump)
                        window.displayTrick(window.trick, game.players)
                        window.displayCards()
                        window.displayMessages()
                        window.updateScoreCard(game.scoreCard)
                        pygame.display.update()


                    # if the number of tricks is equivalent to the round number, i.e. num of cards dealt
                    # then the play phase is over
                    if game.tricks == game.round and player == 1:

                        # determine the score
                        # note: this function resets players, tricksTaken, and cards
                        game.determineScore()

                        # increment the round, reset the tricks, make the play phase false
                        game.round += 1
                        game.tricks = 0
                        game.playPhase = False

                        game = n.send(game)

                    # if it is this player client's turn and the trick is not over
                    if game.currentPlayer == player and not game.trickCompleted and game.playPhase \
                            and game.tricks != game.round:
                        dispOnce = 0

                        window.addMessages("Click the card you would like to play, then hit enter.")
                        window.displayMessages()
                        pygame.display.update()

                        # wait for enter key to confirm selection
                        pygame.event.clear()
                        event = pygame.event.wait()

                        # TODO: make sure user has selected a card as well
                        while event.type != pygame.KEYDOWN:
                            selection = False
                            event = pygame.event.wait()
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                if event.button == 1:
                                    selection = window.cardSelection(event)

                            # update players hand
                            window.redrawWindow(game, player)
                            window.displayTrump(game.trump)
                            window.displayTrick(window.trick, game.players)
                            window.displayCards()
                            window.displayMessages()
                            window.updateScoreCard(game.scoreCard)
                            pygame.display.update()

                        # past this point the player has gone
                        # remove the card from the players hand and add it to the current trick
                        for card in window.userCards:
                            if card.selected:

                                # TODO: check if jester was led -> next card played is leading suit
                                # if this is the first card played it's suit is the leading suit
                                if game.playCount == 0:
                                    game.leadingSuit = card.suit

                                window.userCards.remove(card)

                                # append the card with the card pic to client side "trick" variable
                                window.trick.append(card)

                                # reset the card pic so that it can be sent via pickle
                                card.cardPic = None
                                game.currentTrick.append(card)

                                # this player's turn is done; update the current player
                                game.currentPlayer = (game.currentPlayer + 1) % game.numPlayers

                                game.playCount += 1

                                # if all players have played a card
                                if game.playCount == game.numPlayers:
                                    game.playCount = 0
                                    game.trickCompleted = True

                                else:
                                    # send this so the messages update with who the play is waiting on
                                    game.globalMsg.append(
                                        ("Waiting for " + game.players[game.currentPlayer].name + " to play...",
                                         game.currentPlayer))

                                # send the updates
                                game = n.send(game)

                                # redraw everything
                                window.redrawWindow(game, player)
                                window.displayTrump(game.trump)
                                window.displayTrick(window.trick, game.players)
                                window.displayCards()
                                window.displayMessages()
                                window.updateScoreCard(game.scoreCard)
                                pygame.display.update()

        # if both the bid phase and play phase are over the hand is complete
        if not game.biddingPhase and not game.playPhase and player == 1:

            # display who won to everyone
            game.globalMsg.append(("The hand is over.", -1))

            # prepare the next hand
            game.biddingPhase = True
            game.isDealt = False
            game.bids = 0
            game.dealer = (game.dealer + 1) % game.numPlayers
            game.currentPlayer = (game.dealer + 1) % game.numPlayers
            game.currentTrick.clear()
            game = n.send(game)

        window.redrawWindow(game, player)
        window.updateScoreCard(game.scoreCard)
        window.displayMessages()
        pygame.display.update()

        # update global messages
        while game.globalMsg.__len__() != window.numGlobal:
            message = game.globalMsg[window.numGlobal]
            if message[1] != player:
                window.addMessages(message[0])
            window.numGlobal += 1

            window.displayMessages()
            pygame.display.update()
            time.sleep(3)

    window.redrawWindow(game, player)
    window.updateScoreCard(game.scoreCard)
    window.displayMessages()
    window.displayWinner(game)
    pygame.display.update()
    time.sleep(5)
    window.addMessages("Terminating Game... Goodbye!")
    window.displayMessages()
    pygame.display.update()
    time.sleep(2)

def menu_screen():
    width = 700
    height = 700
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Client")
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        win.fill((128, 128, 128))
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Click to Play!", 1, (255,0,0))
        win.blit(text, (100,200))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

    main()

while True:
    menu_screen()