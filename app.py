import streamlit as st
import requests
import json
import pandas as pd
import time

st.title('⚽️ Bundesliga Probability App')


# Get user input
team_list = ['FC Bayern München', 'Borussia Dortmund', 'FC Schalke 04', 'VfL Wolfsburg', 'Eintracht Frankfurt', 'Hertha BSC Berlin',
                                                          'SC Freiburg', '1. FSV Mainz 05', '1. FC Köln', '1. FC Union Berlin',
                                                          'Bayer 04 Leverkusen', 'Arminia Bielefeld', 'Werder Bremen',
                                                          'Borussia Mönchengladbach', 'TSG 1899 Hoffenheim', 'VfB Stuttgart',
                                                          'RB Leipzig', 'VfL Bochum', 'FC Augsburg', 'SpVgg Greuther Fürth',
                                                          'SC Paderborn 07', '1. FC Nürnberg', 'Fortuna Düsseldorf', 'Hannover 96',
                                                          'Hamburger SV', 'FC Ingolstadt 04', 'SV Darmstadt 98', '']
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
team_dict = {'FC Bayern München': 40,
             'Borussia Dortmund': 7,
             'FC Schalke 04': 9,
             'VfL Wolfsburg': 131,
             'Eintracht Frankfurt': 91,
             'Hertha BSC Berlin': 54,
             'SC Freiburg': 112,
             '1. FSV Mainz 05': 81,
             '1. FC Köln': 65,
             '1. FC Union Berlin': 80,
             'Bayer 04 Leverkusen': 6,
             'Arminia Bielefeld': 83,
             'Werder Bremen': 134,
             'Borussia Mönchengladbach': 87,
             'TSG 1899 Hoffenheim': 175,
             'VfB Stuttgart': 16,
             'RB Leipzig': 1635,
             'VfL Bochum': 129,
             'FC Augsburg': 95,
             'SpVgg Greuther Fürth': 115,
             'SC Paderborn 07': 31,
             '1. FC Nürnberg': 79,
             'Fortuna Düsseldorf': 185,
             'Hannover 96': 55,
             'Hamburger SV': 100,
             'FC Ingolstadt 04': 171,
             'SV Darmstadt 98': 118
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

st.write(f'The probabilities are computed based on {number_of_matches} matches!')

col1, col2, col3 = st.columns([5, 3, 3])

with st.container():
    col1, col2, col3 = st.columns([5, 3, 3])
    with col2:
        st.image(f'logos/{home_team.lower()}.png', width=128)

    with col3:
        st.image(f'logos/{away_team.lower()}.png', width=128)


with st.container():
    new_title = '<p style="font-family:sans-serif; color:Black; font-size: 18px;"><b>Probabilities:</b> </p>'
    st.markdown(new_title, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([7, 4, 3])
    with col1:
        st.write(f'🏆 Won')
        st.write(f"🤝 Draw")
        st.write(f'😢 Lost')


    with col2:
        st.write(f'{home_win_prob}%')
        st.write(f'{draw_prob}%')
        st.write(f'{away_win_prob}%')


    with col3:
        st.write(f'{away_win_prob}%')
        st.write(f'{draw_prob}%')
        st.write(f'{home_win_prob}%')
