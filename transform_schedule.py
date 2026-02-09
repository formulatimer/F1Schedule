import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import git
from git.exc import GitCommandError

# Constants
START_YEAR = 2018
MAX_SESSIONS = 5
SESSION_DURATION_HOURS = 1
F1_SCHEDULE_BASE_URL = 'https://raw.githubusercontent.com/theOehrly/f1schedule/refs/heads/master/schedule_{year}.json'


def parse_gmt_offset(gmt_offset_str: str) -> timedelta:
    """
    Parse GMT offset string (e.g., '+02:00', '-05:30') to timedelta.
    
    Args:
        gmt_offset_str: GMT offset string with sign and time
        
    Returns:
        timedelta object representing the offset
    """
    sign = 1 if gmt_offset_str[0] == '+' else -1
    hours, minutes = map(int, gmt_offset_str[1:].split(':'))
    return timedelta(hours=sign * hours, minutes=sign * minutes)


def convert_to_utc(local_time: str, gmt_offset: timedelta) -> str:
    """Convert local time to UTC ISO format string."""
    local_dt = datetime.fromisoformat(local_time)
    utc_dt = local_dt - gmt_offset
    return utc_dt.isoformat() + 'Z'


def transform_schedule_data(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transform F1 schedule data from raw format to standardized format.
    
    Args:
        raw_data: Raw JSON data from F1 schedule source
        
    Returns:
        List of transformed event dictionaries
    """
    transformed_data = []
    round_count = len(raw_data.get("round_number", {}))
    
    for i in range(round_count):
        str_i = str(i)
        gmt_offset = parse_gmt_offset(raw_data["gmt_offset"][str_i])
        
        event = {
            "name": raw_data["event_name"][str_i],
            "countryName": raw_data["country"][str_i].replace(" ", ""),
            "countryKey": None,
            "roundNumber": raw_data["round_number"][str_i],
            "start": None,
            "end": None,
            "gmt_offset": raw_data["gmt_offset"][str_i],
            "sessions": [],
            "over": False
        }
        
        # Process all sessions
        for session_num in range(1, MAX_SESSIONS + 1):
            session_name = raw_data.get(f'session{session_num}', {}).get(str_i)
            session_date = raw_data.get(f'session{session_num}_date', {}).get(str_i)
            
            if session_name:
                session_start_utc = convert_to_utc(session_date, gmt_offset)
                session_end_dt = datetime.fromisoformat(session_date) - gmt_offset
                session_end_utc = (session_end_dt + timedelta(hours=SESSION_DURATION_HOURS)).isoformat() + 'Z'
                
                event["sessions"].append({
                    "sessionNumber": str(session_num),
                    "kind": session_name,
                    "start": session_start_utc,
                    "end": session_end_utc
                })
        
        # Only add events with sessions
        if event["sessions"]:
            event["start"] = min(s["start"] for s in event["sessions"])
            event["end"] = max(s["end"] for s in event["sessions"])
            transformed_data.append(event)
    
    return transformed_data


def fetch_and_transform(input_url: str, output_file: str) -> bool:
    """
    Fetch schedule data and transform it to output file.
    
    Args:
        input_url: URL to fetch JSON data from
        output_file: Path to write transformed JSON
        
    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.get(input_url, timeout=10)
        response.raise_for_status()
        
        raw_data = response.json()
        transformed_data = transform_schedule_data(raw_data)
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(transformed_data, f, indent=4)
        return True
        
    except requests.exceptions.RequestException:
        return False
    except (json.JSONDecodeError, KeyError):
        return False


def sync_git_repo(repo: git.Repo) -> None:
    """Reset and pull latest changes from remote."""
    try:
        repo.git.reset('--hard')
        repo.git.clean('-fd')
        repo.git.pull('--rebase')
    except GitCommandError as e:
        raise


def commit_and_push(repo: git.Repo, message: str) -> bool:
    """Commit changes and push to remote."""
    try:
        if repo.is_dirty():
            repo.git.add(A=True)
            repo.index.commit(message)
            repo.remote(name='origin').push()
            return True
        else:
            return False
    except GitCommandError:
        return False


def main():
    """Main function to download and update F1 schedules."""
    current_year = datetime.now().year
    repo = git.Repo('.')
    
    # Sync repository first
    sync_git_repo(repo)
    
    # Download and transform schedules
    for year in range(START_YEAR, current_year + 1):
        url = F1_SCHEDULE_BASE_URL.format(year=year)
        output_file = f'{year}.json'
        fetch_and_transform(url, output_file)
    
    # Commit all changes at once
    commit_and_push(repo, "Update F1 schedules")


if __name__ == "__main__":
    main()



