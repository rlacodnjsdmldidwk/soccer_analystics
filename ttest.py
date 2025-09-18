import os
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats

def extract_match_data(event_data):
    teams = {}
    team_names = set()
    team_possession = {}
    total_duration = 0

    for event in event_data:
        team_name = event["team"]["name"]
        team_names.add(team_name)

        # 팀별 초기화
        if team_name not in teams:
            teams[team_name] = {
                "shots": 0,
                "on_target": 0,
                "passes": 0,
                "pass_success": 0,
                "pass_success_rate": 0,
                "fouls": 0
            }

        event_type = event["type"]["name"]
        # 볼 점유율 계산
        possession_team = event.get("possession_team", {}).get("name", None)
        duration = event.get("duration", 0)
        total_duration += duration
        team_possession[possession_team] = team_possession.get(possession_team, 0) + duration

        # 경기 통계 계산
        if event_type == "Shot":
            teams[team_name]["shots"] += 1
            outcome = event.get("shot", {}).get("outcome", {}).get("name", "")
            if outcome in ["Goal", "Saved", "Post"]:
                teams[team_name]["on_target"] += 1
        elif event_type == "Pass":
            teams[team_name]["passes"] += 1
            if "outcome" not in event.get("pass", {}):
                teams[team_name]["pass_success"] += 1
        elif event_type in ["Foul Committed", "Bad Behaviour"]:
            teams[team_name]["fouls"] += 1

    # 볼 점유율 계산
    possession_percentages = {
        team: (time / total_duration) * 100 for team, time in team_possession.items()
    }

    # 패스 성공률 계산
    for team in teams:
        teams[team]["pass_success_rate"] = round(
            (teams[team]["pass_success"] / teams[team]["passes"]) * 100, 2)

    return teams, sorted(list(team_names)), possession_percentages


def extract_turnover_data(events_file_path, side):
    """
    홈팀 또는 어웨이팀의 턴오버 이벤트를 시각화
    턴오버를 실패한 패스, 패배한 듀얼, 드리블 실패로 구분

    매개변수:
    - events_file_path (str): 경기 이벤트 데이터를 포함한 JSON 파일 경로
    - lineup_file_path (str): 라인업 데이터 파일 경로
    - side (str): "home" 또는 "away"를 지정해 특정 팀 선택

    반환값:
    - None: 턴오버 맵을 화면에 출력
    """

    # 데이터 로드
    with open(events_file_path, 'r', encoding='utf-8') as f:
        events_data = json.load(f)

    # 선택된 팀 이름
    if side == 'home':
        team_name = events_data[0]['team']['name']
    elif side == 'away':
        team_name = events_data[1]['team']['name']

    # 전체 event id 추출 -> 드리블 실패 데이터 추출에서 사용
    event_id = [event['id'] for event in events_data if event.get('team', {}).get('name') != team_name]

    # 위치 데이터 추출
    failed_passes_location = []
    lost_duels_location = []
    dribble_losts_location = []
    for event in events_data:

        related_event_list = event.get('related_events', [])

        # 실패한 패스 필터링
        if event["type"]["name"] == "Pass" and "outcome" in event.get("pass", {}) and \
                event["pass"]["outcome"]["name"] == "Incomplete" and event["team"]["name"] == team_name:

            failed_passes_location.append(event['location'])

            # 패배한 듀얼 필터링
        elif event["type"]["name"] == "Duel" and "outcome" in event.get("duel", {}) and \
                event["duel"]["outcome"]["name"] in {"Lost In Play", "Lost Out"} and event["team"]["name"] == team_name:

            lost_duels_location.append(event['location'])

        # 드리블 실패 필터링
        elif event["type"]["name"] == "Carry" and event["team"]["name"] == team_name and \
                any(related_event in event_id for related_event in related_event_list):

            dribble_losts_location.append(event['location'])

    return failed_passes_location, lost_duels_location, dribble_losts_location, team_name, side

def draw_heatmap(data_imported, title):
    """
    축구장 위에 히트맵을 그리는 함수

    매개변수:
    - data_imported: 이벤트 위치를 나타내는 (x, y) 튜플의 리스트
    - title: 히트맵 제목
    """
    # 축구장 크기 (미터)
    field_x = 120  # 가로
    field_y = 80   # 세로

    # 구간 크기 (가로 24개, 세로 16개)
    num_bins_x = 24
    num_bins_y = 16
    bin_x = field_x / num_bins_x
    bin_y = field_y / num_bins_y

    # 패스 데이터 (x, y 좌표)
    location_data = data_imported

    # 히트맵을 위한 2D 배열 (이벤트 개수를 카운트)
    heatmap = np.zeros((num_bins_y, num_bins_x))

    # 이벤트를 각 구간에 분류하고 개수 카운트
    for x, y in location_data:
        # 가로 (x) 위치
        bin_x_index = min(int(x // bin_x), num_bins_x - 1)

        # 세로 (y) 위치
        bin_y_index = min(int(y // bin_y), num_bins_y - 1)

        # 해당 구간의 이벤트 개수 증가
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
    heatmap_img = ax.imshow(heatmap, cmap='YlGnBu', interpolation='nearest', alpha=0.6, extent=[0, field_x, 0, field_y])

    # 축구장 크기와 구간 표시
    ax.set_title(title, fontsize=20, fontweight='bold')
    ax.set_xlabel("Width (m)")
    ax.set_ylabel("Height (m)")

    # 색상 범례 추가 (Colorbar)
    cbar = plt.colorbar(heatmap_img, ax=ax)
    cbar.set_label('count', rotation=270, labelpad=20, fontsize=12)

    # 범례 구간 설정 (색상에 대한 설명)
    ticks = list(range(1, int(np.max(heatmap)) + 1, max(int(np.max(heatmap) / 4), 1)))
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f'{i}' for i in ticks])

    plt.axis('off')
    plt.show()

# 여러개의 json 파일에서 match_id, 승패 정보 추출 추출
folder_path_laliga = 'C:/CODING/python/Infophy_TeamProject/Laliga_10_21'
json_files_laliga = [f for f in os.listdir(folder_path_laliga) if f.endswith('.json')]

# 승리 결과를 저장할 리스트
match_results = []

# 폴더 내 모든 JSON 파일을 순차적으로 처리
for filename in os.listdir(folder_path_laliga):
    if filename.endswith('.json'):  # JSON 파일만 처리
        file_path = os.path.join(folder_path_laliga, filename)

        # JSON 파일 로드
        with open(file_path, 'r', encoding='utf-8') as f:
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

# match_id를 이용해 경기 이벤트 데이터 로드
folder_path_events = 'C:/Users/user/local/GitHub/open-data/data/events'

# 히트맵 데이터 초기화 (승리팀과 패배팀 각각)
winning_pass_locations = []
losing_pass_locations = []

winning_shot_locations = []
losing_shot_locations = []

winning_turnover_locations = []
losing_turnover_locations = []

# 턴오버 데이터 추출을 위한 루프
for i, match_result in enumerate(match_results):
    match_id = match_result['match_id']
    winner_side = match_result['winner']
    loser_side = match_result['loser']

    event_file_path = os.path.join(folder_path_events, f'{match_id}.json')

    if os.path.exists(event_file_path):
        with open(event_file_path, 'r', encoding='utf-8') as f:
            event_data = json.load(f)
    else:
        print(f"Warning: {match_id}에 대한 경기 파일이 존재하지 않습니다.")
        continue

    # 각 팀 데이터 추출
    teams, team_names, possession_percentages = extract_match_data(event_data)

    # 승리팀과 패배팀의 이름 추출
    if winner_side == 'Home':
        winner_team = team_names[0]  # 홈 팀
        loser_team = team_names[1]   # 어웨이 팀
    else:
        winner_team = team_names[1]  # 어웨이 팀
        loser_team = team_names[0]   # 홈 팀

    # 턴오버 데이터 추출 (승리팀)
    failed_passes_location_winner, lost_duels_location_winner, dribble_losts_location_winner, _, _ = extract_turnover_data(
        event_file_path, winner_side.lower())
    winning_turnover_locations.extend(failed_passes_location_winner)
    winning_turnover_locations.extend(lost_duels_location_winner)
    winning_turnover_locations.extend(dribble_losts_location_winner)

    # 턴오버 데이터 추출 (패배팀)
    failed_passes_location_loser, lost_duels_location_loser, dribble_losts_location_loser, _, _ = extract_turnover_data(
        event_file_path, loser_side.lower())
    losing_turnover_locations.extend(failed_passes_location_loser)
    losing_turnover_locations.extend(lost_duels_location_loser)
    losing_turnover_locations.extend(dribble_losts_location_loser)

    # 패스 위치 및 슛 위치 데이터 추출
    for event in event_data:
        if event["team"]["name"] == winner_team:
            if event["type"]["name"] == "Pass":
                location = event.get("location")
                end_location = event.get("pass", {}).get("end_location")
                if location:
                    winning_pass_locations.append(tuple(location))
                if end_location:
                    winning_pass_locations.append(tuple(end_location))
            elif event["type"]["name"] == "Shot":
                if event.get("shot", {}).get("outcome", {}).get("name", "") in ['Goal', "Saved", "Post"]:
                    location = event.get("location")
                    if location:
                        winning_shot_locations.append(tuple(location))
        elif event["team"]["name"] == loser_team:
            if event["type"]["name"] == "Pass":
                location = event.get("location")
                end_location = event.get("pass", {}).get("end_location")
                if location:
                    losing_pass_locations.append(tuple(location))
                if end_location:
                    losing_pass_locations.append(tuple(end_location))
            elif event["type"]["name"] == "Shot":
                if event.get("shot", {}).get("outcome", {}).get("name", "") in ['Goal', "Saved", "Post"]:
                    location = event.get("location")
                    if location:
                        losing_shot_locations.append(tuple(location))

    print(f'{i + 1} / {len(match_results)}')

# 히트맵 생성
# 승리팀 패스 히트맵
draw_heatmap(winning_pass_locations, 'Winning Team Pass Heatmap')

# 패배팀 패스 히트맵
draw_heatmap(losing_pass_locations, 'Losing Team Pass Heatmap')

# 승리팀 슛 히트맵
draw_heatmap(winning_shot_locations, 'Winning Team Shot Heatmap')

# 패배팀 슛 히트맵
draw_heatmap(losing_shot_locations, 'Losing Team Shot Heatmap')

# 승리팀 턴오버 히트맵
draw_heatmap(winning_turnover_locations, 'Winning Team Turnover Heatmap')

# 패배팀 턴오버 히트맵
draw_heatmap(losing_turnover_locations, 'Losing Team Turnover Heatmap')

# 패스 개수 초기화
winning_passes = []
losing_passes = []

# 패스 정확도 초기화
winning_passes_success_rates = []
losing_passes_success_rates = []

# 유효슛 개수 초기화
winning_shots = []
losing_shots = []

# 점유율 초기화
winning_possession_rates = []
losing_possession_rates = []

# 턴오버 개수 초기화
winner_turnover_count = []
loser_turnover_count = []
winner_turnover_count_total = []
loser_turnover_count_total = []

# 파울 개수 초기화
winner_foul_count = []
loser_foul_count = []

for i, match_result in enumerate(match_results):
    match_id = match_result['match_id']
    winner_team = match_result['winner']
    loser_team = match_result['loser']

    event_file_path = os.path.join(folder_path_events, f'{match_id}.json')

    if os.path.exists(event_file_path):
        with open(event_file_path, 'r', encoding='utf-8') as f:
            event_data = (json.load(f))

    else:
        print(f"Warning: {match_id}에 대한 경기 파일이 존재하지 않습니다.")

    # 각 팀 데이터 추출
    teams, team_names, possession_percentages = extract_match_data(event_data)

    # 승리팀과 패배팀의 턴오버 개수 추출
    if winner_team == 'Home':
        failed_passes_location, lost_duels_location, dribble_losts_location, team_name, side = extract_turnover_data(
            event_file_path, winner_team.lower())
        winner_turnover_count_total.append(
            len(failed_passes_location) + len(lost_duels_location) + len(dribble_losts_location))

        failed_passes_location = [(x, y) for x, y in failed_passes_location if x < 60]
        lost_duels_location = [(x, y) for x, y in lost_duels_location if x < 60]
        dribble_losts_location = [(x, y) for x, y in dribble_losts_location if x < 60]
        winner_turnover_count.append(
            len(failed_passes_location) + len(lost_duels_location) + len(dribble_losts_location))

        failed_passes_location, lost_duels_location, dribble_losts_location, team_name, side = extract_turnover_data(
            event_file_path, loser_team.lower())
        loser_turnover_count_total.append(
            len(failed_passes_location) + len(lost_duels_location) + len(dribble_losts_location))

        failed_passes_location = [(x, y) for x, y in failed_passes_location if x < 60]
        lost_duels_location = [(x, y) for x, y in lost_duels_location if x < 60]
        dribble_losts_location = [(x, y) for x, y in dribble_losts_location if x < 60]
        loser_turnover_count.append(
            len(failed_passes_location) + len(lost_duels_location) + len(dribble_losts_location))

        winner_team = team_names[0]
        loser_team = team_names[1]

    elif winner_team == 'Away':
        failed_passes_location, lost_duels_location, dribble_losts_location, team_name, side = extract_turnover_data(
            event_file_path, winner_team.lower())
        winner_turnover_count_total.append(
            len(failed_passes_location) + len(lost_duels_location) + len(dribble_losts_location))

        failed_passes_location = [(x, y) for x, y in failed_passes_location if x < 60]
        lost_duels_location = [(x, y) for x, y in lost_duels_location if x < 60]
        dribble_losts_location = [(x, y) for x, y in dribble_losts_location if x < 60]

        winner_turnover_count.append(
            len(failed_passes_location) + len(lost_duels_location) + len(dribble_losts_location))
        loser_turnover_count_total.append(
            len(failed_passes_location) + len(lost_duels_location) + len(dribble_losts_location))

        failed_passes_location = [(x, y) for x, y in failed_passes_location if x < 60]
        lost_duels_location = [(x, y) for x, y in lost_duels_location if x < 60]
        dribble_losts_location = [(x, y) for x, y in dribble_losts_location if x < 60]

        failed_passes_location, lost_duels_location, dribble_losts_location, team_name, side = extract_turnover_data(
            event_file_path, loser_team.lower())
        loser_turnover_count.append(
            len(failed_passes_location) + len(lost_duels_location) + len(dribble_losts_location))

        winner_team = team_names[1]
        loser_team = team_names[0]

    # 승리팀과 패배팀의 패스 개수 추출
    winning_passes.append(teams[winner_team]['passes'])
    losing_passes.append(teams[loser_team]['passes'])

    # 승리팀과 패배팀의 패스 성공율 추출
    winning_passes_success_rates.append(teams[winner_team]['pass_success_rate'])
    losing_passes_success_rates.append(teams[loser_team]['pass_success_rate'])

    # 승리팀과 패배팀의 유효슛 개수 추출
    winning_shots.append(teams[winner_team]['on_target'])
    losing_shots.append(teams[loser_team]['on_target'])

    # 승리팀과 패배팀의 점유율 추출
    winning_possession_rates.append(possession_percentages[winner_team])
    losing_possession_rates.append(possession_percentages[loser_team])

    # 승리팀과 패배팀의 파울 개수 추출
    winner_foul_count.append(teams[winner_team]['fouls'])
    loser_foul_count.append(teams[loser_team]['fouls'])

    print(f'{i + 1} in {len(match_results)}')

# 패스 평균 계산
winning_pass_average = sum(winning_passes) / len(winning_passes)
losing_pass_average = sum(losing_passes) / len(losing_passes)

# 패스 정확도 평균 계산
winning_passes_success_rate_average = sum(winning_passes_success_rates) / len(winning_passes_success_rates)
losing_passes_success_rate_average = sum(losing_passes_success_rates) / len(losing_passes_success_rates)

# 유효슛 평균 계산
winning_shots_average = sum(winning_shots) / len(winning_shots)
losing_shots_average = sum(losing_shots) / len(losing_shots)

# 점유율 평균 계산
winning_possession_rate_average = sum(winning_possession_rates) / len(winning_possession_rates)
losing_possession_rate_average = sum(losing_possession_rates) / len(losing_possession_rates)

# 전체 턴오버 평균 계산
winning_total_turnover_average = sum(winner_turnover_count_total) / len(winner_turnover_count_total)
losing_total_turnover_average = sum(loser_turnover_count_total) / len(loser_turnover_count_total)

# 턴오버 평균 계산
winning_turnover_average = sum(winner_turnover_count) / len(winner_turnover_count)
losing_turnover_average = sum(loser_turnover_count) / len(loser_turnover_count)

# 턴오버 평균 계산
winning_fouls_average = sum(winner_foul_count) / len(winner_foul_count)
losing_fouls_average = sum(loser_foul_count) / len(loser_foul_count)

# 정규분포를 위한 데이터 생성
win_mean = np.mean(winning_passes)
win_std = np.std(winning_passes)
lose_mean = np.mean(losing_passes)
lose_std = np.std(losing_passes)

x_win = np.linspace(min(winning_passes), max(winning_passes), 100)
y_win = stats.norm.pdf(x_win, win_mean, win_std)

x_lose = np.linspace(min(losing_passes), max(losing_passes), 100)
y_lose = stats.norm.pdf(x_lose, lose_mean, lose_std)

# 패스 T-test 진행
t_stat, p_value = stats.ttest_ind(winning_passes, losing_passes)
print('Pass')
print(winning_pass_average, losing_pass_average)
print(f"pass t-statistic: {t_stat}")
print(f"pass p-value: {p_value}")

if p_value < 0.05:
    print("패스 개수와 경기 승패 간에 유의미한 차이가 존재합니다.")
else:
    print("패스 개수와 경기 승패 간에 유의미한 차이가 존재하지 않습니다.")

print('---------------')


# 패스 t-test 정규분포 그래프
plt.figure()
plt.plot(x_win, y_win, color='skyblue', linestyle='-', linewidth=2, label='Winning Team Normal Dist.')
plt.plot(x_lose, y_lose, color='pink', linestyle='-', linewidth=2, label='Losing Team Normal Dist.')
sns.kdeplot(winning_passes, color='blue', label='Winning Team Passes')
sns.kdeplot(losing_passes, color='red', label='Losing Team Passes')
plt.title('Distribution of Passes: Winning vs Losing Teams')
plt.xlabel('Number of Passes')
plt.ylabel('Density')
plt.legend()
plt.grid(True)

# 정규분포를 위한 데이터 생성
win_mean = np.mean(winning_passes_success_rates)
win_std = np.std(winning_passes_success_rates)
lose_mean = np.mean(losing_passes_success_rates)
lose_std = np.std(losing_passes_success_rates)

x_win = np.linspace(min(winning_passes_success_rates), max(winning_passes_success_rates), 100)
y_win = stats.norm.pdf(x_win, win_mean, win_std)

x_lose = np.linspace(min(losing_passes_success_rates), max(losing_passes_success_rates), 100)
y_lose = stats.norm.pdf(x_lose, lose_mean, lose_std)

# 패스 성공율 T-test 진행
t_stat, p_value = stats.ttest_ind(winning_passes_success_rates, losing_passes_success_rates)
print('Pass Accuracy')
print(winning_passes_success_rate_average, losing_passes_success_rate_average)
print(f"Pass Accuracy t-statistic: {t_stat}")
print(f"Pass Accuracy p-value: {p_value}")

if p_value < 0.05:
    print("패스 성공율과 경기 승패 간에 유의미한 차이가 존재합니다.")
else:
    print("패스 성공율과 경기 승패 간에 유의미한 차이가 존재하지 않습니다.")

print('---------------')

# 패스 성공율과 정규분포 그래프
plt.figure()
plt.plot(x_win, y_win, color='skyblue', linestyle='-', linewidth=2, label='Winning Team Normal Dist.')
plt.plot(x_lose, y_lose, color='pink', linestyle='-', linewidth=2, label='Losing Team Normal Dist.')
sns.kdeplot(winning_passes_success_rates, color='blue', label='Winning Team Pass Accuracy')
sns.kdeplot(losing_passes_success_rates, color='red', label='Losing Team Pass Accuracy')
plt.title('Distribution of Pass Accuracy: Winning vs Losing Teams')
plt.xlabel('Pass Accuracy')
plt.ylabel('Density')
plt.legend()
plt.grid(True)

# 정규분포를 위한 데이터 생성
win_mean = np.mean(winning_shots)
win_std = np.std(winning_shots)
lose_mean = np.mean(losing_shots)
lose_std = np.std(losing_shots)

x_win = np.linspace(min(winning_shots), max(winning_shots), 100)
y_win = stats.norm.pdf(x_win, win_mean, win_std)

x_lose = np.linspace(min(losing_shots), max(losing_shots), 100)
y_lose = stats.norm.pdf(x_lose, lose_mean, lose_std)

# 유효슛 T-test 진행
t_stat, p_value = stats.ttest_ind(winning_shots, losing_shots)
print('Shots')
print(winning_shots_average, losing_shots_average)
print(f"Shots t-statistic: {t_stat}")
print(f"Shots p-value: {p_value}")

if p_value < 0.05:
    print("유효슛과 경기 승패 간에 유의미한 차이가 존재합니다.")
else:
    print("유효슛과 경기 승패 간에 유의미한 차이가 존재하지 않습니다.")

print('---------------')

# 유효슛 정규분포 그래프
plt.figure()
plt.plot(x_win, y_win, color='skyblue', linestyle='-', linewidth=2, label='Winning Team Normal Dist.')
plt.plot(x_lose, y_lose, color='pink', linestyle='-', linewidth=2, label='Losing Team Normal Dist.')
sns.kdeplot(winning_shots, color='blue', label='Winning Team Shots')
sns.kdeplot(losing_shots, color='red', label='Losing Team Shots')
plt.title('Distribution of Shots: Winning vs Losing Teams')
plt.xlabel('Number of On Target Shots')
plt.ylabel('Density')
plt.legend()
plt.grid(True)

# 정규분포를 위한 데이터 생성
win_mean = np.mean(winning_possession_rates)
win_std = np.std(winning_possession_rates)
lose_mean = np.mean(losing_possession_rates)
lose_std = np.std(losing_possession_rates)

x_win = np.linspace(min(winning_possession_rates), max(winning_possession_rates), 100)
y_win = stats.norm.pdf(x_win, win_mean, win_std)

x_lose = np.linspace(min(losing_possession_rates), max(losing_possession_rates), 100)
y_lose = stats.norm.pdf(x_lose, lose_mean, lose_std)

# 점유율 T-test 진행
t_stat, p_value = stats.ttest_ind(winning_possession_rates, losing_possession_rates)
print('Possession Rate')
print(winning_possession_rate_average, losing_possession_rate_average)
print(f"Possession Rate t-statistic: {t_stat}")
print(f"Possession Rate p-value: {p_value}")

if p_value < 0.05:
    print("점유율과 경기 승패 간에 유의미한 차이가 존재합니다.")
else:
    print("점유율과 경기 승패 간에 유의미한 차이가 존재하지 않습니다.")

print('---------------')

# 점유율 정규분포 그래프
plt.figure()
plt.plot(x_win, y_win, color='skyblue', linestyle='-', linewidth=2, label='Winning Team Normal Dist.')
plt.plot(x_lose, y_lose, color='pink', linestyle='-', linewidth=2, label='Losing Team Normal Dist.')
sns.kdeplot(winning_possession_rates, color='blue', label='Winning Team Possession Rate')
sns.kdeplot(losing_possession_rates, color='red', label='Losing Team Possession Rate')
plt.title('Distribution of Possession Rate: Winning vs Losing Teams')
plt.xlabel('Possession Rate')
plt.ylabel('Density')
plt.legend()
plt.grid(True)

# 정규분포를 위한 데이터 생성
win_mean = np.mean(winner_turnover_count_total)
win_std = np.std(winner_turnover_count_total)
lose_mean = np.mean(loser_turnover_count_total)
lose_std = np.std(loser_turnover_count_total)

x_win = np.linspace(min(winner_turnover_count_total), max(winner_turnover_count_total), 100)
y_win = stats.norm.pdf(x_win, win_mean, win_std)

x_lose = np.linspace(min(loser_turnover_count_total), max(loser_turnover_count_total), 100)
y_lose = stats.norm.pdf(x_lose, lose_mean, lose_std)

# 전체 턴오버 T-test 진행
t_stat, p_value = stats.ttest_ind(winner_turnover_count_total, loser_turnover_count_total)
print('Total Turnover')
print(winning_turnover_average, losing_total_turnover_average)
print(f"Total Turnover t-statistic: {t_stat}")
print(f"Total Turnover p-value: {p_value}")

if p_value < 0.05:
    print("전체 턴오버 개수와 경기 승패 간에 유의미한 차이가 존재합니다.")
else:
    print("전체 턴오버 개수와 경기 승패 간에 유의미한 차이가 존재하지 않습니다.")

print('---------------')

# 전체 턴오버 정규분포 그래프
plt.figure()
plt.plot(x_win, y_win, color='skyblue', linestyle='-', linewidth=2, label='Winning Team Normal Dist.')
plt.plot(x_lose, y_lose, color='pink', linestyle='-', linewidth=2, label='Losing Team Normal Dist.')
sns.kdeplot(winner_turnover_count_total, color='blue', label='Winning Team Total Turnover')
sns.kdeplot(loser_turnover_count_total, color='red', label='Losing Team Total Turnover')
plt.title('Distribution of Total Turnover: Winning vs Losing Teams')
plt.xlabel('Total Number of Turnover')
plt.ylabel('Density')
plt.legend()
plt.grid(True)

# 정규분포를 위한 데이터 생성
win_mean = np.mean(winner_turnover_count)
win_std = np.std(winner_turnover_count)
lose_mean = np.mean(loser_turnover_count)
lose_std = np.std(loser_turnover_count)

x_win = np.linspace(min(winner_turnover_count), max(winner_turnover_count), 100)
y_win = stats.norm.pdf(x_win, win_mean, win_std)

x_lose = np.linspace(min(loser_turnover_count), max(loser_turnover_count), 100)
y_lose = stats.norm.pdf(x_lose, lose_mean, lose_std)

# 턴오버 T-test 진행
t_stat, p_value = stats.ttest_ind(winner_turnover_count, loser_turnover_count)
print('Turnover')
print(winning_turnover_average, losing_turnover_average)
print(f"Turnover t-statistic: {t_stat}")
print(f"Turnover p-value: {p_value}")

if p_value < 0.05:
    print("턴오버와 경기 승패 간에 유의미한 차이가 존재합니다.")
else:
    print("턴오버와 경기 승패 간에 유의미한 차이가 존재하지 않습니다.")

print('---------------')

# 턴오버 정규분포 그래프
plt.figure()
plt.plot(x_win, y_win, color='skyblue', linestyle='-', linewidth=2, label='Winning Team Normal Dist.')
plt.plot(x_lose, y_lose, color='pink', linestyle='-', linewidth=2, label='Losing Team Normal Dist.')
sns.kdeplot(winner_turnover_count, color='blue', label='Winning Team Turnover')
sns.kdeplot(loser_turnover_count, color='red', label='Losing Team Turnover')
plt.title('Distribution of Turnover: Winning vs Losing Teams')
plt.xlabel('Number of Turnover')
plt.ylabel('Density')
plt.legend()
plt.grid(True)

# 정규분포를 위한 데이터 생성
win_mean = np.mean(winner_foul_count)
win_std = np.std(winner_foul_count)
lose_mean = np.mean(loser_foul_count)
lose_std = np.std(loser_foul_count)

x_win = np.linspace(min(winner_foul_count), max(winner_foul_count), 100)
y_win = stats.norm.pdf(x_win, win_mean, win_std)

x_lose = np.linspace(min(loser_foul_count), max(loser_foul_count), 100)
y_lose = stats.norm.pdf(x_lose, lose_mean, lose_std)

# 파울 T-test 진행
t_stat, p_value = stats.ttest_ind(winner_foul_count, loser_foul_count)
print('Fouls')
print(winning_fouls_average, losing_fouls_average)
print(f"fouls t-statistic: {t_stat}")
print(f"fouls p-value: {p_value}")

if p_value < 0.05:
    print("파울 개수와 경기 승패 간에 유의미한 차이가 존재합니다.")
else:
    print("파울 개수와 경기 승패 간에 유의미한 차이가 존재하지 않습니다.")

print('---------------')

# 파울 t-test 정규분포 그래프
plt.figure()
plt.plot(x_win, y_win, color='skyblue', linestyle='-', linewidth=2, label='Winning Team Normal Dist.')
plt.plot(x_lose, y_lose, color='pink', linestyle='-', linewidth=2, label='Losing Team Normal Dist.')
sns.kdeplot(winner_foul_count, color='blue', label='Winning Team Fouls')
sns.kdeplot(loser_foul_count, color='red', label='Losing Team Fouls')
plt.title('Distribution of Fouls: Winning vs Losing Teams')
plt.xlabel('Number of Fouls')
plt.ylabel('Density')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()