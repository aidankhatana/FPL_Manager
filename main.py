
import requests
import json 
import pandas as pd
from datetime import datetime, timedelta

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)




def update_team(email = "aidankhatana@gmail.com", password = "Pa$5word" , id = "2793113"):  
    players_df, fixtures_df, gameweek=get_data()
    session = requests.session()
    data = {'login' : email, 'password' : password, 'app' : 'plfpl-web', 'redirect_uri' : 'https://fantasy.premierleague.com/'}
    login_url = "https://users.premierleague.com/accounts/login/"
    
    session.post(url=login_url, data=data)
    
    url = "https://fantasy.premierleague.com/api/my-team/" + str(id)
    team = session.get(url)
    team = json.loads(team.content)
    
    bank = team['transfers']['bank']
    
    players = [x['element'] for x in team['picks']]
    my_team = players_df.loc[players_df.id.isin(players)]
    potential_players = players_df.loc[~players_df.id.isin(players)]
    
def calc_out_weight(players):
    players['weight'] = 100
    players['weight']-= players['diff']/3
    players['weight']-= players['form'].astype("float")*10
    players['weight']+= (100 - players['chance_of_playing_this_round'].astype("float"))*0.2
    players.loc[players['element_type'] ==1, 'weight'] -=10
    players.loc[players['weight'] <0, 'weight'] =0
    return players.sample(1, weights=players.weight)
    
    
    
def get_data():

    
    players =  get('https://fantasy.premierleague.com/api/bootstrap-static/')
    players_df = pd.DataFrame(players['elements'])
    teams_df = pd.DataFrame(players['teams'])
    fixtures_df = pd.DataFrame(players['events'])
    today = datetime.now().timestamp()
    fixtures_df = fixtures_df.loc[fixtures_df.deadline_time_epoch>today]
    if check_update(fixtures_df) == False:
        print("Deadline Too Far Away")
        exit(0)
    gameweek =  fixtures_df.iloc[0].id
    players_df = players_df
    players_df.chance_of_playing_next_round = players_df.chance_of_playing_next_round.fillna(100.0)
    players_df.chance_of_playing_this_round = players_df.chance_of_playing_this_round.fillna(100.0)
    fixtures = get('https://fantasy.premierleague.com/api/fixtures/?event='+str(gameweek))
    fixtures_df = pd.DataFrame(fixtures)

    
    teams=dict(zip(teams_df.id, teams_df.name))
    players_df['team_name'] = players_df['team'].map(teams)
    fixtures_df['team_a_name'] = fixtures_df['team_a'].map(teams)
    fixtures_df['team_h_name'] = fixtures_df['team_h'].map(teams)

    home_strength=dict(zip(teams_df.id, teams_df.strength_overall_home))
    away_strength=dict(zip(teams_df.id, teams_df.strength_overall_away))

    fixtures_df['team_a_strength'] = fixtures_df['team_a'].map(away_strength)
    fixtures_df['team_h_strength'] = fixtures_df['team_h'].map(home_strength)
    
    fixtures_df=fixtures_df.drop(columns=['id'])
    a_players = pd.merge(players_df, fixtures_df, how="inner", left_on=["team"], right_on=["team_a"])
    h_players = pd.merge(players_df, fixtures_df, how="inner", left_on=["team"], right_on=["team_h"])

    a_players['diff'] = a_players['team_a_strength'] - a_players['team_h_strength']
    h_players['diff'] = h_players['team_h_strength'] - h_players['team_a_strength']

    players_df = a_players.append(h_players)
    return players_df, fixtures_df, gameweek
def get(url):
    response = requests.get(url)
    return json.loads(response.content)

def check_update(df):
    
    today = datetime.now()
    tomorrow=(today + timedelta(days=1)).timestamp()
    today = datetime.now().timestamp()
    df = df.loc[df.deadline_time_epoch>today]
    
    deadline = df.iloc[0].deadline_time_epoch
    if deadline<tomorrow:
        return True
    else:
        return False
      
def lambda_handler(event, context):
    email = "your_email"
    password = "your_password"
    user_id = "your_id"
    update_team(email, password,user_id)

update_team()
