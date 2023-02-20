import socket
import threading
import random

CARDS_SUITS = ('S', 'D', 'C', 'H')
CARD_RANKS = {'2': 1, '3': 2, '4' : 3, '5' : 4, '6' : 5, '7' : 6, '8' : 7, '9' : 8, '10' : 9, 'J' : 10, 'Q' : 11,
 'K' : 12, 'A': 13}
MAX_CONNECTIONS = 3
#3 beacuse the main is considered as a thread
CONNECTED = 0
def Thread_handler(client_socket, address):
    """the card are generated in couple (player_card, dealer_card) every pair is a round"""
    global CONNECTED
    global MAX_CONNECTIONS
    #if there are too many players
    if CONNECTED >= MAX_CONNECTIONS:
        client_socket.send(bytes("Deny\nEND", "utf-8"))
        return
    total_bets = 0
    total_earned = 0
    current_bet = 0
    round = 1
    case_winner = 0
    player_card = ""
    dealer_card = ""
    generated_cards = ()
    print (f"currently there are {CONNECTED} players connected. the max amount is: {MAX_CONNECTIONS}\n")
    #maybe critical section
    #generate a player's card and add it to the cards we already used
    player_card = deal_card(generated_cards)
    generated_cards += tuple(player_card)
    #generate a dealers card and add it to the cards we already used
    dealer_card = deal_card(generated_cards)
    generated_cards += tuple(dealer_card)  
    client_socket.send(bytes(f"Accept, {player_card}\nEND","utf-8"))
    while True:
        #we dealt all of the cards or we 
        if len(generated_cards) == 52:
            winner = "Player" if net_worth(total_bets, total_earned)>0 else "Dealer"
            client_socket.send(bytes(f"The game has ended!\n\
            {net_worth(total_bets, total_earned)}$\n\
            {winner} is the winner!\n\
            Would you like to play again?\nEND","utf-8"))
            booly = recive_from_client(client_socket, round, total_bets,total_earned)
            if booly == True:
            #--------------true means the player wanna go again--------------
                generated_cards = ()
                continue
            else:
                break
        #reciving the bet
        current_bet = recive_from_client(client_socket, round, total_bets,total_earned)
        total_bets += current_bet
        case_winner = check_winner(player_card, dealer_card)
        # if player_card rank is higher than the dealers
        if case_winner == 1:
            current_bet = current_bet*2
            total_earned += current_bet
            client_socket.send(bytes(f"The result of round {round}:\n\
            Player won: {current_bet}$\n\
            Dealer\'s card: {dealer_card}\n\
            Player\'s card: {player_card}\nEND","utf-8"))
        #if the dealer card is higher
        elif case_winner == 2:
            client_socket.send(bytes(f"The result of round {round}:\n\
            Dealer won: {current_bet}$\n\
            Dealer\'s card: {dealer_card}\n\
            Player\'s card: {player_card}\nEND","utf-8"))
        #if the ranks are equal go to war *diabolical laughter*
        else:
            client_socket.send(bytes(f"The result of round {round} is a tie!\n","utf-8"))
            client_socket.send(bytes(f"Dealer\'s card: {dealer_card}\n\
            Player\'s card: {player_card}\n\
            The bet: {current_bet}$\n\
            Do you wish to surrender or go to war?END\n","utf-8"))
            replay = recive_from_client(client_socket, round, total_bets, total_earned)
            #if the player wishes to go to war
            if replay == "war" or replay == "War":
                total_bets += current_bet
                #we add current_bet again beacause the player had to double the bet 
                #so the total he bet also increase by current_bet
                doubled_bet = current_bet * 2
                client_socket.send(bytes(f"Round {round} tie breaker:\n\
                Going to war!\n\
                3 cards were discarded.\n\
                Original bet: {current_bet}$\n\
                New bet: {doubled_bet}$\nEND","utf-8"))
                #dicard 3 cards
                for _ in range(3):
                    generated_cards += tuple(deal_card(generated_cards))
                #deal 1 card for the player
                player_card = deal_card(generated_cards)
                generated_cards += tuple(player_card)
                #deal 1 card for the dealer
                dealer_card = deal_card(generated_cards)
                generated_cards += tuple(dealer_card)
                case_winner = check_winner(player_card, dealer_card)
            #-------check who won------------
                if case_winner == 1:
                    #player won his original bet
                    client_socket.send(bytes(f"Player won: {current_bet}$\n\
                    Dealer\'s card: {dealer_card}\n\
                    Player\'s card: {player_card}\nEND","utf-8"))
                    total_earned += current_bet
                elif case_winner == 2:
                    #dealer won doubled bet
                    client_socket.send(bytes(f"Dealer won: {doubled_bet}$\n\
                    Dealer\'s card: {dealer_card}\n\
                    Player\'s card: {player_card}\nEND","utf-8"))
                else:
                    #the ranks are equal, player wins doubled bet
                    client_socket.send(bytes(f"Player won: {doubled_bet}$\n\
                    Dealer\'s card: {dealer_card}\n\
                    Player\'s card: {player_card}\nEND","utf-8"))
                    total_earned += doubled_bet               
            #if the player wishes to surrender this round
            elif replay == "surrender" or replay == "Surrender" :
                total_earned += current_bet/2
                client_socket.send(bytes(f"Round {round} tie breaker:\n\
                Player surrendered!\n\
                The bet: {current_bet}$\n\
                Dealer won: {current_bet/2}$\n\
                Player won: {current_bet/2}$\nEND","utf-8"))
        #---------------------------the start of a new round----------------------------------
        #deal a players card
        player_card = deal_card(generated_cards)
        generated_cards += tuple(player_card)
        #deal a dealers card
        dealer_card = deal_card(generated_cards)
        generated_cards += tuple(dealer_card)
        client_socket.send(bytes(f"Your card is {player_card}\n\
        Please enter your bet\nEND","utf-8"))
        round += 1
    print(f"terminating connection: {address[0]}:{address[1]}")
    CONNECTED -= 1
    client_socket.close()

def deal_card(generated):
    """this function only generates 1 set of cards and returns it to the thread nothing more"""
    card = random.choice(list(CARD_RANKS)) + random.choice(CARDS_SUITS)
    while card in generated:
        card = random.choice(list(CARD_RANKS)) + random.choice(CARDS_SUITS)
    #we generated a new couple. (a third of heaven for us yay!)
    return card

def recive_from_client(client_socket, round, total_bets, total_earned):
    """this function deals with the recived msg from the client for contiuoed process
    and send the end result to the thread"""
    msg = ""
    msg = client_socket.recv(1024).decode("utf-8")
    try:
        msg = int(msg)
    except:
        if msg == "status" or msg == "Status":
            client_socket.send(bytes(f"Current round: {round}\n\
            {net_worth(total_bets, total_earned)}\nEND", "utf-8"))
        elif msg == "quit":
            client_socket.send(bytes(f"The game has ended on round {round}!\n\
            The player quit.\n\
            {net_worth(total_bets, total_earned)}\n\
            Thanks for playing.\nexitEND", "utf-8"))
            return False
        elif msg == 'Yes' or msg == 'yes':
            return True
        else:
            return msg
    return msg

def net_worth(total_bets, total_earned):
    if total_earned == 0:
        return f"Player lost: {total_bets}$"
    else:
        return f"Player won: {total_earned}$"

def check_winner(player_card, dealer_card):
    """this function figures out who won in the battle of ranks by extracting 
    the card number and sending it to the rank table
    then it well compare the two and return who won or if the are the same"""
    player_rank = ""
    dealer_rank = ""
    if len(player_card) == 3:
        player_rank = player_card[:-1]
    else:
        player_rank = player_card[0]
    if len(dealer_card) == 3:
        dealer_rank = dealer_card[:-1]
    else:
        dealer_rank = dealer_card[0]
    if CARD_RANKS[player_rank] > CARD_RANKS[dealer_rank]:
        return 1
    elif CARD_RANKS[player_rank] < CARD_RANKS[dealer_rank]:
        return 2
    else:
        #they are the same
        #we can return any number we want
        return 3

def main():
    global CONNECTED
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("a new socket was created")
    server_socket.bind((socket.gethostname(), 8888))
    print(f"bound to: {socket.gethostname()}:8888")
    while True:
    #listen to new players
        server_socket.listen(5)
        client_socket, address = server_socket.accept()
        CONNECTED += 1
        print(f"recivied connection from: {address[0]}:{address[1]}")
        threading.Thread(target = Thread_handler,args = (client_socket, address)).start()
    server_socket.close()

if __name__ == "__main__":
    main()