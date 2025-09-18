import json
import pandas as pd

# JSON 파일 경로
file_path = 'C:/Users/user/local/GitHub/open-data/data/events/3773457.json'
with open(file_path, 'r', encoding='utf-8-sig') as file:
    data = json.load(file)

# JSON 데이터를 행렬 형태로 변환하는 함수
def flatten_json(json_obj, prefix=''):
    """JSON 객체를 플랫하게 변환"""
    flat_dict = {}
    for key, value in json_obj.items():
        if isinstance(value, dict):  # 값이 딕셔너리인 경우 재귀적으로 호출
            flat_dict.update(flatten_json(value, prefix=prefix + key + '.'))
        elif isinstance(value, list):  # 값이 리스트인 경우
            if value and isinstance(value[0], dict):  # 리스트의 요소가 딕셔너리일 경우
                for i, item in enumerate(value):
                    flat_dict.update(flatten_json(item, prefix=f"{prefix}{key}[{i}]."))
            else:
                flat_dict[prefix + key] = value
        else:
            flat_dict[prefix + key] = value
    return flat_dict

# 각 이벤트를 플랫 데이터로 변환
rows = [flatten_json(event) for event in data]

# DataFrame 생성
df = pd.DataFrame(rows)

# CSV 파일로 저장
csv_file_path = 'C:/CODING/R/R_TeamProject/3773457event_data/3773457events_data.csv'
df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')  # 'utf-8-sig'로 저장

print(f"The CSV file has been saved: {csv_file_path}")

