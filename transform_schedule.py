import json
import requests
from datetime import datetime, timedelta
import os
import git

def transform_json(input_url, output_file):
    response = requests.get(input_url)
    response.raise_for_status()
    data = response.json()
    transformed_data = []

    for i in range(len(data["round_number"])):
        event = {
            "name": data["event_name"][str(i)],
            "countryName": data["country"][str(i)].replace(" ", ""),
            "countryKey": None,
            "roundNumber": data["round_number"][str(i)],
            "start": None,
            "end": None,
            "gmt_offset": data["gmt_offset"][str(i)],
            "sessions": [],
            "over": False
        }

        # Parse GMT offset to convert local time to UTC
        # The offset represents how much ahead/behind UTC the local time is
        # To convert local time to UTC, we subtract the offset
        gmt_offset_str = data["gmt_offset"][str(i)]
        sign = 1 if gmt_offset_str[0] == '+' else -1
        hours, minutes = map(int, gmt_offset_str[1:].split(':'))
        offset = timedelta(hours=sign * hours, minutes=sign * minutes)

        for j in range(1, 6):
            session_name = data[f'session{j}'][str(i)]
            session_date = data[f'session{j}_date'][str(i)]

            if session_name:
                # Convert local time to UTC by subtracting the offset
                session_start_dt = datetime.fromisoformat(session_date)
                session_start_utc = session_start_dt - offset
                session_end_utc = session_start_utc + timedelta(hours=1)

                event["sessions"].append({
                    "sessionNumber": str(j),
                    "kind": session_name,
                    "start": session_start_utc.isoformat() + 'Z',
                    "end": session_end_utc.isoformat() + 'Z'
                })
        if event["sessions"]:
            event["start"] = min(session["start"] for session in event["sessions"])
            event["end"] = max(session["end"] for session in event["sessions"])
            transformed_data.append(event)

    with open(output_file, 'w') as f:
        json.dump(transformed_data, f, indent=4)

    repo = git.Repo(os.getcwd())
    repo.git.add(output_file)
    repo.index.commit(f'Update {output_file} with transformed data')
    origin = repo.remote(name='origin')
    origin.push()


current_year = datetime.now().year

repo = git.Repo(os.getcwd())
origin = repo.remote(name='origin')

# ✅ 1) Sync repo FIRST
repo.git.pull('--rebase')

current_year = datetime.now().year

for year in range(2018, current_year + 1):
    input_url = f'https://raw.githubusercontent.com/theOehrly/f1schedule/refs/heads/master/schedule_{year}.json'
    output_file = f'{year}.json'
    response = requests.get(input_url)
    if response.status_code == 200:
        transform_json(input_url, output_file)
    else:
        print(f"{year} not available")

# ✅ 2) Commit once
repo.git.add(A=True)

if repo.is_dirty():
    repo.index.commit("Update F1 schedules")
    origin.push()
else:
    print("No changes to commit")


