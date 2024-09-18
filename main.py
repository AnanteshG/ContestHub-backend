import json
import uuid

from bs4 import BeautifulSoup

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
    response = requests.get(URL, json={"query": body})
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


def fetch_hackerearth_contests():
    contests = []

    url = "https://www.hackerearth.com/challenges/competitive"

    try:
        challenges_response = requests.get(url, timeout=10)  # Add a timeout of 10 seconds
        challenges_response.raise_for_status()  # Raise an error if the request failed
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from HackerEarth: {e}")
        return contests

    # If request is successful, proceed with parsing
    challenges_soup = BeautifulSoup(challenges_response.text, "html.parser")
    challenges = challenges_soup.select('div.upcoming > div.challenge-card-modern')

    for challenge in challenges:
        try:
            title_span = challenge.find('span', class_='challenge-list-title')
            if not title_span:
                continue

            title = ' '.join(title_span.text.split())  # Clean the title

            url_tag = challenge.find('a', class_='challenge-card-wrapper')
            if not url_tag or 'href' not in url_tag.attrs:
                continue

            contest_url = url_tag['href']
            event_slug = contest_url.strip('/').split('/')[-1]
            contest_url = f"https://www.hackerearth.com{contest_url}"

            # Get contest details for start and end times
            contest_details_url = f'https://www.hackerearth.com/challengesapp/api/events/{event_slug}/?only_meta=false'

            try:
                contest_details_response = requests.get(contest_details_url, timeout=10)
                contest_details_response.raise_for_status()
                contest_details = contest_details_response.json()

                # Parse start and end date
                start_date = datetime.fromisoformat(contest_details.get('start_date')[:-1])
                end_date = datetime.fromisoformat(contest_details.get('end_date')[:-1])
                duration = end_date - start_date

                # Add contest to list
                contests.append({
                    "id": uuid.uuid4().hex,
                    "platform": "HackerEarth",
                    "title": title,
                    "url": contest_url,
                    "start_time": start_date.isoformat(),
                    "duration": duration.seconds + duration.days * SECONDS_PER_DAY,
                })

            except requests.exceptions.RequestException as e:
                print(f"Error fetching contest details for {title}: {e}")
                continue

        except Exception as e:
            print(f"Error processing challenge: {e}")
            continue

    return contests


def fetch_atcoder_contests() -> list[dict]:
    contests = []

    url = "https://atcoder.jp/contests/"

    try:
        response = requests.get(url, timeout=10)  # Add a timeout of 10 seconds
        response.raise_for_status()  # Raise an error if the request failed
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from HackerEarth: {e}")
        return contests

    soup = BeautifulSoup(response.text, "html.parser")
    contest_rows = soup.select('#contest-table-upcoming tbody tr')

    for row in contest_rows:
        try:
            start_time = row.select_one('td a time').text.strip()  # example: 2024-09-21 21:00:00+0900
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S%z')

            contest_info = row.select_one('td:nth-of-type(2) a')
            title = contest_info.text.strip()
            contest_url = f'https://atcoder.jp{contest_info["href"]}'

            duration = row.select_one('td:nth-of-type(3)').text.strip().split(':')  # example: 120:00
            duration = int(duration[0]) * 60 + int(duration[1])  # convert to minutes

            contests.append({
                "id": uuid.uuid4().hex,
                "platform": "AtCoder",
                "title": title,
                "url": contest_url,
                "start_time": start_time.isoformat(),
                "duration": duration*60,
            })

        except Exception as e:
            continue

    return contests


contests = (
    fetch_codechef_contests() +
    fetch_codeforces_contests() +
    fetch_geeksforgeeks_contests() +
    fetch_leetcode_contests() +
    fetch_hackerearth_contests() +
    fetch_atcoder_contests()
)

with (Path(__file__).parent / "contests").open("w") as f:
    json.dump(contests, f)

with (Path(__file__).parent / "contests.json").open("w") as f:
    json.dump(contests, f, indent=4)


def format_date(date: datetime) -> str:
    day = date.day
    month = date.strftime("%b")
    year = date.year
    suffix = 'th'
    if day % 10 == 1 and day != 11:
        suffix = 'st'
    elif day % 10 == 2 and day != 12:
        suffix = 'nd'
    elif day % 10 == 3 and day != 13:
        suffix = 'rd'
    return f"{day}{suffix} {month} {year}"


readme_path = Path(__file__).parent / "README.md"
current_datetime = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
formatted_date = format_date(current_datetime)
date_time_str = f"{formatted_date} {current_datetime.strftime('%H:%M:%S %Z')}"

with readme_path.open("r") as file:
    lines = file.readlines()

# Update or add the line with the last update information
updated = False
for i, line in enumerate(lines):
    if line.startswith("Last updated:"):
        lines[i] = f"Last updated: {date_time_str}\n"
        updated = True
        break

if not updated:
    lines.append(f"Last updated: {date_time_str}\n")

with readme_path.open("w") as file:
    file.writelines(lines)
