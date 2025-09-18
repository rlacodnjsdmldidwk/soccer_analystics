import json

def calculate_possession(events_file_path):
    """
    JSON 데이터를 기반으로 팀별 볼 점유율을 계산하는 함수

    매개변수:
    - file_path (str): JSON 파일 경로

    반환값:
    - dict: 팀별 볼 점유율
    - float: 총 경기 시간(분 단위)
    """
    # JSON 파일 로드
    with open(events_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 변수 초기화
    team_possession = {}
    total_duration = 0

    # 데이터 분석
    for event in data:
        possession_team = event.get("possession_team", {}).get("name", None)
        duration = event.get("duration", 0)
        total_duration += duration

        # 팀별 점유 시간 계산
        if possession_team:
            team_possession[possession_team] = team_possession.get(possession_team, 0) + duration

    # 점유율 계산
    possession_percentages = {
        team: (time / total_duration) * 100 for team, time in team_possession.items()
    }

    return possession_percentages, total_duration / 60

events_file_path = 'C:/Users/user/local/GitHub/open-data/data/events/3773457.json'
possession_percentages, total_minutes = calculate_possession(events_file_path)
print("볼 점유율:", possession_percentages)
print("총 경기 시간 (분):", total_minutes)
