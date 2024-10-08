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
            "countryName": data["country"][str(i)],
            "countryKey": None,
            "roundNumber": data["round_number"][str(i)],
            "start": None,
            "end": None,
            "gmt_offset": data["gmt_offset"][str(i)],
            "sessions": [],
            "over": False
        }

        for j in range(1, 6):
            session_name = data[f'session{j}'][str(i)]
            session_date = data[f'session{j}_date'][str(i)]

            if session_name:
                session_start = session_date
                session_start_dt = datetime.fromisoformat(session_start)
                session_end_dt = session_start_dt + timedelta(hours=1)

                event["sessions"].append({
                    "sessionNumber": str(j),
                    "kind": session_name,
                    "start": session_start + 'Z',
                    "end": session_end_dt.isoformat() + 'Z'
                })

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

input_url = 'https://raw.githubusercontent.com/theOehrly/f1schedule/refs/heads/master/schedule_2020.json'
output_file = '2020.json'
transform_json(input_url, output_file)
