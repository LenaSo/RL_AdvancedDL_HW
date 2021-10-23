import gym
from gym import spaces
from gym.utils import seeding

# original: https://github.com/openai/gym/blob/master/gym/envs/toy_text/blackjack.py

def cmp(a, b):
    return float(a > b) - float(a < b)


def draw_card(np_random, deck):
    card = int(np_random.choice(deck))
    deck.remove(card)
    return card


def draw_hand(np_random, deck):
    return [draw_card(np_random, deck), draw_card(np_random, deck)]


def usable_ace(hand):  # Does this hand have a usable ace?
    return 1 in hand and sum(hand) + 10 <= 21


def sum_hand(hand):  # Return current hand total
    if usable_ace(hand):
        return sum(hand) + 10
    return sum(hand)


def is_bust(hand):  # Is this hand a bust?
    return sum_hand(hand) > 21


def score(hand):  # What is the score of this hand (0 if bust)
    return 0 if is_bust(hand) else sum_hand(hand)


def is_natural(hand):  # Is this hand a natural blackjack?
    return sorted(hand) == [1, 10]


class DoubleBlackjackWithCntEnv(gym.Env):
    def __init__(self):
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Tuple(
            (spaces.Discrete(32), spaces.Discrete(11), spaces.Discrete(2))
        )
        self.seed()
        # 1 = Ace, 2-10 = Number cards, Jack/Queen/King = 10
        self.deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] * 4

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        assert self.action_space.contains(action)
        if action == 2:
            state, reward, done, info = self.step(1)
            if not done:
                state, reward, done, info = self.step(0)
            reward *= 2
        elif action == 1:  # hit: add a card to players hand and return
            self.player.append(draw_card(self.np_random, self.deck))
            if is_bust(self.player):
                done = True
                reward = -1.0
            else:
                done = False
                reward = 0.0
        else:  # stick: play out the dealers hand, and score
            done = True
            while sum_hand(self.dealer) < 17:
                self.dealer.append(draw_card(self.np_random, self.deck))
            reward = cmp(score(self.player), score(self.dealer))
            if is_natural(self.player) and not is_natural(self.dealer):
                # Player automatically wins. Rules consistent with S&B
                reward = 1.5

        return self._get_obs(), reward, done, {}
        
    def _get_obs(self):
        return (sum_hand(self.player), self.dealer[0], usable_ace(self.player), self.deck_cnt)
    

    def reset(self):
        if len(self.deck) < 15:
            self.deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] * 4
            
        d = [11 if card == 1 else card for card in self.deck] 
        self.deck_cnt = int(round( 3 * sum(d) / len(d) ))
        
        self.dealer = draw_hand(self.np_random, self.deck)
        self.player = draw_hand(self.np_random, self.deck)
        return self._get_obs()