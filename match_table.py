import json
import matplotlib.pyplot as plt
import pandas as pd

def extract_match_data(events_file_path):
    """
    JSON 데이터를 기반으로 경기 통계를 추출하는 함수

    매개변수:
    - events_file_path (str): JSON 파일 경로

    반환값:
    - dict: 팀별 경기 통계
    - list: 추출된 팀 이름 리스트
    - dict: 팀별 볼 점유율
    """
    with open(events_file_path, 'r', encoding='utf-8') as f:
        events_data = json.load(f)

    teams = {}
    team_names = set()
    team_possession = {}
    total_duration = 0

    for event in events_data:
        team_name = event["team"]["name"]
        team_names.add(team_name)
        
        # 팀별 초기화
        if team_name not in teams:
            teams[team_name] = {
                "shots": 0,
                "on_target": 0,
                "fouls": 0,
                "yellow_cards": 0,
                "red_cards": 0,
                "offsides": 0,
                "corners": 0,
                "passes": 0,
                "pass_success": 0,
                "pass_success_rate": 0,
                "possession_rate": 0
            }

        event_type = event["type"]["name"]
        
        # 경기 통계 계산
        if event_type == "Shot":
            teams[team_name]["shots"] += 1
            outcome = event.get("shot", {}).get("outcome", {}).get("name", "")
            if outcome in ["Goal", "Saved", "Post"]:
                teams[team_name]["on_target"] += 1

        if event_type == "Pass":
            teams[team_name]["passes"] += 1
            if "outcome" not in event.get("pass", {}):
                teams[team_name]["pass_success"] += 1
            if 'outcome' in event['pass'] and event['pass']['outcome']['name'] == 'Pass Offside':
                teams[team_name]["offsides"] += 1
            if 'type' in event["pass"] and event["pass"]["type"]["name"] == 'Corner':
                teams[team_name]["corners"] += 1
                
        if event_type in ["Foul Committed", "Bad Behaviour"]:
            teams[team_name]["fouls"] += 1
            card_type1 = event.get("foul_committed", {}).get("card", {}).get("name", "")
            card_type2 = event.get("bad_behaviour", {}).get("card", {}).get("name", "")
            if card_type1 == "Yellow Card" or card_type2 == "Yellow Card":
                teams[team_name]["yellow_cards"] += 1
            elif card_type1 in ["Red Card", "Second Yellow"] or card_type2 in ["Red Card", "Second Yellow"]:
                teams[team_name]["red_cards"] += 1   

        # 볼 점유 시간 계산
        possession_team = event.get("possession_team", {}).get("name", None)
        duration = event.get("duration", 0)
        total_duration += duration
        team_possession[possession_team] = team_possession.get(possession_team,0) + duration

        
    # 볼 점유율 계산
    for team in team_possession: 
        teams[team]["possession_rate"] = (team_possession[team]/total_duration) * 100

    # 패스 성공률 계산
    for team in teams:
        teams[team]["pass_success_rate"] = round((teams[team]["pass_success"] / teams[team]["passes"]) * 100, 2)

    return teams, list(team_names)

def create_match_table(teams, team_names):
    """
    주어진 경기 데이터를 표로 출력하는 함수
    """
    columns = ["Category", team_names[0], team_names[1]]
    rows = [
        ["Shots", teams[team_names[0]]["shots"], teams[team_names[1]]["shots"]],
        ["On Target", teams[team_names[0]]["on_target"], teams[team_names[1]]["on_target"]],
        ["Possession", f"{teams[team_names[0]]["possession_rate"]:.2f}%", f"{teams[team_names[1]]["possession_rate"]:.2f}%"],
        ["Passes", teams[team_names[0]]["passes"], teams[team_names[1]]["passes"]],
        ["Pass Accuracy", f"{teams[team_names[0]]['pass_success_rate']}%", f"{teams[team_names[1]]['pass_success_rate']}%"],
        ["Foul", teams[team_names[0]]["fouls"], teams[team_names[1]]["fouls"]],
        ["Yellow Card", teams[team_names[0]]["yellow_cards"], teams[team_names[1]]["yellow_cards"]],
        ["Red Card", teams[team_names[0]]["red_cards"], teams[team_names[1]]["red_cards"]],
        ["Offside", teams[team_names[0]]["offsides"], teams[team_names[1]]["offsides"]],
        ["Corners", teams[team_names[0]]["corners"], teams[team_names[1]]["corners"]],
    ]

    df = pd.DataFrame(rows, columns=columns)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis("tight")
    ax.axis("off")
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.auto_set_column_width(col=list(range(len(df.columns))))
    table.scale(1, 1.5)
    plt.title("Match Statistics", fontsize=16, fontweight="bold")
    plt.show()

# 파일 경로
events_file_path = "C:/Users/user/local/GitHub/open-data/data/events/3773457.json"

# 데이터 추출
teams, team_names = extract_match_data(events_file_path)

# 표 생성 및 출력
create_match_table(teams, team_names)
