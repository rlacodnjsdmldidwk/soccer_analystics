import os
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
from tqdm import tqdm

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
                "pass_success_rate": 0,
                "fouls": 0
            }

        event_type = event["type"]["name"]
        possession_team = event.get("possession_team", {}).get("name", None)
        duration = event.get("duration", 0)
        total_duration += duration
        if possession_team:
            team_possession[possession_team] = team_possession.get(possession_team, 0) + duration

        # 통계 계산
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

    # 점유율 계산
    possession_percentages = {
        team: (time / total_duration) * 100 for team, time in team_possession.items()
    }

    # 패스 성공률 계산
    for team in teams:
        if teams[team]["passes"] > 0:
            teams[team]["pass_success_rate"] = round((teams[team]["pass_success"] / teams[team]["passes"]) * 100, 2)
        else:
            teams[team]["pass_success_rate"] = 0

    return teams, sorted(list(team_names)), possession_percentages

def extract_turnover_data(events_file_path, side):
    with open(events_file_path, 'r', encoding='utf-8') as f:
        events_data = json.load(f)

    if side == 'home':
        team_name = events_data[0]['team']['name']
    elif side == 'away':
        team_name = events_data[1]['team']['name']

    event_id = [event['id'] for event in events_data if event.get('team', {}).get('name') != team_name]

    failed_passes_location = []
    lost_duels_location = []
    dribble_losts_location = []

    for event in events_data:
        related_event_list = event.get('related_events', [])

        # 실패한 패스
        if event["type"]["name"] == "Pass" and "outcome" in event.get("pass", {}) and \
                event["pass"]["outcome"]["name"] == "Incomplete" and event["team"]["name"] == team_name:
            failed_passes_location.append(event['location'])

        # 패배한 듀얼
        elif event["type"]["name"] == "Duel" and "outcome" in event.get("duel", {}) and \
                event["duel"]["outcome"]["name"] in {"Lost In Play", "Lost Out"} and event["team"]["name"] == team_name:
            lost_duels_location.append(event['location'])

        # 드리블 실패
        elif event["type"]["name"] == "Carry" and event["team"]["name"] == team_name and \
                any(related_event in event_id for related_event in related_event_list):
            dribble_losts_location.append(event['location'])

    return failed_passes_location, lost_duels_location, dribble_losts_location, team_name, side

def draw_heatmap(data_imported, title):
    field_x = 120
    field_y = 80
    num_bins_x = 24
    num_bins_y = 16
    bin_x = field_x / num_bins_x
    bin_y = field_y / num_bins_y

    location_data = data_imported
    heatmap = np.zeros((num_bins_y, num_bins_x))

    for x, y in location_data:
        bin_x_index = min(int(x // bin_x), num_bins_x - 1)
        bin_y_index = min(int(y // bin_y), num_bins_y - 1)
        heatmap[bin_y_index, bin_x_index] += 1

    fig, ax = plt.subplots(figsize=(12, 8))

    # 축구장 외곽선
    ax.plot([0, 0, field_x, field_x, 0], [0, field_y, field_y, 0, 0], color="black")
    ax.plot([field_x / 2, field_x / 2], [0, field_y], color="black")

    center_circle = plt.Circle((field_x / 2, field_y / 2), 9.15, color="black", fill=False)
    ax.add_patch(center_circle)
    ax.scatter(field_x / 2, field_y / 2, color="black", s=20)

    # 페널티 구역
    ax.plot([0, 16.5, 16.5, 0],
            [(field_y - 40.3) / 2, (field_y - 40.3) / 2, (field_y + 40.3) / 2, (field_y + 40.3) / 2], color="black")
    ax.plot([field_x, field_x - 16.5, field_x - 16.5, field_x],
            [(field_y - 40.3) / 2, (field_y - 40.3) / 2, (field_y + 40.3) / 2, (field_y + 40.3) / 2], color="black")

    # 골키퍼 구역
    ax.plot([0, 5.5, 5.5, 0],
            [(field_y - 18.32) / 2, (field_y - 18.32) / 2, (field_y + 18.32) / 2, (field_y + 18.32) / 2], color="black")
    ax.plot([field_x, field_x - 5.5, field_x - 5.5, field_x],
            [(field_y - 18.32) / 2, (field_y - 18.32) / 2, (field_y + 18.32) / 2, (field_y + 18.32) / 2],
            color="black")

    # 골대
    ax.plot([0, -2], [(field_y - 7.32) / 2, (field_y - 7.32) / 2], color="black")
    ax.plot([0, -2], [(field_y + 7.32) / 2, (field_y + 7.32) / 2], color="black")
    ax.plot([field_x, field_x + 2], [(field_y - 7.32) / 2, (field_y - 7.32) / 2], color="black")
    ax.plot([field_x, field_x + 2], [(field_y + 7.32) / 2, (field_y + 7.32) / 2], color="black")

    ax.set_xlim(-5, field_x + 5)
    ax.set_ylim(-5, field_y + 5)
    ax.set_aspect("equal", adjustable="box")

    heatmap_img = ax.imshow(heatmap, cmap='YlGnBu', interpolation='nearest', alpha=0.6, extent=[0, field_x, 0, field_y])
    ax.set_title(title, fontsize=20, fontweight='bold')
    ax.set_xlabel("Width (m)")
    ax.set_ylabel("Height (m)")

    cbar = plt.colorbar(heatmap_img, ax=ax)
    cbar.set_label('count', rotation=270, labelpad=20, fontsize=12)
    plt.axis('off')
    plt.show()

#--- 메인 코드 시작 ---#

# match_id 및 승패 정보 추출
folder_path_laliga = '/Users/kyuhyeon/coding/python/Infophy_TeamProject/Laliga_10_21'
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

folder_path_events = '/Users/kyuhyeon/Documents/data/events'

# 데이터 저장용 리스트 초기화
winning_pass_locations = []
losing_pass_locations = []

winning_shot_locations = []
losing_shot_locations = []

winning_turnover_locations = []
losing_turnover_locations = []

winning_passes = []
losing_passes = []

winning_passes_success_rates = []
losing_passes_success_rates = []

winning_shots = []
losing_shots = []

winning_possession_rates = []
losing_possession_rates = []

winner_turnover_count = []
loser_turnover_count = []
winner_turnover_count_total = []
loser_turnover_count_total = []

winner_foul_count = []
loser_foul_count = []

total_matches = len(match_results)

# 메인 루프: 모든 경기 데이터 처리
for i, match_result in tqdm(enumerate(match_results), total=total_matches, desc="Processing matches", unit="match"):
    match_id = match_result['match_id']
    winner_side = match_result['winner']
    loser_side = match_result['loser']

    event_file_path = os.path.join(folder_path_events, f'{match_id}.json')
    if not os.path.exists(event_file_path):
        continue

    with open(event_file_path, 'r', encoding='utf-8') as f:
        event_data = json.load(f)

    # 팀 데이터 추출
    teams, team_names, possession_percentages = extract_match_data(event_data)

    # winner_team, loser_team 이름 결정
    if winner_side == 'Home':
        winner_team = team_names[0]  # 홈팀
        loser_team = team_names[1]  # 어웨이팀
    else:
        winner_team = team_names[1]  # 어웨이팀
        loser_team = team_names[0]  # 홈팀

    # 턴오버 데이터 추출 (승리팀)
    fp_w, ld_w, dl_w, _, _ = extract_turnover_data(event_file_path, winner_side.lower())
    winning_turnover_locations.extend(fp_w)
    winning_turnover_locations.extend(ld_w)
    winning_turnover_locations.extend(dl_w)

    # 턴오버 데이터 추출 (패배팀)
    fp_l, ld_l, dl_l, _, _ = extract_turnover_data(event_file_path, loser_side.lower())
    losing_turnover_locations.extend(fp_l)
    losing_turnover_locations.extend(ld_l)
    losing_turnover_locations.extend(dl_l)

    # 패스, 슛 위치 추출
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
                outcome = event.get("shot", {}).get("outcome", {}).get("name", "")
                if outcome in ['Goal', "Saved", "Post"]:
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
                outcome = event.get("shot", {}).get("outcome", {}).get("name", "")
                if outcome in ['Goal', "Saved", "Post"]:
                    location = event.get("location")
                    if location:
                        losing_shot_locations.append(tuple(location))

    # 턴오버 개수 계산
    # 전체 턴오버
    winner_total_turnover = len(fp_w) + len(ld_w) + len(dl_w)
    loser_total_turnover = len(fp_l) + len(ld_l) + len(dl_l)
    winner_turnover_count_total.append(winner_total_turnover)
    loser_turnover_count_total.append(loser_total_turnover)

    # 하프라인 이전 (x<60)에 발생한 턴오버
    fp_w_half = [(x, y) for x, y in fp_w if x < 60]
    ld_w_half = [(x, y) for x, y in ld_w if x < 60]
    dl_w_half = [(x, y) for x, y in dl_w if x < 60]
    fp_l_half = [(x, y) for x, y in fp_l if x < 60]
    ld_l_half = [(x, y) for x, y in ld_l if x < 60]
    dl_l_half = [(x, y) for x, y in dl_l if x < 60]

    winner_half_turnover = len(fp_w_half) + len(ld_w_half) + len(dl_w_half)
    loser_half_turnover = len(fp_l_half) + len(ld_l_half) + len(dl_l_half)

    winner_turnover_count.append(winner_half_turnover)
    loser_turnover_count.append(loser_half_turnover)

    # 통계치 추출
    winning_passes.append(teams[winner_team]['passes'])
    losing_passes.append(teams[loser_team]['passes'])

    winning_passes_success_rates.append(teams[winner_team]['pass_success_rate'])
    losing_passes_success_rates.append(teams[loser_team]['pass_success_rate'])

    winning_shots.append(teams[winner_team]['on_target'])
    losing_shots.append(teams[loser_team]['on_target'])

    winning_possession_rates.append(possession_percentages[winner_team])
    losing_possession_rates.append(possession_percentages[loser_team])

    winner_foul_count.append(teams[winner_team]['fouls'])
    loser_foul_count.append(teams[loser_team]['fouls'])

    # 진행 상황 출력
    # print(f"Progress: {i + 1}/{total_matches}")

# 히트맵 생성
draw_heatmap(winning_pass_locations, 'Winning Team Pass Heatmap')
draw_heatmap(losing_pass_locations, 'Losing Team Pass Heatmap')
draw_heatmap(winning_shot_locations, 'Winning Team Shot Heatmap')
draw_heatmap(losing_shot_locations, 'Losing Team Shot Heatmap')
draw_heatmap(winning_turnover_locations, 'Winning Team Turnover Heatmap')
draw_heatmap(losing_turnover_locations, 'Losing Team Turnover Heatmap')

# 평균 계산
winning_pass_average = np.mean(winning_passes)
losing_pass_average = np.mean(losing_passes)

winning_passes_success_rate_average = np.mean(winning_passes_success_rates)
losing_passes_success_rate_average = np.mean(losing_passes_success_rates)

winning_shots_average = np.mean(winning_shots)
losing_shots_average = np.mean(losing_shots)

winning_possession_rate_average = np.mean(winning_possession_rates)
losing_possession_rate_average = np.mean(losing_possession_rates)

winning_total_turnover_average = np.mean(winner_turnover_count_total)
losing_total_turnover_average = np.mean(loser_turnover_count_total)

winning_turnover_average = np.mean(winner_turnover_count)
losing_turnover_average = np.mean(loser_turnover_count)

winning_fouls_average = np.mean(winner_foul_count)
losing_fouls_average = np.mean(loser_foul_count)

def plot_distribution_and_test(winning_data, losing_data, title, xlabel):
    t_stat, p_value = stats.ttest_ind(winning_data, losing_data, equal_var=False)

    print(title)
    print("Winning avg:", np.mean(winning_data))
    print("Losing avg:", np.mean(losing_data))
    print(f"{title} t-statistic: {t_stat}")
    print(f"{title} p-value: {p_value}")
    if p_value < 0.05:
        print(f"{title}와(과) 경기 승패 간에 유의미한 차이가 존재합니다.")
    else:
        print(f"{title}와(과) 경기 승패 간에 유의미한 차이가 존재하지 않습니다.")
    print('---------------')

    win_mean = np.mean(winning_data)
    win_std = np.std(winning_data)
    lose_mean = np.mean(losing_data)
    lose_std = np.std(losing_data)

    x_win = np.linspace(min(winning_data), max(winning_data), 100)
    y_win = stats.norm.pdf(x_win, win_mean, win_std)
    x_lose = np.linspace(min(losing_data), max(losing_data), 100)
    y_lose = stats.norm.pdf(x_lose, lose_mean, lose_std)

    plt.figure()
    plt.plot(x_win, y_win, color='skyblue', linestyle='-', linewidth=2, label='Winning Team Normal Dist.')
    plt.plot(x_lose, y_lose, color='pink', linestyle='-', linewidth=2, label='Losing Team Normal Dist.')
    sns.kdeplot(winning_data, color='blue', label='Winning Team')
    sns.kdeplot(losing_data, color='red', label='Losing Team')
    plt.title(f'Distribution of {title}: Winning vs Losing Teams')
    plt.xlabel(xlabel)
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    plt.show()

# T-test 및 분포 그래프
plot_distribution_and_test(winning_passes, losing_passes, "Passes", "Number of Passes")
plot_distribution_and_test(winning_passes_success_rates, losing_passes_success_rates, "Pass Accuracy", "Pass Accuracy (%)")
plot_distribution_and_test(winning_shots, losing_shots, "Shots On Target", "Number of On Target Shots")
plot_distribution_and_test(winning_possession_rates, losing_possession_rates, "Possession Rate", "Possession Rate (%)")
plot_distribution_and_test(winner_turnover_count_total, loser_turnover_count_total, "Total Turnover", "Total Number of Turnover")
plot_distribution_and_test(winner_turnover_count, loser_turnover_count, "Turnover (Half Field)", "Number of Turnover in Own Half")
plot_distribution_and_test(winner_foul_count, loser_foul_count, "Fouls", "Number of Fouls")
