import os
import json
from collections import defaultdict

# JSON 파일 경로
folder_path_laliga = 'C:/CODING/python/Infophy_TeamProject/Laliga_10_21'
json_files_lalaga = [f for f in os.listdir(folder_path_laliga) if f.endswith('.json')]

# 팀별 통계 초기화
team_stats = defaultdict(lambda: {'matches': 0, 'wins': 0})

# 폴더 내 모든 JSON 파일 처리
for filename in json_files_lalaga:
    file_path = os.path.join(folder_path_laliga, filename)
    
    # JSON 파일 로드
    with open(file_path, 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    # 데이터 처리
    for match in matches:
        home_team = match['home_team']['home_team_name']
        away_team = match['away_team']['away_team_name']
        home_score = match['home_score']
        away_score = match['away_score']

        # 경기 수 증가
        team_stats[home_team]['matches'] += 1
        team_stats[away_team]['matches'] += 1

        # 승리 수 증가
        if home_score > away_score:
            team_stats[home_team]['wins'] += 1
        elif away_score > home_score:
            team_stats[away_team]['wins'] += 1

# 결과 출력
for team, stats in team_stats.items():
    print(f"{team} 경기 수: {stats['matches']}, 승리 수: {stats['wins']}")