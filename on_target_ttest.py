import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np

def extract_match_data(event_data):
    teams = {}
    team_names = set()
    team_possession = {}
    total_duration = 0

    for event in event_data:
        team_name = event["team"]["name"]
        team_names.add(team_name)
        
        if team_name not in teams:
            teams[team_name] = {
                "shots": 0,
                "on_target": 0,
                "passes": 0,
                "pass_success": 0,
                "pass_success_rate": 0
            }

        event_type = event["type"]["name"]
        possession_team = event.get("possession_team", {}).get("name", None)
        duration = event.get("duration", 0)
        total_duration += duration
        team_possession[possession_team] = team_possession.get(possession_team, 0) + duration

        if event_type == "Shot":
            teams[team_name]["shots"] += 1
            outcome = event.get("shot", {}).get("outcome", {}).get("name", "")
            if outcome in ["Goal", "Saved", "Post"]:
                teams[team_name]["on_target"] += 1
        elif event_type == "Pass":
            teams[team_name]["passes"] += 1
            if "outcome" not in event.get("pass", {}):
                teams[team_name]["pass_success"] += 1        

    possession_percentages = {
        team: (time / total_duration) * 100 for team, time in team_possession.items()
    }

    for team in teams:
        teams[team]["pass_success_rate"] = round(
            (teams[team]["pass_success"] / teams[team]["passes"]) * 100, 2)

    return teams, sorted(list(team_names)), possession_percentages

folder_path_laliga = 'C:/CODING/python/Infophy_TeamProject/Laliga_10_21'
json_files_laliga = [f for f in os.listdir(folder_path_laliga) if f.endswith('.json')]

match_results = []

for filename in os.listdir(folder_path_laliga):
    if filename.endswith('.json'):  
        file_path = os.path.join(folder_path_laliga, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

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
                continue
            
            match_result = {
                'match_id': match['match_id'],
                'winner': winner,
                'loser': loser
            }
            
            match_results.append(match_result)

folder_path_events = 'C:/Users/user/local/GitHub/open-data/data/events'

winning_shots = []
losing_shots = []

for match_result in match_results:
    match_id = match_result['match_id']
    winner_team = match_result['winner']
    loser_team = match_result['loser']

    event_file_path = os.path.join(folder_path_events, f'{match_id}.json')
    
    if os.path.exists(event_file_path):
        with open(event_file_path, 'r', encoding='utf-8') as f:
            event_data = (json.load(f))       
    else:
        print(f"Warning: {match_id}에 대한 경기 파일이 존재하지 않습니다.")

    teams, team_names, possession_percentages = extract_match_data(event_data)

    if winner_team == 'Home':
        winner_team = team_names[0]
        loser_team = team_names[1]
    elif winner_team == 'Away':
        winner_team = team_names[1]
        loser_team = team_names[0]

    winning_shots.append(teams[winner_team]['on_target'])
    losing_shots.append(teams[loser_team]['on_target'])

winning_shots_average = sum(winning_shots)/len(winning_shots)
losing_shots_average = sum(losing_shots)/len(losing_shots)

df = pd.DataFrame({'Winning Team Shots': winning_shots, 'Losing Team Shots': losing_shots})

t_stat, p_value = stats.ttest_ind(winning_shots, losing_shots)
print(f"t-statistic: {t_stat}")
print(f"p-value: {p_value}")

if p_value < 0.05:
    print("유효슛과 경기 승패 간에 유의미한 차이가 존재합니다.")
else:
    print("유효슛과 경기 승패 간에 유의미한 차이가 존재하지 않습니다.")

# 정규분포를 위한 평균과 표준편차 계산
win_mean = np.mean(winning_shots)
win_std = np.std(winning_shots)
lose_mean = np.mean(losing_shots)
lose_std = np.std(losing_shots)



# 정규분포를 위한 x 값 생성
x_win = np.linspace(min(winning_shots), max(winning_shots), 100)
y_win = stats.norm.pdf(x_win, win_mean, win_std)

x_lose = np.linspace(min(losing_shots), max(losing_shots), 100)
y_lose = stats.norm.pdf(x_lose, lose_mean, lose_std)

# 그래프 생성
plt.figure(figsize=(10, 6))

# KDE (Kernel Density Estimation) 곡선: 데이터의 분포를 추정
# 주어진 데이터 포인트를 기반으로 연속적인 확률 밀도 함수
#  데이터의 분포를 부드럽고 연속적으로 시각화
sns.histplot(winning_shots, kde=True, color='blue', label='Winning Team Shots', stat='density', bins=15)
sns.histplot(losing_shots, kde=True, color='red', label='Losing Team Shots', stat='density', bins=15)

# 정규분포곡선
plt.plot(x_win, y_win, color='skyblue', linestyle='-', linewidth=2, label='Winning Team Normal Dist.')
plt.plot(x_lose, y_lose, color='pink', linestyle='-', linewidth=2, label='Losing Team Normal Dist.')
plt.title('Distribution of Shots: Winning vs Losing Teams (with Normal Distribution)')
plt.xlabel('Number of On Target Shots')
plt.ylabel('Density')
plt.legend()
plt.grid(True)
plt.show()