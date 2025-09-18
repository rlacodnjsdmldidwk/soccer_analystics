import json
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter, defaultdict


    ## 축구장 그리기
def draw_soccer_field(ax, side, field_dimen=(120, 80)):
        """
        축구 필드 그리기

        매개변수:
        - ax (matplotlib.axes): 필드를 그릴 matplotlib 축
        - field_dimen (tuple): 필드의 크기 (길이, 너비)

        반환값:
        - ax (matplotlib.axes): 축구 필드가 그려진 matplotlib 축
        """
        field_length, field_width = field_dimen

        # 필드 외곽선
        ax.plot([0, 0, field_length, field_length, 0], [0, field_width, field_width, 0, 0], color="black")

        # 홈/어웨이 진영 배경색 표시
        if side == 'home':
            ax.add_patch(
                plt.Rectangle((0, 0), field_length / 2, field_width, color="lightblue", alpha=0.2, label="Home Side"))
            ax.add_patch(plt.Rectangle((field_length / 2, 0), field_length / 2, field_width, color="lightcoral", alpha=0.2,
                                       label="Away Side"))
        elif side == 'away':
            ax.add_patch(plt.Rectangle((field_length / 2, 0), field_length / 2, field_width, color="lightblue", alpha=0.2,
                                       label="Home Side"))
            ax.add_patch(
                plt.Rectangle((0, 0), field_length / 2, field_width, color="lightcoral", alpha=0.2, label="Away Side"))

        # 센터 라인
        ax.plot([field_length / 2, field_length / 2], [0, field_width], color="black")

        # 센터 서클
        center_circle = plt.Circle((field_length / 2, field_width / 2), 9.15, color="black", fill=False)
        ax.add_patch(center_circle)
        ax.scatter(field_length / 2, field_width / 2, color="black", s=20)  # 센터 스팟

        # 페널티 구역
        ax.plot([0, 16.5, 16.5, 0], [(field_width - 40.3) / 2, (field_width - 40.3) / 2,
                                     (field_width + 40.3) / 2, (field_width + 40.3) / 2], color="black")
        ax.plot([field_length, field_length - 16.5, field_length - 16.5, field_length],
                [(field_width - 40.3) / 2, (field_width - 40.3) / 2,
                 (field_width + 40.3) / 2, (field_width + 40.3) / 2], color="black")

        # 골키퍼 구역
        ax.plot([0, 5.5, 5.5, 0], [(field_width - 18.32) / 2, (field_width - 18.32) / 2,
                                   (field_width + 18.32) / 2, (field_width + 18.32) / 2], color="black")
        ax.plot([field_length, field_length - 5.5, field_length - 5.5, field_length],
                [(field_width - 18.32) / 2, (field_width - 18.32) / 2,
                 (field_width + 18.32) / 2, (field_width + 18.32) / 2], color="black")

        # 골대
        ax.plot([0, -2], [(field_width - 7.32) / 2, (field_width - 7.32) / 2], color="black")
        ax.plot([0, -2], [(field_width + 7.32) / 2, (field_width + 7.32) / 2], color="black")
        ax.plot([field_length, field_length + 2], [(field_width - 7.32) / 2, (field_width - 7.32) / 2], color="black")
        ax.plot([field_length, field_length + 2], [(field_width + 7.32) / 2, (field_width + 7.32) / 2], color="black")

        ax.set_xlim(-5, field_length + 5)
        ax.set_ylim(-5, field_width + 5)
        ax.set_aspect("equal", adjustable="box")
        return ax


    ###### passmap

def draw_pass_network(events_file_path, lineup_file_path, side):
        """
        홈팀 또는 원정팀의 선발 명단(Starting XI)에 대해 패스 네트워크를 시각화

        매개변수:
        - events_file_path (str): 경기 이벤트 데이터를 포함한 JSON 파일 경로
        - lineup_file_path (str): 라인업 데이터를 포함한 JSON 파일 경로
        - side (str): "home" 또는 "away"를 지정해 특정 팀 선택

        반환값:
        - None: 패스 네트워크 맵을 화면에 출력
        """

        # 데이터 로드
        with open(events_file_path, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        with open(lineup_file_path, 'r', encoding='utf-8') as f:
            lineup_data = json.load(f)

        # 팀과 선발 명단 확인
        if side == 'home':
            lineup_info = lineup_data[0]
        else:
            side == 'away'
            lineup_info = lineup_data[1]

        team_name = lineup_info["team_name"]

        starting_players = []
        for player in lineup_info['lineup']:
            if any(position["start_reason"] == "Starting XI" for position in player.get("positions", [])):
                starting_players.append(player['player_name'])

        # 선택된 팀과 선수의 패스 필터링
        team_passes = []
        for event in events_data:
            if event["type"]["name"] == "Pass" and event["team"]["name"] == team_name:
                team_passes.append(event)

        # 각 선수의 패스 위치 수집
        player_positions = defaultdict(list)
        pass_counter = Counter()
        for event in team_passes:
            passer = event["player"]["name"]
            recipient = event["pass"].get("recipient", {}).get("name")
            if passer in starting_players:
                player_positions[passer].append(event["location"])
            if recipient in starting_players:
                player_positions[recipient].append(event["pass"]["end_location"])
            if passer in starting_players and recipient in starting_players:
                pass_counter[(passer, recipient)] += 1

        # 선수별 평균 위치 계산
        average_positions = {}
        for player, positions in player_positions.items():
            tem1 = []
            for coord in zip(*positions):
                tem2 = sum(coord) / len(coord)
                tem1.append(tem2)
            average_positions[player] = tem1

        # 각 선수의 총 패스 수 계산 (보낸 패스 + 받은 패스)
        pass_counts = Counter()
        for (passer, recipient), count in pass_counter.items():
            pass_counts[passer] += count
            pass_counts[recipient] += count

        # 축구 필드와 패스 네트워크 그리기
        fig, ax = plt.subplots(figsize=(12, 8))
        ax = draw_soccer_field(ax, side)

        # 패스 연결선 그리기
        for (passer, recipient), count in pass_counter.items():
            if passer in average_positions and recipient in average_positions:
                start_x, start_y = average_positions[passer]
                end_x, end_y = average_positions[recipient]
                ax.plot(
                    [start_x, end_x], [start_y, end_y],
                    color="blue", linewidth=count / 2, alpha=0.7
                )

                # 선수 위치와 이름 표시
        for player, (x, y) in average_positions.items():
            node_size = pass_counts[player] * 5
            ax.scatter(x, y, c="red", s=node_size, edgecolor="black", zorder=5)
            ax.text(x, y + 2, player, fontsize=10, ha="center", zorder=6)

        # 최종 그래프 설정
        ax.legend()
        plt.title(f"{team_name} Pass Network (Starting XI)", fontsize=14)
        plt.axis("off")


    ##### shotmap

def draw_shot_map(events_file_path, lineup_file_path, side="home"):
        """
        홈팀 또는 원정팀의 슛 위치를 시각화
        슛을 득점, 유효 슛(막힘, 골대 맞음), 비유효 슛으로 구분

        매개변수:
        - events_file_path (str): 경기 이벤트 데이터를 포함한 JSON 파일 경로
        - side (str): "home" 또는 "away"를 지정해 특정 팀 선택

        반환값:
        - None: 슛 맵을 화면에 출력
        """

        # 데이터 로드
        with open(events_file_path, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        with open(lineup_file_path, 'r', encoding='utf-8') as f:
            lineup_data = json.load(f)

        # 팀과 선발 명단 확인
        if side == 'home':
            lineup_info = lineup_data[0]
        else:
            side == 'away'
            lineup_info = lineup_data[1]

        side_team = lineup_info["team_name"]

        team_shots = []
        for event in events_data:
            if event["type"]["name"] == "Shot" and event["team"]["name"] == side_team:
                team_shots.append(event)

        # 슛 위치, 결과, 카테고리 추출
        shot_locations = []
        shot_outcomes = []
        for shot in team_shots:
            shot_locations.append(shot['location'])
            shot_outcomes.append(shot['shot']['outcome']['name'])

        shot_categories = []  # 카테고리: "Goal", "On Target", "Off Target"
        for outcome in shot_outcomes:
            if outcome == "Goal":
                shot_categories.append("Goal")
            elif outcome in ["Saved", "Post", 'Saved Off Target', 'Saved to Post', 'Blocked']:
                shot_categories.append("On Target")
            else:
                shot_categories.append("Off Target")

        # 축구 필드 그리기
        fig, ax = plt.subplots(figsize=(12, 8))
        ax = draw_soccer_field(ax, side)

        # 슛 위치 표시
        for location, category in zip(shot_locations, shot_categories):
            x, y = location
            if category == "Goal":
                ax.scatter(x, y, c="green", s=100, label="Goal" if "Goal" not in ax.get_legend_handles_labels()[1] else "")
            elif category == "On Target":
                ax.scatter(x, y, c="blue", s=100,
                           label="On Target" if "On Target" not in ax.get_legend_handles_labels()[1] else "")
            else:
                ax.scatter(x, y, c="red", s=100,
                           label="Off Target" if "Off Target" not in ax.get_legend_handles_labels()[1] else "")

        # 범례와 제목 추가
        ax.legend()
        plt.title(f"{side_team} Shot Map", fontsize=14)
        plt.axis("off")


    ######## match table

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
                    "turnover_count": 0
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
                if outcome in ["Goal", "Saved", "Post", 'Saved Off Target', 'Saved to Post', 'Blocked']:
                    teams[team_name]["on_target"] += 1
            elif event_type == "Pass":
                teams[team_name]["passes"] += 1
                if "outcome" not in event.get("pass", {}):
                    teams[team_name]["pass_success"] += 1
                elif event['pass']['outcome']['name'] == 'Pass Offside':
                    teams[team_name]["offsides"] += 1
                elif event['pass'].get('type', {}).get('name', '') == 'Corner':
                    teams[team_name]["corners"] += 1
            if event_type in ["Foul Committed", "Bad Behaviour"]:
                teams[team_name]["fouls"] += 1
                card_type1 = event.get("foul_committed", {}).get("card", {}).get("name", "")
                card_type2 = event.get("bad_behaviour", {}).get("card", {}).get("name", "")
                if card_type1 == "Yellow Card" or card_type2 == "Yellow Card":
                    teams[team_name]["yellow_cards"] += 1
                elif card_type1 in ["Red Card", "Second Yellow"] or card_type2 in ["Red Card", "Second Yellow"]:
                    teams[team_name]["red_cards"] += 1

                    # 볼 점유율 계산
        possession_percentages = {
            team: (time / total_duration) * 100 for team, time in team_possession.items()
        }

        # 패스 성공률 계산
        for team in teams:
            teams[team]["pass_success_rate"] = round(
                (teams[team]["pass_success"] / teams[team]["passes"]) * 100, 2)

        return teams, list(team_names), possession_percentages


def create_match_table(match_data, team_names, possession_percentages):
        """
        주어진 경기 데이터를 표로 출력하는 함수
        """
        columns = ["Category", team_names[0], team_names[1]]
        rows = [
            ["Shots", match_data[team_names[0]]["shots"], match_data[team_names[1]]["shots"]],
            ["On Target", match_data[team_names[0]]["on_target"], match_data[team_names[1]]["on_target"]],
            ["Possession", f"{possession_percentages[team_names[0]]:.2f}%",
             f"{possession_percentages[team_names[1]]:.2f}%"],
            ["Passes", match_data[team_names[0]]["passes"], match_data[team_names[1]]["passes"]],
            ["Pass Accuracy", f"{match_data[team_names[0]]['pass_success_rate']}%",
             f"{match_data[team_names[1]]['pass_success_rate']}%"],
            ["Foul", match_data[team_names[0]]["fouls"], match_data[team_names[1]]["fouls"]],
            ["Yellow Card", match_data[team_names[0]]["yellow_cards"], match_data[team_names[1]]["yellow_cards"]],
            ["Red Card", match_data[team_names[0]]["red_cards"], match_data[team_names[1]]["red_cards"]],
            ["Offside", match_data[team_names[0]]["offsides"], match_data[team_names[1]]["offsides"]],
            ["Corners", match_data[team_names[0]]["corners"], match_data[team_names[1]]["corners"]],
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


    ####### most player

def extract_record_data(events_file_path):
        """
        JSON 데이터를 기반으로 선수별 데이터를 추출하는 함수

        매개변수:
        - events_file_path (str): JSON 파일 경로

        반환값:
        - None: 분야별 Most Player를 표로 출력

        """
        with open(events_file_path, 'r', encoding='utf-8') as f:
            events_data = json.load(f)

        record_count = Counter()

        # 이벤트 데이터를 순회하면서 'Shot', 'Dribble', 'Pass' 카운트
        for event in events_data:
            event_type = event.get('type', {}).get('name', None)
            player_name = event.get('player', {}).get('name', None)

            if event_type == 'Shot':
                record_count[(player_name, 'Shot')] += 1
            elif event_type == 'Dribble' and event.get('dribble', {}).get('outcome', {}).get('name', None) == 'Complete':
                record_count[(player_name, 'Dribble')] += 1
            elif event_type == 'Pass' and 'outcome' not in event.get('pass', {}):   # pass.outcome이 없을 때 -> 성공한 패스
                 record_count[(player_name, 'Pass')] += 1

        player_record = {}
        for (player, action), count in record_count.items():
            if player not in player_record:
                player_record[player] = {'Dribble': 0, 'Shot': 0, 'Pass': 0}
            player_record[player][action] = count

        player_name = []
        dribble_list = []
        shot_list = []
        pass_list = []

        for player, actions in player_record.items():
            player_name.append(player)
            dribble_list.append(actions['Dribble'])
            shot_list.append(actions['Shot'])
            pass_list.append(actions['Pass'])

        # DataFrame 생성
        my_df_dribble = pd.DataFrame({
            "Player": player_name,
            "Dribble": dribble_list,
        })
        max_dribbler = my_df_dribble.loc[my_df_dribble['Dribble'].idxmax()]

        my_df_shot = pd.DataFrame({
            "Player": player_name,
            "Shot": shot_list
        })
        max_shooter = my_df_shot.loc[my_df_shot['Shot'].idxmax()]

        my_df_pass = pd.DataFrame({
            "Player": player_name,
            "Pass": pass_list
        })
        max_passer = my_df_pass.loc[my_df_pass['Pass'].idxmax()]

        fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(8, 6))

        # 드리블 통계
        ax[0].axis("tight")
        ax[0].axis("off")
        table_data = [["Player", "Dribble"], [max_dribbler["Player"], max_dribbler["Dribble"]]]
        table = ax[0].table(cellText=table_data, cellLoc="center", loc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.auto_set_column_width(col=1)
        table.scale(1, 1.5)
        ax[0].set_title("Most Dribbler", fontsize=16, fontweight="bold")

        # 슛 통계
        ax[1].axis("tight")
        ax[1].axis("off")
        table_data = [["Player", "Shot"], [max_shooter["Player"], max_shooter["Shot"]]]
        table = ax[1].table(cellText=table_data, cellLoc="center", loc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.auto_set_column_width(col=1)
        table.scale(1, 1.5)
        ax[1].set_title("Most Shooter", fontsize=16, fontweight="bold")

        # 패스 통계
        ax[2].axis("tight")
        ax[2].axis("off")
        table_data = [["Player", "Pass"], [max_passer["Player"], max_passer["Pass"]]]
        table = ax[2].table(cellText=table_data, cellLoc="center", loc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.auto_set_column_width(col=1)
        table.scale(1, 1.5)
        ax[2].set_title("Most Passer", fontsize=16, fontweight="bold")

        plt.tight_layout()


    ####### event chain

    # '슛' 이벤트를 필터링하는 함수

def find_shot_events(events, team_name):
        shot_events_id = []
        shot_category = []
        for event in (events):
            if event['type']['name'] == 'Shot' and event['team']['name'] == team_name:
                # outcome 값을 'shot' 객체 내에서 추출
                outcome = event.get('shot', {}).get('outcome', {}).get('name')
                shot_events_id.append(event['id'])
                shot_category.append(outcome)

        return shot_events_id, shot_category


    # 직전 이벤트 추출 함수

def get_locations(events_file_path, shot_events_id, team_name):
        keypass_id_list = []
        shot_location = []
        for shot_id in shot_events_id:
            for event in events_file_path:
                if event['id'] == shot_id and 'key_pass_id' in event['shot']:
                    key_id = event['shot']['key_pass_id']
                    keypass_id_list.append(key_id)
                    location = event['location']
                    shot_location.append(location)

        pass_location = []
        pass_id_list = []
        for keypass_id in keypass_id_list:
            for event in events_file_path:
                if event['id'] == keypass_id and event['type']['name'] == 'Pass':
                    location = event['location']
                    pass_location.append(location)
                    pass_id_list.append(event['id'])

        pass_location_1 = []
        for pass_id in pass_id_list:
            tem = ''
            for event in events_file_path[::-1]:
                if event['id'] == pass_id:
                    tem = team_name
                    continue
                if event['type']['name'] == 'Pass' and event['team']['name'] == tem:
                    location = event['location']
                    pass_location_1.append(location)
                    break

        return shot_location, pass_location, pass_location_1


    # 이벤트 체인의 좌표를 화살표로 연결하고 시각화하는 함수
def draw_event_chain(events_file_path, lineup_file_path, side):
        fig, ax = plt.subplots(figsize=(12, 8))
        draw_soccer_field(ax, side)

        with open(lineup_file_path, 'r', encoding='utf-8') as f:
            lineup_data = json.load(f)
        with open(events_file_path, 'r', encoding='utf-8') as file:
            events = json.load(file)

        # 팀과 선발 명단 확인
        if side == 'home':
            lineup_info = lineup_data[0]
        else:
            side == 'away'
            lineup_info = lineup_data[1]

        team_name = lineup_info["team_name"]

        # '슛' 이벤트 중 결과가 골, 포스트, 세이브인 이벤트만 필터링
        shot_event_id, shot_category = find_shot_events(events, team_name)

        # 필터링된 '슛' 이벤트가 없는 경우
        if not shot_event_id:
            print("No shot events found.")
            return

        # 좌표데이터 추출
        shot_locations, pass_locations, pass_locations_1 = get_locations(events, shot_event_id, team_name)

        # 직전 이벤트들을 화살표로 연결
        for shot, _pass, _pass_1, category in zip(shot_locations, pass_locations, pass_locations_1, shot_category):
            if category in ["Goal", "Saved", "Post", 'Saved Off Target', 'Saved to Post', 'Blocked']:
                color = 'red'
                category = 'On Target'

                # 화살표 그리기
                ax.annotate('', xy=(shot[0], shot[1]),
                            xytext=(_pass[0], _pass[1]),
                            arrowprops=dict(arrowstyle="->", color=color, lw=2))

                if _pass[0] >= 60 and _pass_1[0] >= 60:
                    ax.annotate('', xy=(_pass[0], _pass[1]),
                                xytext=(_pass_1[0], _pass_1[1]),
                                arrowprops=dict(arrowstyle="->", color=color, lw=2))

            else:
                color = 'gray'
                category = 'Off Target'

                # 화살표 그리기
                ax.annotate('', xy=(shot[0], shot[1]),
                            xytext=(_pass[0], _pass[1]),
                            arrowprops=dict(arrowstyle="->", color=color, lw=2, alpha=0.4))

                if _pass[0] >= 60 and _pass_1[0] >= 60:
                    ax.annotate('', xy=(_pass[0], _pass[1]),
                                xytext=(_pass_1[0], _pass_1[1]),
                                arrowprops=dict(arrowstyle="->", color=color, lw=2, alpha=0.4))

            # 각 이벤트의 점
            ax.scatter(shot[0], shot[1], color=color, s=1,
                       label=category if category not in ax.get_legend_handles_labels()[1] else "")

            # 자연수 표시 (번호는 순차적으로 부여)
            event_number_1 = 1
            event_number_2 = 2
            event_number_3 = 3
            ax.text(shot[0], shot[1], f"{event_number_1}", color='black', fontsize=10, ha='center', va='center', alpha=0.6)
            ax.text(_pass[0], _pass[1], f"{event_number_2}", color='black', fontsize=10, ha='center', va='center',
                    alpha=0.6)
            if _pass[0] >= 60 and _pass_1[0] >= 60:
                ax.text(_pass_1[0], _pass_1[1], f"{event_number_3}", color='black', fontsize=10, ha='center', va='center',
                        alpha=0.6)

        plt.title(f"Event Chain for {team_name}")
        plt.axis('off')
        plt.legend(loc='upper right')


    ## 실행

if __name__ == '__main__':
        events_file_path = "/Users/kyuhyeon/Documents/data/events/3773457.json"
        lineup_file_path = "/Users/kyuhyeon/Documents/data/lineups/3773457.json"

        ##passmap
        draw_pass_network(events_file_path, lineup_file_path, side = "home")
        draw_pass_network(events_file_path, lineup_file_path, side = "away")

        ##shotmap
        draw_shot_map(events_file_path, lineup_file_path, side = "home")
        draw_shot_map(events_file_path, lineup_file_path, side = "away")

        ## match table
        match_data, team_names, possession_percentages = extract_match_data(events_file_path)
        create_match_table(match_data, team_names, possession_percentages)

        ## most player
        extract_record_data(events_file_path)

        ## event chain
        draw_event_chain(events_file_path, lineup_file_path, 'home')
        draw_event_chain(events_file_path,lineup_file_path, 'away')

        plt.tight_layout()
        plt.show()