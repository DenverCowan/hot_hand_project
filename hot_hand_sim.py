'''
@Author: Denver Cowan, Duke University. 2024
'''
import random
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp



def single_shot(shooting_average: float) -> int:
    '''Takes in a players shooting average and compares it to a randomly generated value between 0 and 1 for the sake of simulating a shot. 
    1 = hit
    0 = miss
    '''
    random_value = random.random()
    if random_value <= shooting_average:
        return 1
    else:
        return 0

def multiple_shots(shooting_average: float, number_of_shots: int) -> list:
    '''
    this function simulates multiple shots taken in sequence by a player with a given shooting average.
    output: list of hits and misses 
    1 = hit
    0 = miss
    '''
    result = []
    for i in range(0, number_of_shots):
        shot = single_shot(shooting_average)
        result.append(shot)
    return result

def hit_streak_lengths(shot_sequence: list) -> list:
    '''
    This function determines the number of and length of made basket, or "hit" streaks in a sequence of shots
    output: a list where each entry is a length of a hit streak. 
    '''
    result = []
    streaking = False
    count = len(shot_sequence)
    current_hit_streak = 0

    for shot in shot_sequence:
        if shot == 1: # shot is a hit
            if streaking == False:
                streaking = True
                current_hit_streak = 1
            else:
                current_hit_streak += 1
        else: # shot is a miss
            if streaking == True:
                streaking = False
                result.append(current_hit_streak)
                current_hit_streak = 0
    
    # the code below is to handle the case where the player was still in a 
    # streak at the end of the loop. for example: [0,1,1,1]
    if streaking == True:
        result.append(current_hit_streak)

    return result

def hit_streak_frequencies(hit_streak_lengths: list) -> list:
    '''
    This function takes in a list of hit streak lengths, I.E. how many shots a player made in a row at different points in a season and outputs the frequency of hit streaks of that lenght
    '''
    result = defaultdict(int)

    for hits_in_a_row in hit_streak_lengths:
        result[hits_in_a_row] += 1

    return result.values()

def simulate_season(shooting_average: float, shots_taken: int) -> list:
    '''
    This function will generate a shot sequence for a given player with a
    specified shooting average and number of shots taken, determine hit streaks they got in that sequence, and then normalize those frequencies the normalized frequencies of those streaks is the return value.
    '''
    shot_sequence = multiple_shots(shooting_average, shots_taken)
    streak_lengths = hit_streak_lengths(shot_sequence)
    number_of_streaks = len(streak_lengths)
    frequency_of_streaks = hit_streak_frequencies(streak_lengths)
    
    normalized_frequencies = [freq / number_of_streaks for freq in frequency_of_streaks]

    return normalized_frequencies

def visualize_streaks(streak: list) -> None:
    '''
    This function takes in the results of a simulated season and visualizes them on a bar chart.
    '''
    plt.bar(range(1, len(streak)+1),streak)
    plt.xlabel("Streak length")
    plt.ylabel('frequency')
    plt.title('Frequency of hit streaks in a season')
    plt.show()

def compare_two_players(p1_avg: float, p1_num_shots: int, p2_avg: float, p2_num_shots) -> None:
    '''
    This function takes in two players shooting averages and number of shots taken respectively
    then generates the results of their seasons and visulizes them for comparison.
    '''
    p1_shots = simulate_season(p1_avg, p1_num_shots)
    p2_shots = simulate_season(p2_avg, p2_num_shots)

    streak_lengths = np.arange(len(p1_shots))
    bar_width = 0.35

    plt.bar(streak_lengths - bar_width/2, p1_shots, bar_width, label='Player 1')
    plt.bar(streak_lengths + bar_width/2, p2_shots, bar_width, label='Player 2')

    plt.xlabel('Streak Length')
    plt.ylabel('Frequency')
    plt.title("Comparison of Streak Lengths")
    plt.xticks(streak_lengths, [f"Streak {i+1}" for i in range(len(streak_lengths))])
    plt.legend()
    plt.tight_layout()
    plt.show()

def average_several_seasons(shooting_avg: float, shots_taken: int, trials: int):
    '''
    This function runs through several simulated seasons and adds up the normalized streak length frequencies from each season for that player and then returns the average.
    The purpose of this method is to allow us to get a better estimation of the expected value that a players streak length frequency will converge to as opposed to only running one simulation.
    '''
    all_lists = []

    for i in range(trials):
        sim = simulate_season(shooting_avg, shots_taken)
        all_lists.append(sim)

    summed_values = [sum(values) for values in zip(*all_lists)]
    return summed_values


# simulating normally distributed shooting streaks for each player with the exact same shooting averages, and shots attempted as they had in their real season.

deandre_jordan_simulated = average_several_seasons(0.71, 100000, 100) # id = 201599 
# visualize_streaks(deandre_jordan)

al_horford_simulated = average_several_seasons(0.54, 965, 100) # id = 2199
#visualize_streaks(al_horford)

brandan_wright_simulated = average_several_seasons(0.64, 726, 100) # id = 201148
#visualize_streaks(brandan_wright)

rudy_gobert_simulated = average_several_seasons(0.60, 427, 100) # id = 203497
#visualize_streaks(rudy_gobert)

andrea_bargnani_simulated = average_several_seasons(0.45, 361, 100) # id = 2730
# print(andrea_bargnani)
#visualize_streaks(andrea_bargnani)

# reading in real player data
csv_file_path = '/Users/denvercowan/player_streak_data.csv'
actual_streak_data = pd.read_csv(csv_file_path)
#print(actual_streak_data.head())

# Initialize a dictionary to hold the data
player_streak_frequencies = defaultdict(lambda: defaultdict(int))

# Fill the dictionary with frequencies
for _, row in actual_streak_data.iterrows():
    player_id = row['player_id']
    streak_length = int(row['streak_length'])
    frequency = int(row['frequency'])
    player_streak_frequencies[player_id][streak_length] = frequency

# Now convert the nested defaultdict to a list format for each player
player_streak_lists = {}
for player_id, streaks in player_streak_frequencies.items():
    max_streak_length = max(streaks.keys())
    frequency_list = [0] * (max_streak_length + 1)  # Initialize the list with zeros
    for length, freq in streaks.items():
        frequency_list[length] = freq
    player_streak_lists[player_id] = frequency_list

deandre_jordan_actual = player_streak_lists[201599]
al_horford_actual = player_streak_lists[2199]
brandan_wright_actual = player_streak_lists[201148]
rudy_gobert_actual = player_streak_lists[203497]
andrea_bargnani_actual = player_streak_lists[2730]

# Perform the Kolmogorov-Smirnov test for each player:
# ks_stat_dj, p_value_dj = ks_2samp(deandre_jordan_actual, deandre_jordan_simulated)
# print(f"K-S statistic dj: {ks_stat_dj}")
# print(f"P-value dj: {p_value_dj}")

# ks_stat_ah, p_value_ah = ks_2samp(al_horford_actual, al_horford_simulated)
# print(f"K-S statistic AH: {ks_stat_ah}")
# print(f"P-value AH: {p_value_ah}")

# ks_stat_bw, p_value_bw = ks_2samp(brandan_wright_actual, brandan_wright_simulated)
# print(f"K-S statistic BW: {ks_stat_bw}")
# print(f"P-value BW: {p_value_bw}")

# ks_stat_rg, p_value_rg = ks_2samp(rudy_gobert_actual, rudy_gobert_simulated)
# print(f"K-S statistic RG: {ks_stat_rg}")
# print(f"P-value RG: {p_value_rg}")

# ks_stat_bargnani, p_value_bargnani = ks_2samp(andrea_bargnani_actual, andrea_bargnani_simulated)
# print(f"K-S statistic AB: {ks_stat_bargnani}")
# print(f"P-value AB: {p_value_bargnani}")

def ecdf(data):
    """Compute ECDF for a one-dimensional array of measurements."""
    # Number of data points: n
    n = len(data)

    # x-data for the ECDF: x
    x = np.sort(data)

    # y-data for the ECDF: y
    y = np.arange(1, n+1) / n

    return x, y

# Generate ECDFs
x_actual, y_actual = ecdf(andrea_bargnani_actual)
x_sim, y_sim = ecdf(andrea_bargnani_simulated)

# Plot the ECDFs
plt.figure(figsize=(8, 5))
plt.plot(x_actual, y_actual, marker='.', linestyle='none', label='Actual Data')
plt.plot(x_sim, y_sim, marker='.', linestyle='none', color='red', label='Simulated Data')
plt.xlabel('Streak Length')
plt.ylabel('ECDF')
plt.title('ECDF Comparison: Actual vs. Simulated Data')
plt.legend()
plt.grid(True)
plt.show()