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
    event_id = [event['id'] for event in events_data if event.get('team',{}).get('name') != team_name]
    
    # 위치 데이터 추출
    failed_passes_location = []
    lost_duels_location = []
    dribble_losts_location = []
    for event in events_data:
        
        related_event_list = event.get('related_events',[])
        
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
    

    
    return failed_passes_location, lost_duels_location, dribble_losts_location, team_name, side

events_file_path = "C:/Users/user/local/GitHub/open-data/data/events/3773457.json"

if __name__ == '__main__':
    # 축구 필드 그리기
    fig, ax = plt.subplots(figsize=(12, 8))

    failed_passes_location, lost_duels_location, dribble_losts_location, team_name, side = extract_turnover_data(events_file_path,"home")
    ax = draw_soccer_field(ax, side)

    # 턴오버 이벤트 위치와 카테고리
    turnover_locations = failed_passes_location + lost_duels_location + dribble_losts_location
    turnover_categories = (
        ["Failed Pass"] * len(failed_passes_location) +
        ["Lost Duel"] * len(lost_duels_location) +
        ["Dribble Lost"] * len(dribble_losts_location)
    )


    # 턴오버 이벤트 시각화
    for location, category in zip(turnover_locations, turnover_categories):
        x, y = location
        if category == "Failed Pass":
            ax.scatter(x, y, c="red", s=100, label="Failed Pass" if "Failed Pass" not in ax.get_legend_handles_labels()[1] else "")
        elif category == "Lost Duel":
            ax.scatter(x, y, c="orange", s=100, label="Lost Duel" if "Lost Duel" not in ax.get_legend_handles_labels()[1] else "")
        elif category == "Dribble Lost":
            ax.scatter(x, y, c="purple", s=100, label="Dribble Lost" if "Dribble Lost" not in ax.get_legend_handles_labels()[1] else "")
        # 범례와 제목 추가
    ax.legend(loc = 'upper right')
    plt.title(f"{team_name} Turnover Map", fontsize=14)
    plt.axis("off")
    plt.show()

if __name__ == '__main__':
    # 축구 필드 그리기
    fig, ax = plt.subplots(figsize=(12, 8))

    failed_passes_location, lost_duels_location, dribble_losts_location, team_name, side = extract_turnover_data("./data/events/15946.json","away")
    ax = draw_soccer_field(ax, side)

    # 턴오버 이벤트 위치와 카테고리
    turnover_locations = failed_passes_location + lost_duels_location + dribble_losts_location
    turnover_categories = (
        ["Failed Pass"] * len(failed_passes_location) +
        ["Lost Duel"] * len(lost_duels_location) +
        ["Dribble Lost"] * len(dribble_losts_location)
    )


    # 턴오버 이벤트 시각화
    for location, category in zip(turnover_locations, turnover_categories):
        x, y = location
        if category == "Failed Pass":
            ax.scatter(x, y, c="red", s=100, label="Failed Pass" if "Failed Pass" not in ax.get_legend_handles_labels()[1] else "")
        elif category == "Lost Duel":
            ax.scatter(x, y, c="orange", s=100, label="Lost Duel" if "Lost Duel" not in ax.get_legend_handles_labels()[1] else "")
        elif category == "Dribble Lost":
            ax.scatter(x, y, c="purple", s=100, label="Dribble Lost" if "Dribble Lost" not in ax.get_legend_handles_labels()[1] else "")
        # 범례와 제목 추가
    ax.legend(loc = 'upper right')
    plt.title(f"{team_name} Turnover Map", fontsize=14)
    plt.axis("off")
    plt.show()