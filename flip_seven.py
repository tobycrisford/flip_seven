from tqdm import tqdm

import pickle

TOTAL_CARDS = 79

CARD_PROBS = {i: i / TOTAL_CARDS for i in range(1, 13)}
CARD_PROBS[0] = 1 / TOTAL_CARDS
print(sum(CARD_PROBS[card] for card in CARD_PROBS))

FLIP_BONUS = 15

LIMIT = 7

class HandStats:

    def __init__(self):
        self.e_score = 0.0
        self.bust_prob = 0.0

    def add_stats(self, score: float, bust: bool, prob: float) -> None:
        self.e_score += score * prob
        if bust:
            self.bust_prob += prob

class StatsLookup:

    def __init__(self):
        self.stats_lookup = {}

    def add_stats(self, key: tuple[int, ...], score: float, bust: bool, prob: float) -> None:
        
        if key not in self.stats_lookup:
            self.stats_lookup[key] = HandStats()

        self.stats_lookup[key].add_stats(score, bust, prob)


    def add_hand(self, hand: list[int], score: float, bust: bool, prob: float) -> None:

        for i in range(len(hand)):
            self.add_stats(tuple(hand[:i+1]), score, bust, prob)

    def get_conditional_stats(self, hand: tuple[int]):

        hand_key = hand
        hand_stats = self.stats_lookup[hand_key]
        hand_prob = 1.0
        for card in hand_key:
            hand_prob *= CARD_PROBS[card]

        hand_sum = sum(hand)
        next_turn_val = 0.0
        next_turn_bust_prob = 0.0
        for card in CARD_PROBS:
            if card in hand:
                next_turn_val += -1 * hand_sum * CARD_PROBS[card]
                next_turn_bust_prob += CARD_PROBS[card]
            else:
                next_turn_val += card * CARD_PROBS[card]

        return {
            'e_score': hand_stats.e_score / (hand_prob),
            'bust_prob': hand_stats.bust_prob / (hand_prob),
            'next_turn_val': next_turn_val,
            'next_turn_bust_prob': next_turn_bust_prob,
        }


    def compute_stats(
        self,
        limit: int,
        cards: list[int] | None = None,
        cards_set: set[int] | None = None,
        prob: float = 1.0,
        tqdm_fn = lambda x: x,
    ):

        if cards is None:
            cards = []
        if cards_set is None:
            cards_set = set()

        assert len(cards) == len(cards_set)

        if len(cards) == limit:
            score = sum(cards) + FLIP_BONUS
            self.add_hand(cards, score, False, prob)
            return

        for card in tqdm_fn(CARD_PROBS):
            if card in cards_set:
                self.add_hand(cards, 0.0, True, prob * CARD_PROBS[card])
                continue
            cards.append(card)
            cards_set.add(card)
            self.compute_stats(limit, cards, cards_set, prob * CARD_PROBS[card])
            cards_set.remove(card)
            cards.pop()


try:
    with open('flip_seven_stats.pkl','rb') as f:
        stats_lookup = pickle.load(f)
except FileNotFoundError:
    stats_lookup = StatsLookup()
    stats_lookup.compute_stats(LIMIT, tqdm_fn = tqdm)
    with open('flip_seven_stats.pkl','wb') as f:
        pickle.dump(stats_lookup, f)

breakpoint()