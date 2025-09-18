import matplotlib.pyplot as plt
import json

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
def get_locations(events_file_path, shot_events_id,team_name):

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


# 축구 필드 그리기 함수
def draw_soccer_field(ax, side, field_dimen=(120, 80)):
    """
    축구 필드를 그리는 함수
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
    shot_locations, pass_locations, pass_locations_1  = get_locations(events, shot_event_id,team_name)
    
    # 직전 이벤트들을 화살표로 연결
    for shot, _pass, _pass_1, category in zip(shot_locations, pass_locations, pass_locations_1, shot_category):
        if category in ["Goal", "Saved", "Post",'Saved Off Target', 'Saved to Post','Blocked']:
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
                    arrowprops=dict(arrowstyle="->", color=color, lw=2,alpha = 0.4))
                
            if _pass[0] >= 60 and _pass_1[0] >= 60:
                ax.annotate('', xy=(_pass[0], _pass[1]),
                            xytext=(_pass_1[0], _pass_1[1]),
                            arrowprops=dict(arrowstyle="->", color=color, lw=2,alpha = 0.4))
        
        # 각 이벤트의 점
        ax.scatter(shot[0], shot[1], color=color, s=1,label=category if category not in ax.get_legend_handles_labels()[1] else "")
        

        # 자연수 표시 (번호는 순차적으로 부여)
        event_number_1 = 1
        event_number_2 = 2
        event_number_3 = 3
        ax.text(shot[0], shot[1], f"{event_number_1}", color='black', fontsize=10, ha='center', va='center',alpha= 0.6)
        ax.text(_pass[0], _pass[1], f"{event_number_2}", color='black', fontsize=10, ha='center', va='center', alpha= 0.6)
        if _pass[0] >= 60 and _pass_1[0] >= 60:
            ax.text(_pass_1[0], _pass_1[1], f"{event_number_3}", color='black', fontsize=10, ha='center', va='center', alpha= 0.6)
     
    
    plt.title(f"Event Chain for {team_name}")
    plt.axis('off')
    plt.legend(loc='upper right')
    plt.show()

# 이벤트 파일 경로 입력
events_file_path = "C:/Users/user/local/GitHub/open-data/data/events/3773457.json"
lineup_file_path = "C:/Users/user/local/GitHub/open-data/data/lineups/3773457.json"
# 함수 호출
draw_event_chain(events_file_path,lineup_file_path, 'home')
draw_event_chain(events_file_path,lineup_file_path, 'away')
