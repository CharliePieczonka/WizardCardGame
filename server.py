import socket
from _thread import *
import pickle
import game

# AS THE HOST, CHANGE THIS VALUE TO YOUR COMPUTER'S IPv4 ADDRESS
server = "192.168.0.26"
# **************************************************************

port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen()
print("Waiting for a connection, Server Started")

# store ip addresses of connected clients
connected = set()

# games dict to be able to run multiple games at once
games = {}

# track id to act as the key for the games dict
idCount = 0

# this runs for every player that connects
def threaded_client(conn, p, gameId):
    # need to access the idCount so that we can disconnect players if one person exits
    # and subtract from it so the games are tracked properly
    global idCount

    # when we connect we send the player client their player number
    conn.send(str.encode(str(p)))

    while True:
        try:
            # receive data from the client
            #data = conn.recv(4096).decode()
            data = pickle.loads(conn.recv(4096*2048))

            # check if the game exists
            if gameId in games:
                # obtain the game from the games dict
                game = games[gameId]

                # if theres no data then break
                if not data:
                    break

                # otherwise process data
                else:

                    # send the entire game with a pickle object
                    # (if its just get this is all that will occur)
                    if data == "get":
                        conn.sendall(pickle.dumps(game))

                    # else the client is sending their game to the server
                    # thus update the server game to match the client game
                    # so when other clients load the game its updated
                    else:
                        games[gameId] = data
                        conn.sendall(pickle.dumps(games[gameId]))

            # if game is not in game dict
            else:
                break

        # if anything goes wrong while in the try
        except:
            break

    # if something goes wrong or game doesnt exist
    print("Lost connection")
    try:
        # try to delete the game
        del games[gameId]
        print("Closing Game", gameId)
    except:
        pass

    # decrement the idcount and close the connection
    idCount -= 1
    conn.close()

# numPlayers = integer value
# names = a list of player names
def server(numPlayers, playerNames, maxRound):
    # create new games as people connect
    global idCount
    while True:

        # WAITS for a person to connect, does not continue until a connection occurs
        conn, addr = s.accept()
        print("Connected to:", addr)

        # once we have a connection:
        # increment our id count, keeps track of amount of people connected
        idCount += 1

        # current player
        p = 0

        # every "numPlayers" people that connect we increment gameID by 1
        gameId = (idCount - 1) // numPlayers

        # start a new game every 2 people
        if idCount % numPlayers == 1:

            # create a game with id = gameId, and store it in the game dict
            games[gameId] = game.game(numPlayers, playerNames, maxRound)
            print("Creating a new game...")

        # if this is the "numPlayers"-ith player, we start the game
        elif idCount % numPlayers == 0:
            games[gameId].ready = True
            p = idCount - 1

        # else its not the first or last player to join, so just start a thread for them
        else:
            p = idCount - 1

        # p = player number, gameId = the game they get connected to
        start_new_thread(threaded_client, (conn, p, gameId))

# TODO: have each user put in their name from the client side and send it to the server to update game.players.name
# TODO: potentially have the first user to connect specify number of players too
# as is all games will have 4 players and the same names
#server(4, ["Charlie", "Jan", "Sam", "Chris"])
server(2, ["player1", "player2"], 3)

# # create new games as people connect
# while True:
#
#     # WAITS for a person to connect, does not continue until a connection occurs
#     conn, addr = s.accept()
#     print("Connected to:", addr)
#
#     # once we have a connection:
#     # increment our id count, keeps track of amount of people connected
#     idCount += 1
#
#     # current player
#     p = 0
#
#     # every 2 people that connect we increment gameID by 1
#     gameId = (idCount - 1)//2
#
#     # start a new game every 2 people
#     if idCount % 2 == 1:
#
#         # create a game with id = gameId, and store it in the game dict
#         games[gameId] = game.game(2)
#         print("Creating a new game...")
#
#     # elif idCount % 3 == 2:
#     #     # player 2
#     #     p = 1
#
#     else:
#         # if we have an even number of people, we have 2 players ready for a game
#         # so set the ready status of the game to true
#         games[gameId].ready = True
#
#         # make this player p3
#         p = 1
#
#     # p = 0 or 1 depending on player number,
#     start_new_thread(threaded_client, (conn, p, gameId))
