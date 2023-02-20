import random

CARDS_SUITS = ('S', 'D', 'C', 'H')
CARD_RANKS = {'2': 1, '3': 2, '4' : 3, '5' : 4, '6' : 5, '7' : 6, '8' : 7, '9' : 8, '10' : 9, 'J' : 10, 'Q' : 11,
 'K' : 12, 'A': 13}

def deal_cards(generated):
    """this function only generates num_of_cards sets of cards and returns them to the thread nothing more"""
    player_card = random.choice(list(CARD_RANKS)) + random.choice(CARDS_SUITS)
    while player_card in generated:
        player_card = random.choice(list(CARD_RANKS)) + random.choice(CARDS_SUITS)
    #we generated a new couple. (a third of heaven for us yay!)
    dealer_card = random.choice(list(CARD_RANKS)) + random.choice(CARDS_SUITS)
    while dealer_card in generated:
        dealer_card = random.choice(list(CARD_RANKS)) + random.choice(CARDS_SUITS)
    #we generated another couple. (another third of heaven for us yay!)
    return player_card, dealer_card

def main():
    generated = ()
    for _ in range(3):
        generated += deal_cards(generated)
    print(len(generated))

if __name__ == "__main__":
    main()