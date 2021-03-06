import random
import torch
import torch.nn as nn
import lib

INPUT_SIZE = 32
HIDDEN_SIZE1 = 32
HIDDEN_SIZE2 = 32
OUTPUT_SIZE = 1
LAMBDA = 0.55
GAMMA = 0.35
ALPHA = 0.4
EPISODES = 10
SCORE_WEIGHT = 100
OUTPUT_PATH = "../Data/Neural Network/output.pt"


def roll(kept):
    result = [0, 0, 0, 0, 0]
    length = len(kept)
    for i in range(length):
        result[i] = kept[i]
    for i in range(5 - length):
        result[length + i] = random.randint(1, 6)
    result.sort(reverse=True)
    return result


def input_format(states1, up1, y_state1, score1, states2, up2, y_state2, score2):
    return torch.tensor(states1 + [up1, y_state1, score1] + states2 + [up2, y_state2, score2], dtype=torch.float32)


def state_evaluate(dice, cat, up, state, y_state, score1, state2, up2, y_state2, score2, model):
    # Initialization
    evals = [lib.yahtzee, lib.ones, lib.twos, lib.threes, lib.fours, lib.fives, lib.sixes, lib.three_of_a_kind,
             lib.four_of_a_kind, lib.fullhouse, lib.small_straight, lib.large_straight, lib.chance]

    # First evaluation
    score = evals[cat](dice, up)

    # Handle upper bonus counter
    if (cat < 7) and (cat > 0) and (up < 63):
        up = up + score
        if up > 63:
            up = 63

    # Joker rule and Yahtzee bonus
    if lib.yahtzee(dice, up) > 0:
        # In the case of Yahtzee is filled:
        if (y_state == 1) or (y_state == -1):
            # If Yahtzee is filled with 50, get a bonus of 100.
            if y_state == 1:
                score += 100

            # Check Joker.
            # If the corresponding upper section is filled, Joker is allowed.
            if state[dice[0]] == 1:
                # Check small straight, large straight, fullhouse.
                if cat == 9:
                    score += 25
                elif cat == 10:
                    score += 30
                elif cat == 11:
                    score += 40

    next_state = list(state)
    next_state[cat] = 1
    next_y_state = 0
    if y_state != 0:
        next_y_state = y_state
    else:
        if cat == 0:
            if score > 0:
                next_y_state = 1
            else:
                next_y_state = 0

    if model:
        return model(input_format(next_state, up, next_y_state, score1 + score, state2, up2, y_state2, score2)).item()
    else:
        return score


def main():
    # Setup Network
    m = nn.Sequential(nn.Linear(INPUT_SIZE, HIDDEN_SIZE1, True),
                      nn.Sigmoid(),
                      nn.Linear(HIDDEN_SIZE1, HIDDEN_SIZE2, True),
                      nn.Sigmoid(),
                      nn.Linear(HIDDEN_SIZE2, OUTPUT_SIZE, True),
                      nn.Sigmoid()
                      )

    cache = [[[]], lib.dicePatterns(1), lib.dicePatterns(2), lib.dicePatterns(3), lib.dicePatterns(4),
             lib.dicePatterns(5)]
    full = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    '''
    State encoding:
        13 values for 13 categories, filled = 1, unfilled = 0.
        1 value for upper section score.
        1 value for yahtzee status: unfilled = 0, obtained = 1, unobtained = -1.
        initial_state = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        Lowest possible score: 5
        Highest possible score: 1575
    '''

    # m.load_state_dict(torch.load("Data/two_player2.pt"))

    for p in m.parameters():
        # p.data = torch.zeros_like(p)
        p.grad = torch.zeros_like(p)

    print("training...")

    for episode in range(EPISODES):
        # Clear the trace
        for p in m.parameters():
            p.grad = torch.zeros_like(p)

        # Initial state
        state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        up = 0
        y_state = 0
        current_score = 0

        state2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        up2 = 0
        y_state2 = 0
        current_score2 = 0

        # Loop for each step of episode
        for round_id in range(13):
            # -----------------------------------------
            # The First player's part
            # Compute R3,K2,R2,K1
            empty = list(full)
            for i in range(13):
                if state[i] == 1:
                    empty.remove(i)

            R3 = {}
            for d in cache[5]:
                max_exp = 0
                for e in empty:
                    score = state_evaluate(d, e, up, state, y_state, current_score, state2, up2, y_state2,
                                           current_score2, m)
                    if score > max_exp:
                        max_exp = score
                R3[cache[5].index(d)] = max_exp

            K2 = {}
            for d in cache[5]:
                K2[cache[5].index(d) * 10 + 5] = R3[cache[5].index(d)]
            for k in range(4, -1, -1):
                for d in cache[k]:
                    exp = 0
                    for e in range(1, 7):
                        new_d = lib.extend(d, e)
                        exp += K2[cache[k + 1].index(new_d) * 10 + k + 1]
                    K2[cache[k].index(d) * 10 + k] = exp / 6

            R2 = {0: K2.get(0)}
            for k in range(1, 6):
                for d in cache[k]:
                    max_exp = K2.get(cache[k].index(d) * 10 + k)
                    for e in range(1, 7):
                        r = lib.remove(d, e)
                        if r or (r == []):
                            max_exp = max(max_exp, R2[cache[k - 1].index(r) * 10 + k - 1])
                    R2[cache[k].index(d) * 10 + k] = max_exp

            K1 = {}
            for d in cache[5]:
                K1[cache[5].index(d) * 10 + 5] = R2[cache[5].index(d) * 10 + 5]
            for k in range(4, -1, -1):
                for d in cache[k]:
                    exp = 0
                    for e in range(1, 7):
                        new_d = lib.extend(d, e)
                        exp += K1[cache[k + 1].index(new_d) * 10 + k + 1]
                    K1[cache[k].index(d) * 10 + k] = exp / 6

            # 1st Roll
            dice = roll([])
            max_keep = []
            max_exp = 0.0
            for key, val in K1.items():
                d = cache[key % 10][key // 10]

                if lib.subset(d, dice):
                    if val > max_exp:
                        max_exp = val
                        max_keep = d

            # 2nd Roll
            dice = roll(max_keep)
            max_keep = []
            max_exp = 0.0
            for key, val in K2.items():
                d = cache[key % 10][key // 10]

                if lib.subset(d, dice):
                    if val > max_exp:
                        max_exp = val
                        max_keep = d

            # 3rd Roll
            dice = roll(max_keep)
            max_cat = empty[0]
            max_exp = 0
            for e in empty:
                v = state_evaluate(dice, e, up, state, y_state, current_score, state2, up2, y_state2, current_score2, m)
                if v > max_exp:
                    max_exp = v
                    max_cat = e

            # Work out next state
            next_state = list(state)
            next_state[max_cat] = 1
            next_up = up
            next_ystate = y_state
            if (up < 63) and (max_cat >= 1) and (max_cat <= 6):
                for d in dice:
                    if d == max_cat:
                        next_up += max_cat
                if next_up > 63:
                    next_up = 63

            if max_cat == 0:
                if lib.yahtzee(dice, 0) > 0:
                    next_ystate = 1
                else:
                    next_ystate = -1

            next_score = current_score + state_evaluate(dice, max_cat, up, state, y_state, current_score,
                                                        state2, up2, y_state2, current_score2, None)

            '''
            # Do the TD-Lambda thing
            with torch.no_grad():
                for p in m.parameters():
                    p.grad *= l

            out = m(input_format(state, up, y_state, current_score,state2, up2, y_state2, current_score2))
            out.backward()
            with torch.no_grad():
                reward = (next_score - current_score2) / score_weight
                if current_score > current_score2:
                    reward = reward
                delta = reward + g * m(input_format(next_state, next_up, next_ystate, next_score, state2, up2, y_state2, current_score2)) - out

                for p in m.parameters():
                    p += a * delta * p.grad

            '''
            state = next_state
            up = next_up
            y_state = next_ystate
            current_score = next_score

            # -----------------------------------------
            # The Second player's part
            # Compute R3,K2,R2,K1
            empty = list(full)
            for i in range(13):
                if state2[i] == 1:
                    empty.remove(i)

            R3 = {}
            for d in cache[5]:
                max_exp = 0
                for e in empty:
                    score = state_evaluate(d, e, up2, state2, y_state2, current_score2, state, up, y_state,
                                           current_score, m)
                    if score > max_exp:
                        max_exp = score
                R3[cache[5].index(d)] = max_exp

            K2 = {}
            for d in cache[5]:
                K2[cache[5].index(d) * 10 + 5] = R3[cache[5].index(d)]
            for k in range(4, -1, -1):
                for d in cache[k]:
                    exp = 0
                    for e in range(1, 7):
                        new_d = lib.extend(d, e)
                        exp += K2[cache[k + 1].index(new_d) * 10 + k + 1]
                    K2[cache[k].index(d) * 10 + k] = exp / 6

            R2 = {0: K2.get(0)}
            for k in range(1, 6):
                for d in cache[k]:
                    max_exp = K2.get(cache[k].index(d) * 10 + k)
                    for e in range(1, 7):
                        r = lib.remove(d, e)
                        if r or (r == []):
                            max_exp = max(max_exp, R2[cache[k - 1].index(r) * 10 + k - 1])
                    R2[cache[k].index(d) * 10 + k] = max_exp

            K1 = {}
            for d in cache[5]:
                K1[cache[5].index(d) * 10 + 5] = R2[cache[5].index(d) * 10 + 5]
            for k in range(4, -1, -1):
                for d in cache[k]:
                    exp = 0
                    for e in range(1, 7):
                        new_d = lib.extend(d, e)
                        exp += K1[cache[k + 1].index(new_d) * 10 + k + 1]
                    K1[cache[k].index(d) * 10 + k] = exp / 6

            # 1st Roll
            dice = roll([])
            max_keep = []
            max_exp = 0.0
            for key, val in K1.items():
                d = cache[key % 10][key // 10]

                if lib.subset(d, dice):
                    if val > max_exp:
                        max_exp = val
                        max_keep = d

            # 2nd Roll
            dice = roll(max_keep)
            max_keep = []
            max_exp = 0.0
            for key, val in K2.items():
                d = cache[key % 10][key // 10]

                if lib.subset(d, dice):
                    if val > max_exp:
                        max_exp = val
                        max_keep = d

            # 3rd Roll
            dice = roll(max_keep)
            max_cat2 = empty[0]
            max_exp = 0
            for e in empty:
                v = state_evaluate(dice, e, up2, state2, y_state2, current_score2, state, up, y_state, current_score, m)
                if v > max_exp:
                    max_exp = v
                    max_cat2 = e

            # Work out next state
            next_state2 = list(state2)
            next_state2[max_cat2] = 1
            next_up2 = up2
            next_ystate2 = y_state2
            if (up2 < 63) and (max_cat2 >= 1) and (max_cat2 <= 6):
                for d in dice:
                    if d == max_cat2:
                        next_up2 += max_cat2
                if next_up2 > 63:
                    next_up2 = 63

            if max_cat2 == 0:
                if lib.yahtzee(dice, 0) > 0:
                    next_ystate2 = 1
                else:
                    next_ystate2 = -1

            next_score2 = current_score2 + state_evaluate(dice, max_cat2, up2, state2, y_state2, current_score2,
                                                          state, up, y_state, current_score, None)

            # Do the TD-Lambda thing
            with torch.no_grad():
                for p in m.parameters():
                    p.grad *= LAMBDA

            out = m(input_format(state2, up2, y_state2, current_score2, state, up, y_state, current_score))
            out.backward()
            with torch.no_grad():
                if (len(empty)) == 1:
                    if next_score2 > current_score:
                        delta = 1 - out
                    else:
                        delta = 0 - out
                else:
                    delta = GAMMA * m(input_format(next_state2, next_up2, next_ystate2, next_score2, state, up, y_state,
                                     current_score)) - out

                for p in m.parameters():
                    p += ALPHA * delta * p.grad

            state2 = next_state2
            up2 = next_up2
            y_state2 = next_ystate2
            current_score2 = next_score2

        print(episode, " / ", EPISODES)
        print(m(input_format([0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0], 0, 0, 67,
                             [0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0], 0, 0, 100)))
        print(m(input_format([0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0], 0, 0, 100,
                             [0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0], 0, 0, 67)))

    torch.save(m.state_dict(), OUTPUT_PATH)


main()
