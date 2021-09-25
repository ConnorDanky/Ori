from datetime import datetime, timedelta
from pytz import timezone
import pytz
import requests
import json

def response (team = ""):

    string_return = ""
    #team all caps
    team = team.upper()

    #Time Stuff!
    now = datetime.now(tz=pytz.utc)
    #print(f"UTC TIME: {now}")
    now = now.astimezone(timezone('US/Pacific'))
    #print(f"PST TIME: {now}")

    #URL Time!
    baseball_url = "https://gd2.mlb.com/components/game/mlb/year_%d/month_%s/day_%s/master_scoreboard.json" \
        % (now.year, now.strftime("%m"), now.strftime("%d"))
    #print(f"URL: {baseball_url}")
    baseball_data = requests.get(baseball_url)

    #Building Data
    game_data = baseball_data.json()
    game_array = game_data['data']['games']['game']

    #print(game_array)

    #Game Logic
    for game in game_array:
        if (game['home_name_abbrev']) == team or (game['away_name_abbrev']) == team:
            output = team_score(game)
            if output:
                string_return = ""
                string_return += output 
                break
        else:
            output = game_info(game)
            if output:
                string_return += output

    print(string_return)
    return string_return

## PRE MADE BASEBALL FUNCTIONS (SEARCH)
def game_info(game):
    
    if game['status']['status'] == "In Progress":
        if game['status']['inning_state'] == "Bottom":
            topBottom = "B"
        if game['status']['inning_state'] == 'Top':
            topBottom = "T"
        if game['status']['inning_state'] == 'Middle':
            topBottom = "M"
        if game['status']['inning_state'] == 'End':
            topBottom = "E"

        return '%s (%s) vs %s (%s) [%s%s]\n' % (
                game['away_team_name'],
                game['linescore']['r']['away'],
                game['home_team_name'],
                game['linescore']['r']['home'],
                topBottom,
                game['status']['inning']
            )
    elif (game['status']['status'] == "Final" or game['status']['status'] == "Game Over" or game['status']['status'] == "Postponed"):
        return '%s (%s) vs %s (%s) [%s]\n' % (
                game['away_team_name'],
                game['linescore']['r']['away'],
                game['home_team_name'],
                game['linescore']['r']['home'],
                game['status']['status']
            )
    
    elif (game['status']['status'] == "Pre-Game" or game['status']['status'] == "Warmup"):
        return '%s vs %s @ %s %s%s %s\n' % (
                game['away_team_name'],
                game['home_team_name'],
                game['venue'],
                game['home_time'],
                game['hm_lg_ampm'],
                game['status']['status']
            )

    elif (game['status']['status'] == "Preview"):
        return '%s vs %s @ %s %s%s\n' % (
                game['away_team_name'],
                game['home_team_name'],
                game['venue'],
                game['home_time'],
                game['hm_lg_ampm']
            )
    
#function to determine the status of a game, if a team is selected
#based on the progress, different data is returned

def team_score(game):
    if game['status']['status'] == "In Progress":
        disp = box_score(game)
        return \
        '%s\n' \
        '-------------------------------\n' \
        '%s (%s) vs. %s (%s) @ %s\n' \
        '%s: %s of the %s\n' \
        'Pitching: %s || Batting: %s || S: %s B: %s O: %s\n' \
        '-------------------------------' % (
                disp,
                game['away_team_name'],
                game['linescore']['r']['away'],
                game['home_team_name'],
                game['linescore']['r']['home'],
                game['venue'],
                game['status']['status'],
                game['status']['inning_state'],
                game['status']['inning'],
                game['pitcher']['last'],
                game['batter']['last'],
                game['status']['s'],
                game['status']['b'],
                game['status']['o']
            )
    elif (game['status']['status'] == "Final" or game['status']['status'] == "Game Over"):
        disp = box_score(game)
        return \
        '%s\n-------------------------------\n' \
        '%s (%s) vs. %s (%s) @ %s\n' \
        'W: %s || L: %s || SV: %s\n' \
        '-------------------------------' % (
                disp,
                game['away_team_name'],
                game['linescore']['r']['away'],
                game['home_team_name'],
                game['linescore']['r']['home'],
                game['venue'],
                game['winning_pitcher']['name_display_roster'],
                game['losing_pitcher']['name_display_roster'],
                game['save_pitcher']['name_display_roster']
            )
    elif (game['status']['status'] == "Pre-Game" or game['status']['status'] == "Preview"):
        return \
        '-------------------------------\n' \
        '%s vs %s @ %s %s%s\n' \
        'P: %s || P: %s\n' \
        '-------------------------------' % (
                game['away_team_name'],
                game['home_team_name'],
                game['venue'],
                game['home_time'],
                game['hm_lg_ampm'],
                game['away_probable_pitcher']['name_display_roster'],
                game['home_probable_pitcher']['name_display_roster']
               )
                
def box_score(game):
    header = f"{'':>3}"
    home = f"{game['home_name_abbrev']}"
    away = f"{game['away_name_abbrev']}"

    game_number = 0
    for inning in game['linescore']['inning']:
        h_r = inning['home']
        a_r = inning['away']
        game_number += 1
        header += f"{game_number:>5}"
        home += f"{h_r:>5}"
        away += f"{a_r:>5}"

    r = game['linescore']['r']
    h = game['linescore']['h']
    e = game['linescore']['e']

    header += f"{'R':>3}{'H':>3}{'E':>3}"
    home += f"{r['home']:>3}{h['home']:>3}{e['home']:>3}"
    away += f"{r['away']:>3}{h['away']:>3}{e['away']:>3}"

    output = f"{header}\n{away}\n{home}"
    return output
