import os
import json
import numpy as np
import matplotlib.pyplot as plt

from ttest import winner

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

def draw_heatmap(data_imported, type):
    # 축구장 크기 (m)
    field_x = 120  # 가로
    field_y = 80  # 세로

    # 구간 크기 (가로 24개, 세로 16개)
    num_bins_x = 24
    num_bins_y = 16
    bin_x = field_x / num_bins_x
    bin_y = field_y / num_bins_y

    # 예시 패스 데이터 (x, y 좌표)
    location_data = data_imported

    # 히트맵을 위한 2D 배열 (패스 개수를 카운트)
    heatmap = np.zeros((num_bins_y, num_bins_x))

    # 패스를 각 구간에 분류하고 개수 카운트
    for x, y in location_data:
        # 가로 (x) 위치
        bin_x_index = min(int(x // bin_x), num_bins_x - 1)
        
        # 세로 (y) 위치
        bin_y_index = min(int(y // bin_y), num_bins_y - 1)
        
        # 해당 구간의 패스 개수 증가
        heatmap[bin_y_index, bin_x_index] += 1

    # 축구장 그림 그리기
    fig, ax = plt.subplots(figsize=(12, 8))

    # 축구장 외곽선
    ax.plot([0, 0, field_x, field_x, 0], [0, field_y, field_y, 0, 0], color="black")

    # 센터 라인
    ax.plot([field_x / 2, field_x / 2], [0, field_y], color="black")

    # 센터 서클
    center_circle = plt.Circle((field_x / 2, field_y / 2), 9.15, color="black", fill=False)
    ax.add_patch(center_circle)
    ax.scatter(field_x / 2, field_y / 2, color="black", s=20)  # 센터 스팟

    # 페널티 구역
    ax.plot([0, 16.5, 16.5, 0], [(field_y - 40.3) / 2, (field_y - 40.3) / 2,
                                (field_y + 40.3) / 2, (field_y + 40.3) / 2], color="black")
    ax.plot([field_x, field_x - 16.5, field_x - 16.5, field_x],
            [(field_y - 40.3) / 2, (field_y - 40.3) / 2,
            (field_y + 40.3) / 2, (field_y + 40.3) / 2], color="black")

    # 골키퍼 구역
    ax.plot([0, 5.5, 5.5, 0], [(field_y - 18.32) / 2, (field_y - 18.32) / 2,
                                (field_y + 18.32) / 2, (field_y + 18.32) / 2], color="black")
    ax.plot([field_x, field_x - 5.5, field_x - 5.5, field_x],
            [(field_y - 18.32) / 2, (field_y - 18.32) / 2,
            (field_y + 18.32) / 2, (field_y + 18.32) / 2], color="black")

    # 골대
    ax.plot([0, -2], [(field_y - 7.32) / 2, (field_y - 7.32) / 2], color="black")
    ax.plot([0, -2], [(field_y + 7.32) / 2, (field_y + 7.32) / 2], color="black")
    ax.plot([field_x, field_x + 2], [(field_y - 7.32) / 2, (field_y - 7.32) / 2], color="black")
    ax.plot([field_x, field_x + 2], [(field_y + 7.32) / 2, (field_y + 7.32) / 2], color="black")

    ax.set_xlim(-5, field_x + 5)
    ax.set_ylim(-5, field_y + 5)
    ax.set_aspect("equal", adjustable="box")

    # 히트맵 시각화
    # 히트맵을 축구장 위에 투명하게 덧붙이기
    heatmap_img = ax.imshow(heatmap, cmap='YlGnBu', interpolation='nearest', alpha=0.6, extent=[0, field_x, 0, field_y])

    # 축구장의 크기와 구간을 시각적으로 표시
    ax.set_title(f"{team_name} {type} Heatmap", fontsize=30,fontweight='bold')
    ax.set_xlabel("Width (m)")
    ax.set_ylabel("Height (m)")

    # 범례 추가 (Colorbar)
    cbar = plt.colorbar(heatmap_img, ax=ax)
    cbar.set_label(type, rotation=270, labelpad=20, fontsize=15)

    # 범례 구간 구분 (색상에 대한 설명)
    ticks = list(range(1, int(np.max(heatmap)), int(int(np.max(heatmap))/4)))  
    cbar.set_ticks(ticks)


    cbar.set_ticklabels([f'{i}' for i in ticks])

    plt.axis('off')


# 한 match 데이터 추출
folder_path_laliga = 'C:\CODING\python\Infophy_TeamProject\Laliga_10_21'
json_files_laliga = [f for f in os.listdir(folder_path_laliga) if f.endswith('.json')]

match_data_list = []

for filename in json_files_laliga:
    file_path = os.path.join(folder_path_laliga,filename)

    with open(file_path,'r', encoding='utf-8') as f:
        data = json.load(f)

    # 경기 결과 분석
    for match in data:
        home_team = match['home_team']
        away_team = match['away_team']
        home_score = match['home_score']
        away_score = match['away_score']

        if home_score > away_score:
            winner = 'Home'
            loser = 'Away'
        elif away_score > home_score:
            winner = 'Away'
            loser = 'Home'
        else:
            continue  # 비긴 경기는 제외

        # 매치 ID, 승리팀/패배팀(홈/어웨이)을 딕셔너리 형태로 저장
        match_result = {
            'match_id': match['match_id'],
            'winner': winner,
            'loser': loser
        }

        # match_results 리스트에 추가
        match_results.append(match_result)

# pass location 데이터 추출
folder_path_events = 'C:/Users/user/local/GitHub/open-data/data/events'
folder_path_lineups = 'C:/Users/user/local/GitHub/open-data/data/lineups'

# 데이터 초기화
winner_pass_location = []
winner_failed_passes_location = []
winner_lost_duels_location = []
winner_dribble_losts_location = []
winner_shot_locations = []

loser_pass_location = []
loser_failed_passes_location = []
loser_lost_duels_location = []
loser_dribble_losts_location = []
loser_shot_locations = []

# 데이터 추출
k = 0
for match_id, match_result{winner} in (match_data_list):
    file_path_event = os.path.join(folder_path_events, match_id)
    file_path_lineup = os.path.join(folder_path_lineups, match_id)


    with open(file_path_event, 'r', encoding= 'utf-8') as f:
        events = json.load(f)
    with open(file_path_lineup, 'r', encoding= 'utf-8') as f:
        lineup = json.load(f)
        
    if match_result{winner} == 'home':
        lineup_info = lineup[0]
    else:
        match_result{winner} == 'away'
        lineup_info = lineup[1]

    # 선발 선수의 데이터만 사용
    starting_players = []
    for player in lineup_info['lineup']:
        if any(position["start_reason"] == "Starting XI" for position in player.get("positions", [])):
            starting_players.append(player['player_name'])
    

    # 선택된 팀과 선수의 패스 필터링
    team_passes = []
    team_shots =[]

    # 전체 event id 추출 -> 드리블 실패 데이터 추출에서 사용
    event_id = [event['id'] for event in events if event.get('team',{}).get('name') != team_name]

    for event in events:
        
        related_event_list = event.get('related_events',[])

        if event["type"]["name"] == "Pass" and event["team"]["name"] == team_name:
            team_passes.append(event)
        elif event["type"]["name"] == "Shot":
            team_shots.append(event)
        
        

        # 실패한 패스 필터링
        if event["type"]["name"] == "Pass" and "outcome" in event.get("pass", {}) and\
        event["pass"]["outcome"]["name"] == "Incomplete" and event["team"]["name"] == team_name:
        
            failed_passes_location.append(event['location']) 
        

        # 패배한 듀얼 필터링
        elif event["type"]["name"] == "Duel" and "outcome" in event.get("duel", {}) and\
            event["duel"]["outcome"]["name"] in {"Lost In Play", "Lost Out"} and event["team"]["name"] == team_name:
            
            lost_duels_location.append(event['location'])
        
        # 드리블 실패 필터링
        elif event["type"]["name"] == "Carry" and event["team"]["name"] == team_name and\
                any(related_event in event_id for related_event in related_event_list):
            
            dribble_losts_location.append(event['location'])

    # 패스 위치 수집
    for passes in team_passes:
        passer = passes["player"]["name"]
        recipient = passes["pass"].get("recipient", {}).get("name")
        if passer in starting_players:
            pass_location.append(passes["location"])

        if recipient in starting_players:
            pass_location.append(passes["pass"]["end_location"])

    
        
        

        
    # 슛 위치, 결과, 카테고리 추출
    for shot in team_shots:
        if shot['shot']['outcome']['name'] in ['Goal',"Saved", "Post",'Saved Off Target', 'Saved to Post','Blocked']:
            shot_locations.append(shot['location'])

    
    print(f'{k+1} in {len(match_data_list)}')  
    k += 1      

turnover_location = failed_passes_location + lost_duels_location + dribble_losts_location



if __name__ == '__main__':
    # pass heatmap
    draw_heatmap(pass_location, team_name, 'Pass')

    # shot heatmap
    draw_heatmap(shot_locations, team_name, 'Shot')

    # turnover heatmap
    draw_heatmap(turnover_location, team_name,'Turnover')

    plt.show()