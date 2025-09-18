import os
import json
from heatmap import draw_heatmap

type = 'pass'

# find all of the team names
"""
for filename in os.listdir(folder_path_laliga):
        if filename.endswith('.json'):  # JSON 파일만 처리
            file_path = os.path.join(folder_path_laliga, filename)
            
            # JSON 파일 로드
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for i in data:
                    team_name_away = i['away_team']['away_team_name']
                    team_name_home = i['home_team']['home_team_name']
                    team_names.add(team_name_away)
                    team_names.add(team_name_home)
"""


# 팀 이름
team_name_id = int(input("""what team's pass heatmap do you want to see?
['0':'Barcelona', '1':'RC Deportivo La Coruña', '2':'Racing Santander', '3': 'CD Numancia de Soria']
enter any number : """))

team_name_list = ['Barcelona', 'RC Deportivo La Coruña', 'Racing Santander', 'CD Numancia de Soria']
team_name = team_name_list[team_name_id]

# 선택한 팀이 한 match 데이터 추출
folder_path_laliga = 'C:/CODING/python/Infophy_TeamProject/Laliga_10_21'

json_files_laliga = [f for f in os.listdir(folder_path_laliga) if f.endswith('.json')]

match_data_list = []
k = 0
for filename in json_files_laliga:
    file_path = os.path.join(folder_path_laliga,filename)

    with open(file_path,'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in data:
            if i['home_team']['home_team_name'] == team_name:
                match_id = str(i['match_id']) + '.json'
                side = 'home'
                match_data_list.append((match_id, side))
            elif i['away_team']['away_team_name'] == team_name:
                match_id = str(i['match_id']) + '.json'
                side = 'away'
                match_data_list.append((match_id, side))


# pass location 데이터 추출
folder_path_events = 'C:/Users/user/local/GitHub/open-data/data/events'
folder_path_lineups = 'C:/Users/user/local/GitHub/open-data/data/lineups'

pass_location = []
for match_id, side in (match_data_list):
    file_path_event = os.path.join(folder_path_events, match_id)
    file_path_lineup = os.path.join(folder_path_lineups, match_id)
    

    with open(file_path_event, 'r', encoding= 'utf-8') as f:
        events = json.load(f)
    with open(file_path_lineup, 'r', encoding= 'utf-8') as f:
        lineup = json.load(f)
        
    if side == 'home':
        lineup_info = lineup[0]
    else:
        side == 'away'
        lineup_info = lineup[1]

    # 선발 선수의 데이터만 사용
    starting_players = []
    for player in lineup_info['lineup']:
        if any(position["start_reason"] == "Starting XI" for position in player.get("positions", [])):
            starting_players.append(player['player_name'])
    
   

    # 선택된 팀과 선수의 패스 필터링
    team_passes = []
    for event in events:
        if event["type"]["name"] == "Pass" and event["team"]["name"] == team_name:
            team_passes.append(event)
    
    # 패스 위치 수집
    for event in team_passes:
        passer = event["player"]["name"]
        recipient = event["pass"].get("recipient", {}).get("name")
        if passer in starting_players:
            pass_location.append(event["location"])

        if recipient in starting_players:
            pass_location.append(event["pass"]["end_location"])
    
    print(f'{k+1} in {len(match_data_list)}')  
    k += 1      

# heatmap으로 표현
draw_heatmap(pass_location, team_name, type)