import json
import matplotlib.pyplot as plt

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
    # 홈/어웨이 진영 배경색 표시
    if side == 'home':
        ax.add_patch(plt.Rectangle((0, 0), field_length / 2, field_width, color="lightblue", alpha=0.2, label="Home Side"))
        ax.add_patch(plt.Rectangle((field_length / 2, 0), field_length / 2, field_width, color="lightcoral", alpha=0.2, label="Away Side"))
    elif side == 'away':
        ax.add_patch(plt.Rectangle((field_length / 2, 0), field_length / 2, field_width, color="lightblue", alpha=0.2, label="Home Side"))
        ax.add_patch(plt.Rectangle((0, 0), field_length / 2, field_width, color="lightcoral", alpha=0.2, label="Away Side"))

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

    team_shots =[]
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
        elif outcome in ["Saved", "Post"]:
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
            ax.scatter(x, y, c="blue", s=100, label="On Target" if "On Target" not in ax.get_legend_handles_labels()[1] else "")
        else:
            ax.scatter(x, y, c="red", s=100, label="Off Target" if "Off Target" not in ax.get_legend_handles_labels()[1] else "")
    
    # 범례와 제목 추가
    ax.legend()
    plt.title(f"{side_team} Shot Map", fontsize=14)
    plt.axis("off")
    plt.show()

draw_shot_map("C:/Users/user/local/GitHub/open-data/data/events/3773457.json",
              "C:/Users/user/local/GitHub/open-data/data/lineups/3773457.json",
              "home")

draw_shot_map("C:/Users/user/local/GitHub/open-data/data/events/3773457.json",
              "C:/Users/user/local/GitHub/open-data/data/lineups/3773457.json",
              "away")
