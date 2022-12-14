import streamlit as st
import requests
import json
import pandas as pd
import time

st.title('⚽️ Bundesliga Probability App')


# Get user input
team_list = ['Bayern', 'Dortmund', 'Schalke', 'Wolfsburg', 'Frankfurt', 'Hertha',
                                                          'Freiburg', 'Mainz', 'Köln', 'Union Berlin', 'Leverkusen', 'Bielefeld',
                                                          'Bremen', 'Gladbach', 'Hoffenheim', 'Stuttgart', 'Leipzig', 'Bochum',
                                                          'Augsburg']
team_list.sort()

home_team = st.sidebar.selectbox('Pick your HOME team:', team_list)

away_team = st.sidebar.selectbox('Pick your AWAY team:', team_list)

with st.spinner(text="Loading data..."):
    time.sleep(1)
    if home_team == away_team:
        st.error('Select 2 different teams!')
        st.stop()
    else:
        st.success('Loaded!')

# Create dict of available teams
team_dict = {'Bayern': 40,
             'Dortmund': 7,
             'Schalke': 9,
             'Wolfsburg': 131,
             'Frankfurt': 91,
             'Hertha': 54,
             'Freiburg': 112,
             'Mainz': 81,
             'Köln': 65,
             'Union Berlin': 80,
             'Leverkusen': 6,
             'Bielefeld': 83,
             'Bremen': 134,
             'Gladbach': 87,
             'Hoffenheim': 175,
             'Stuttgart': 16,
             'Leipzig': 1635,
             'Bochum': 129,
             'Augsburg': 95,
             }

# Check if team exists
def return_team_number(home_team, away_team, team_dict):
    home = team_dict[home_team]
    away = team_dict[away_team]

    return home, away

# Get team number
home, away = return_team_number(home_team, away_team, team_dict)

# API call: Get the match data for both teams: team1 is the HOME and team2 is the AWAY team
url = f'https://api.openligadb.de/getmatchdata/{home}/{away}'
response = requests.get(url)


# Return the end score for both home and away team
def team_func(team, response):
    # home team is Bayern
    # check if result at the end of the match
    endergebnis = 'Endergebnis'
    # count number of matches
    match = 0
    # store if win, draw, loss in dict
    match_history = {'match':[],
                 'outcome': [],
                 'goals_team_1': [],
                 'goals_team_2': []}
    # store match_history dict in list of dicts to later transform into df

    for x in range(0, len(response.json())):

        try:
            if response.json()[x]['team1']['teamId'] == team:
                if endergebnis in response.json()[x]['matchResults'][0].values():
                    goals_team1 = response.json()[x]['matchResults'][0]['pointsTeam1']
                    goals_team2 = response.json()[x]['matchResults'][0]['pointsTeam2']
                    if goals_team1 > goals_team2:
                        match_history['match'].append(x)
                        match_history['goals_team_1'].append(goals_team1)
                        match_history['goals_team_2'].append(goals_team2)
                        match += 1
                    elif goals_team1 < goals_team2:
                        match_history['match'].append(x)
                        match_history['goals_team_1'].append(goals_team1)
                        match_history['goals_team_2'].append(goals_team2)
                        match += 1
                    else:
                        match_history['match'].append(x)
                        match_history['goals_team_1'].append(goals_team1)
                        match_history['goals_team_2'].append(goals_team2)
                        match += 1
                else:
                    goals_team1 = response.json()[x]['matchResults'][1]['pointsTeam1']
                    goals_team2 = response.json()[x]['matchResults'][1]['pointsTeam2']
                    if goals_team1 > goals_team2:
                        match_history['match'].append(x)
                        match_history['goals_team_1'].append(goals_team1)
                        match_history['goals_team_2'].append(goals_team2)
                        match += 1
                    elif goals_team1 < goals_team2:
                        match_history['match'].append(x)
                        match_history['goals_team_1'].append(goals_team1)
                        match_history['goals_team_2'].append(goals_team2)
                        match += 1
                    else:
                        match_history['match'].append(x)
                        match_history['goals_team_1'].append(goals_team1)
                        match_history['goals_team_2'].append(goals_team2)
                        match += 1
        except IndexError:
            continue

    return match_history

# Home team
home_match_history = team_func(home, response)
home_match_df = pd.DataFrame(home_match_history.items())
home_df = home_match_df.set_index(0).T
home_df = home_df.explode(['match', 'goals_team_1', 'goals_team_2'])
home_df = home_df[['match', 'goals_team_1', 'goals_team_2']]
home_df = home_df.set_index('match').reset_index()
home_team = [team for team, number in team_dict.items() if number == home][0]
home_df = home_df.rename(columns={'goals_team_1': home_team, 'goals_team_2': away_team})

# Away team
away_match_history = team_func(away, response)
away_match_df = pd.DataFrame(away_match_history.items())
away_df = away_match_df.set_index(0).T
away_df = away_df.explode(['match', 'goals_team_1', 'goals_team_2'])
away_df = away_df[['match', 'goals_team_1', 'goals_team_2']]
away_df = away_df.set_index('match').reset_index()
away_df = away_df.rename(columns={'goals_team_1': away_team, 'goals_team_2': home_team})

# Combine both df
def calc_new_col(row):
    if row[0] > row[1]:
        val = 1
    elif row[0] < row[1]:
        val = 2
    else:
        val = 0

    return val

def create_complete_df(home_df, away_df):
    complete_df = pd.concat([home_df, away_df])
    complete_df = complete_df.sort_values(by='match').set_index('match').reset_index()
    complete_df = complete_df.iloc[:, 1:3].astype(int)

    complete_df['outcome'] = complete_df.apply(calc_new_col, axis=1)

    return complete_df

# This is the combined dataframe
complete_df = create_complete_df(home_df, away_df)

# Caclulate the win/draw/loss probabilities for the home team
def calculate_probability(complete_df):
    home_win_prob = float(round(complete_df[complete_df['outcome']==1]['outcome'].count()/complete_df.outcome.count()* 100, 2))
    away_win_prob = float(round(complete_df[complete_df['outcome']==2]['outcome'].count()/complete_df.outcome.count()* 100, 2))
    draw_prob = float(round(100 - home_win_prob - away_win_prob, 2))
    number_of_matches = complete_df['outcome'].count()

    return home_win_prob, away_win_prob, draw_prob, number_of_matches

# Call the function
home_win_prob, away_win_prob, draw_prob, number_of_matches = calculate_probability(complete_df)

# Create columns to show the results

st.write(f'🏆 The win probabilities are: for {home_team} is: {home_win_prob}%...')
st.write(f'🤝 The draw probability is: {home_team} is: {draw_prob}%...')
st.write(f'😢 The loss probabilities are: for {home_team} is: {away_win_prob}%, based on {number_of_matches} matches!')


c1, c2, c3 = st.columns(3)
c4, c5, c6 = st.columns(3) #just to highlight these are different cols

with st.container():
    c1.write('Probabilities')
    c2.image(f'logos/{home_team.lower()}.png', width=128)
    c3.image(f'logos/{away_team.lower()}.png', width=128)

with st.container():
    c4.write(f'🏆 Win')
    c5.write(f'{home_win_prob}%')
    c6.write(f'{100 - home_win_prob}%')

with st.container():
    c4.write(f"🤝 Draw")
    c5.write(f'{draw_prob}%')
    c6.write(f'{draw_prob}%')

with st.container():
    c4.write(f'😢 Loss')
    c5.write(f'{away_win_prob}%')
    c6.write(f'{100 - away_win_prob}%')





# Show team logo
