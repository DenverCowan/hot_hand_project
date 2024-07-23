'''
@Author: Denver Cowan, Duke University. 2024
'''
import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import os

def find_streakiness(shot_sequence: dict) -> dict:
    '''
    This function has multiple purposes:
    1. it finds and records every players shooting streaks and the length of it
    2. it finds each players average streakiness as calculated by: 
    sum(shooting_streaks) / length(shooting_streaks)
    3. it finds the overall average of all shooting streaks
    4. it finds the standard deviation of all shooting streaks
    5. it calculates the z-score of all shooters streakiness in relation to the overall avg and std
    output: a dict of the form {player_id: players z-score}
    '''
    streakiness = {}
    all_streaks = []

    for player, sequence in shot_sequence.items():
        result = []
        streaking = False
        current_hit_streak = 0
        for shot in sequence:
            if shot == 1: # shot is a hit
                if not streaking:
                    streaking = True
                    current_hit_streak = 1
                else:
                    current_hit_streak += 1
            else: # shot is a miss
                if streaking:
                    streaking = False
                    result.append(current_hit_streak)
                    current_hit_streak = 0
        # handles streak at end of loop for example: [0,1,1,1]
        if streaking == True:
            result.append(current_hit_streak)
        # keeps track of all shooting streaks    
        all_streaks.extend(result)
        # keeps track of each players average streakiness
        streakiness[player] = sum(result)/ len(result) if result else 0
    # find mean and standard deviation of all the streaks.
    overall_mean = np.mean(all_streaks)
    overall_std = np.std(all_streaks)
    # calculate z-score of each players streakiness
    for player in streakiness:
        streakiness[player] = (streakiness[player] - overall_mean) / overall_std if overall_std != 0 else 0

    return streakiness

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

def plot_hit_streak_histogram(player_data: dict) -> None:
    '''
    This function iterates over a dict of the form {player_id: (streak lengths, streak frequencies)}, creates, and displays a histogram for each player
    '''
    for player, data in player_data.items():
        lengths, _ = data

        # Compute frequencies using numpy.histogram
        freqs, bins = np.histogram(lengths, bins=np.arange(1, max(lengths) + 2))

        plt.bar(bins[:-1], freqs)
        plt.xlabel('Hit Streak Length')
        plt.ylabel('Frequency of Streak')
        plt.title(f'Hit Streak Histogram for Player {player}')
        plt.show()

# Read the CSV file into a DataFrame.
file_path = '/Users/denvercowan/DukeCourses/spring24/ma242/hot_hand_project/all_shots_2014.csv'
df = pd.read_csv(file_path, delimiter=',')

# make a date column in order to keep shots sequential
df['DATE'] = pd.to_datetime(df['MATCHUP'].str.split(' - ', expand=True)[0], format='%b %d, %Y')

# get all unique player id's in their own group, then sort by Date, and game
# clock to ensure shots are in order that they occurred. 
sorted_df = df.groupby('PLAYER_ID').apply(lambda x: x.sort_values(by=['DATE', 'GAME_CLOCK']))

# create a list of 0's and 1's to represent each players shooting streaks.
shooting_streaks_dict = {}
current_player_id = None
current_streak = []
total_attempts = {}

for _, row in sorted_df.iterrows():
    player_id = row['PLAYER_ID']

    if player_id != current_player_id:
        current_player_id = player_id
        current_streak = []

    if row['SHOT_RESULT'] == 'made':
        current_streak.append(1)
    else:
        current_streak.append(0)

    shooting_streaks_dict[player_id] = current_streak
    total_attempts[player_id] = total_attempts.get(player_id, 0) + 1

# filter out anyone with < 50 shooting streaks that season
min_streaks = 100

player_streak_counts = {player_id: len(streaks) for player_id, streaks in shooting_streaks_dict.items()}

filtered_players = {player_id: streaks for player_id, streaks in shooting_streaks_dict.items() if player_streak_counts.get(player_id, 0) >= min_streaks}

# find all players z-scores
player_z_scores = find_streakiness(filtered_players)

# find player shooting streak lengths
player_hit_streak_lengths = {}
for player, shots in filtered_players.items():
    streak_lengths = hit_streak_lengths(shots)
    player_hit_streak_lengths[player] = streak_lengths

# find streak length frequencies of players
player_hit_freqs = {}
for player_id, streaks in filtered_players.items():
    frequencies = hit_streak_frequencies(streaks)
    player_hit_freqs[player_id] = frequencies

# find frequencies of player hit streaks
player_hit_streak_frequencies = {}
for player, lengths in player_hit_streak_lengths.items():
    frequencies = hit_streak_frequencies(lengths)
    player_hit_streak_frequencies[player] = frequencies

# sort all players by z-score
sorted_players = sorted(player_z_scores.items(), key= lambda x: x[1], reverse=True)

# seperate most streaky players into a diff dict for visulization purposes
streakiest_shooters = dict(sorted_players[:5])
print(streakiest_shooters)

# now we want to visualize the player streak length, and frequencies on a histogram
player_data = {}
for player in streakiest_shooters:
    player_data[player] = (player_hit_streak_lengths[player], player_hit_streak_frequencies[player])

# Create a list of dictionaries, each representing data for one player
player_data_for_df = []
for player_id, (lengths, freqs) in player_data.items():
    # Assuming that the lengths and frequencies align, which they should
    for streak_length, frequency in zip(lengths, freqs):
        player_data_for_df.append({
            'player_id': player_id,
            'streak_length': streak_length,
            'frequency': frequency
        })

# Convert the list of dictionaries to a DataFrame
player_data_df = pd.DataFrame(player_data_for_df)

# Get the home directory path
home_dir = os.path.expanduser('~')

# Build the full file path
file_path = os.path.join(home_dir, 'player_streak_data.csv')
print(file_path)
# Save the CSV to the specified path
player_data_df.to_csv(file_path, index=False)

#plot_hit_streak_histogram(player_data)