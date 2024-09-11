import json
import uuid

from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

SECONDS_PER_DAY = 24 * 60 * 60

def fetch_codechef_contests() -> list[dict]:
    URL = "https://www.codechef.com/api/list/contests/all"
    payload = {
        "sort_by": "START",
        "sorting_order": "asc",
    }
    contests = []
    response = requests.get(URL, params=payload)
    if response.ok:
        response = response.json()
        contests_data = response["present_contests"] + response["future_contests"]
        for data in contests_data:
            try:
                title = data["contest_name"]
                url   = f"https://www.codechef.com/{data['contest_code']}"
                start_time = datetime.fromisoformat(data["contest_start_date_iso"])
                end_time   = datetime.fromisoformat(data["contest_end_date_iso"])
                duration   = end_time - start_time
            except:
                continue
            contests.append({                
                "id": uuid.uuid4().hex,
                "platform": "CodeChef",
                "title": title,
                "url": url,
                "start_time": start_time.isoformat(),
                "duration": duration.seconds + duration.days * SECONDS_PER_DAY
            })
    return contests

def fetch_codeforces_contests() -> list[dict]:
    URL = "https://codeforces.com/api/contest.list"
    contests = []
    response = requests.get(URL)
    if response.ok:
        response = response.json()
        contests_data = response["result"]
        for data in contests_data:
            title = data["name"]
            url   = f"https://codeforces.com/contests/{data['id']}"
            start_time = datetime.fromtimestamp(float(data["startTimeSeconds"]), tz=ZoneInfo("Asia/Kolkata"))
            end_time   = start_time + timedelta(seconds=float(data["durationSeconds"]))
            if end_time <= datetime.now(tz=ZoneInfo("Asia/Kolkata")): 
                continue  # include ongoing and upcoming contests only
            duration   = end_time - start_time
            contests.append({                
                "id": uuid.uuid4().hex,
                "platform": "Codeforces",
                "title": title,
                "url": url,
                "start_time": start_time.isoformat(),
                "duration": duration.seconds + duration.days * SECONDS_PER_DAY
            })
    return contests

def fetch_geeksforgeeks_contests() -> list[dict]:
    URL = "https://practiceapi.geeksforgeeks.org/api/vr/events/"
    payload = {
        "type": "contest",
        "sub_type": "upcoming"
    }
    contests = []
    response = requests.get(URL, params=payload)
    if response.ok:
        response = response.json()
        contests_data = response["results"]["upcoming"]
        for data in contests_data:
            title = data["name"]
            url   = f"https://practice.geeksforgeeks.org/contest/{data['slug']}"
            start_time = datetime.fromisoformat(data["start_time"]).astimezone(ZoneInfo("Asia/Kolkata"))
            end_time   = datetime.fromisoformat(data["end_time"]).astimezone(ZoneInfo("Asia/Kolkata"))
            duration   = end_time - start_time
            contests.append({                
                "id": uuid.uuid4().hex,
                "platform": "GeeksforGeeks",
                "title": title,
                "url": url,
                "start_time": start_time.isoformat(),
                "duration": duration.seconds + duration.days * SECONDS_PER_DAY
            })
    return contests

def fetch_leetcode_contests() -> list[dict]:
    URL  = "https://leetcode.com/graphql"
    body = """
    {
        allContests {
            title
            titleSlug
            startTime
            duration
        }
    }
    """
    contests = []
    response = requests.get(URL, json={"query" : body})
    if response.ok:
        response = response.json()
        contests_data = response["data"]["allContests"]
        for data in contests_data:
            title = data["title"]
            url   = f"https://leetcode.com/contest/{data['titleSlug']}"
            start_time = datetime.fromtimestamp(int(data["startTime"])).astimezone(ZoneInfo("Asia/Kolkata"))
            end_time = start_time + timedelta(seconds=int(data["duration"]))
            if end_time <= datetime.now(tz=ZoneInfo("Asia/Kolkata")): 
                continue
            duration = end_time - start_time
            contests.append({                
                "id": uuid.uuid4().hex,
                "platform": "LeetCode",
                "title": title,
                "url": url,
                "start_time": start_time.isoformat(),
                "duration": duration.seconds + duration.days * SECONDS_PER_DAY
            })
    return contests

contests = ( 
    fetch_codechef_contests() +
    fetch_codeforces_contests() +
    fetch_geeksforgeeks_contests() +
    fetch_leetcode_contests()
)

with (Path(__file__).parent / "contests").open("w") as f:
    json.dump(contests, f)

with (Path(__file__).parent / "contests.json").open("w") as f:
    json.dump(contests, f, indent=4)
