import json 

events_file_path = "C:/Users/user/local/GitHub/open-data/data/events/3773457.json"
with open(events_file_path, 'r', encoding='utf-8') as f:
    events_data = json.load(f)

print(type(events_data))
print(type(events_data[0]))
print(type(events_data[0]["type"]))
print(type(events_data[0]["type"]["name"]))

for event in events_data:

print(type(event))