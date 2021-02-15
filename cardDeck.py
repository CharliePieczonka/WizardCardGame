from random import randint
import pygame
import os


class card:

    # a card has a suit, value, and a bool for in the deck or not
    # imgName added for later use of assigning each card an image of that card
    def __init__(self, suit, value, cardID):
        self.suit = suit
        self.value = value
        self.cardID = cardID
        self.owner = -1
        self.selected = False

class cardDeck:

    def __init__(self):

        # create a list to hold all of the cards in the deck
        self.cards = []
        
        # initialize the deck size as 60
        self.deckSize = 60

        # populate the deck of cards
        # values are 2 through 14; 11 = jack, 12 = queen, 13 = king, 14 = ace
        for i in range(13):
            self.cards.append(card("spade", i+2, str(i+2) + "S"))
        for i in range(13):
            self.cards.append(card("club", i+2, str(i+2) + "C"))
        for i in range(13):
            self.cards.append(card("heart", i+2, str(i+2) + "H"))
        for i in range(13):
            self.cards.append(card("diamond", i+2, str(i+2) + "D"))

        # value of 0 for jesters
        for i in range(4):
            self.cards.append(card("none", 0, "E"))

        # value of 15 for wizards
        for i in range(4):
            self.cards.append(card("none", 15, "W"))

    def randomCard(self):
        # generate a random value between 0 and the deck size
        value = randint(0, self.deckSize-1)
        randCard = self.cards[value]
        
        # remove the card from the deck, and decrement the deck size
        self.cards.remove(randCard)
        self.deckSize -= 1

        # return the random card
        return randCard

class cardGraphic:
    def __init__(self, position, size, cardID, folder):
        cardPNG = pygame.image.load(os.path.join(folder, cardID + ".png"))
        self.resizedPNG = pygame.transform.scale(cardPNG, size) # size = 100, 151
        self._rect = pygame.Rect(position, size)
        self.position = position
        self.size = size

    def draw(self, screen):
        screen.blit(self.resizedPNG, self.position)





