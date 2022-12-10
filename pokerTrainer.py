#Poker Odds Trainer made with python using Streamlit Framework
import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import numpy as np
import random
import pokerTrainerBackend

st.title('Poker Odds Trainer')

#generate hash number to represent each suit and rank in a list
_SUITS = [1 << (i + 12) for i in range(4)]
_RANKS = [(1 << (i + 16)) | (i << 8) for i in range(13)]

#13 prime numbers used for each rank in the hash function
_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

#create list of tuples to represent every possible card i.e. 4 suits combined with 13 ranks
cartesianProduct = [(a, b) for a in range(13) for b in range(4)]

#genrate a deck of 52 cards using the hash numbers that represent each card
_DECK = [_RANKS[rank] | _SUITS[suit] | _PRIMES[rank] for rank, suit in cartesianProduct]

#create the game deck built from readable cards
GameSuits = 'CDHS'
GameRanks = '23456789TJQKA'
GameDeck = [''.join(s) for s in [(a, b) for a in GameRanks for b in GameSuits]]

#create dictionary to map game card with hash number
lookUpTable = dict(zip(GameDeck, _DECK))

def hash_function(x):
    # hash function written by Cactus Kev in C
    x += 0xe91aaa35
    x ^= x >> 16
    x += x << 8
    x &= 0xffffffff
    x ^= x >> 4
    b = (x >> 8) & 0x1ff
    a = (x + (x << 2)) >> 19
    r = (a ^ pokerTrainerBackend.HASH_ADJUST[b]) & 0x1fff
    return pokerTrainerBackend.HASH_VALUES[r]

def whoWins(hand):
  #create temporary list
  temp = []

  #loop through every combination of 5 cards out of 7 cards (players' 2 and 5 community)
  for i in combinations(hand, 5):
    #create 5 vars to represent the hash number of each card in hand
    c1, c2, c3, c4, c5 = (lookUpTable[x] for x in i)
    #  q equals union of all cards rightshifted by 16
    q = (c1 | c2 | c3 | c4 | c5) >> 16

    #checking for a flush by seing if call cards have the same suit
    if (0xf000 & c1 & c2 & c3 & c4 & c5):
      # flushes table ranks straight flushes and flushes
        temp.append(pokerTrainerBackend.FLUSHES[q])
        break

    #if no flush make a new var s through the unique cards table
    s = pokerTrainerBackend.UNIQUE_5[q]
    # if cards form any staights or are simply highcard hands, the unique_5 array will return its score value
    if s:
        temp.append(s)
        break
    # if not flush and s = 0 we need to calculate the score given by
    # taking each card, extract its prime number value, and then multiply them all together
    p = (c1 & 0xff) * (c2 & 0xff) * (c3 & 0xff) * (c4 & 0xff) * (c5 & 0xff)
    # search this value using binary search algo and hashfunction math
    temp.append(hash_function(p))

  #return the lowest actual score of all combianitons
  #like golf low is better so a royal flush is a 1
  return min(temp)

def combinations(lis, length):
    out = set()
    queue = [((lis[i],), lis[:i]+lis[i+1:]) for i,n in enumerate(lis)]
    while queue:
        comb, remains = queue.pop(0)
        for i, selected in enumerate(remains):
            unselected = remains[:i] + remains[i+1:]
            if selected >= comb[-1]:
                new = comb + (selected,)

                if len(new) == length:
                    out.add(new)
                else:
                    queue.append((new, unselected))
    return out

def runGame(p1Hand, p2Hand):
    # shuffle a deck
    deck = list(GameDeck)
    random.shuffle(deck)
    #remove chosen cards
    playerHand = p1Hand
    deck.remove(p1Hand[0])
    deck.remove(p1Hand[1])
    #assign enemy hand
    enemyHand = p2Hand
    deck.remove(p2Hand[0])
    deck.remove(p2Hand[1])
    # draw community and two hands
    community = deck[:5]

    # evaluate the hands using whoWins func
    score1 = whoWins(community + playerHand)
    score2 = whoWins(community + enemyHand)
    # display the winning hand
    community = '[%s]' % ' '.join(community)
    playerHand = '[%s]' % ' '.join(playerHand)
    enemyHand = '[%s]' % ' '.join(enemyHand)
    if score1 < score2:
        #print('%s beats %s' % (playerHand, enemyHand))
        return 1
    elif score1 == score2:
        #print('%s ties %s' % (playerHand, enemyHand))
        return 1
    else:
        #print('%s beats %s' % (enemyHand, playerHand))
        return 0

if __name__ == '__main__':
    #split screen into 3 columns
    col1, col2, col3 = st.columns([1,1,2.5], gap = 'medium')
    #change gap distance and text allignment CSS
    st.markdown("""
    <style>
    [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
        gap: 0.2rem;
    }
    [data-testid=column]:nth-of-type(2) [data-testid=stVerticalBlock]{
        gap: 0.2rem;
    }
    [data-testid=column]:nth-of-type(3) [data-testid=stVerticalBlock]{
        text-align: center;
        gap: 1rem;
    }
    </style>
    """,unsafe_allow_html=True)

    suitDict = {'Clubs' : 'C', 'Diamonds' : 'D', 'Hearts' : 'H', 'Spades' : 'S'}

    #create player one cards chosen interface
    with col1:
        p1container = st.container()
        p1container.header("Player One")
        st.subheader("Card 1:")
        st.selectbox('Rank', ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'], key = "player1card1rank")
        st.selectbox("Suit:", ['Clubs', 'Diamonds', 'Hearts', 'Spades'], key = "player1card1suit")
        st.subheader("Card 2:")
        st.selectbox('Rank', ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'], key = "player1card2rank")
        st.selectbox("Suit:", ['Clubs', 'Diamonds', 'Hearts', 'Spades'], key = "player1card2suit")
        st.text(" ")
        st.text(" ")
        st.text(" ")
        p1card1img = './Finished Cards/'+ str(st.session_state.player1card1suit[:-1]) + ' ' + str(st.session_state.player1card1rank) + '.png'
        p1card2img = './Finished Cards/'+ str(st.session_state.player1card2suit[:-1]) + ' ' + str(st.session_state.player1card2rank) + '.png'
        p1container.image([p1card1img, p1card2img], width= 120)

    #save player one card choices
    player1Hand = [st.session_state.player1card1rank  + suitDict[st.session_state.player1card1suit], st.session_state.player1card2rank + suitDict[st.session_state.player1card2suit]]

    #create player two cards chosen interface
    with col2:
        p2container = st.container()
        p2container.header("Player Two")
        st.subheader("Card 1:")
        st.selectbox('Rank', ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'], key = "player2card1rank")
        st.selectbox("Suit:", ['Clubs', 'Diamonds', 'Hearts', 'Spades'], key = "player2card1suit")
        st.subheader("Card 2:")
        st.selectbox('Rank', ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'], key = "player2card2rank")
        st.selectbox("Suit:", ['Clubs', 'Diamonds', 'Hearts', 'Spades'], key = "player2card2suit")
        st.text(" ")
        st.text(" ")
        st.text(" ")
        p2card1img = './Finished Cards/'+ str(st.session_state.player2card1suit[:-1]) + ' ' + str(st.session_state.player2card1rank) + '.png'
        p2card2img = './Finished Cards/'+ str(st.session_state.player2card2suit[:-1]) + ' ' + str(st.session_state.player2card2rank) + '.png'
        p2container.image([p2card1img, p2card2img], width= 120)

    #save player two card choices
    player2Hand = [st.session_state.player2card1rank  + suitDict[st.session_state.player2card1suit], st.session_state.player2card2rank + suitDict[st.session_state.player2card2suit]]

    #create column three game interface
    col3.write("By Adam Mualem")
    col3.image('./table.png', width = 700)

    #run game with button and display results 
    if col3.button('Run Game'):
        x = 1000
        sum = 0
        for i in range(x):
            sum += runGame(player1Hand, player2Hand)
        stat = sum * 100 / x

        if stat >= 50:
            col3.subheader('Player One beats Player Two ' + str(stat) + "% of the time")
        else:
            col3.subheader('Player Two beats Player One ' + str(100 - stat) + "% of the time")
