import json
from datetime import datetime, timedelta
from collections import defaultdict
import os

FISCAL_YEAR = 2024
CHECK_DATE_STR = "2023-10-01" 
TRAININGS = ["Electrical Safety for Labs", "X-Ray Safety", "Laboratory Safety Training"]

INPUT_FILE = "content/trainings.txt"
OUTPUT_DIR = "content/output"
OUTPUT_FILE_1 = os.path.join(OUTPUT_DIR, "training_completion_counts.json")
OUTPUT_FILE_2 = os.path.join(OUTPUT_DIR, "fiscal_year_completions.json")
OUTPUT_FILE_3 = os.path.join(OUTPUT_DIR, "expired_or_expiring_trainings.json")

def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def get_most_recent_completions(data):

    recent_completions = {}
    for person in data:
        for training in person['completions']:
            if 'timestamp' not in training:
                print(f"Skipping training {training['name']} for {person['name']} due to missing timestamp")
                continue
            
            key = (person['name'], training['name'])
            try:
                completion_date = datetime.strptime(training['timestamp'], '%m/%d/%Y')
            except ValueError:
                print(f"Skipping training {training['name']} for {person['name']} due to invalid date format")
                continue

            if key not in recent_completions or completion_date > datetime.strptime(recent_completions[key]['completion_date'], '%m/%d/%Y'):
                recent_completions[key] = {
                    "name": person['name'],
                    "training_name": training['name'],
                    "completion_date": training['timestamp'],
                    "expires": training['expires']
                }
    return recent_completions


def task_1_completion_counts(recent_completions):

    counts = defaultdict(int)
    for record in recent_completions.values():
        counts[record['training_name']] += 1
    return dict(counts)

def task_2_fiscal_year_completions(recent_completions, fiscal_year):

    start_date = datetime(fiscal_year - 1, 7, 1)
    end_date = datetime(fiscal_year, 6, 30)
    results = defaultdict(list)
    
    for record in recent_completions.values():
        completion_date = datetime.strptime(record['completion_date'], '%m/%d/%Y')
        if record['training_name'] in TRAININGS and start_date <= completion_date <= end_date:
            results[record['training_name']].append(record['name'])
    return dict(results)

def task_3_expired_or_expiring_trainings(recent_completions, check_date_str):

    check_date = datetime.strptime(check_date_str, "%Y-%m-%d")
    one_month = timedelta(days=30)
    soon_date = check_date + one_month
    results = defaultdict(list)

    for record in recent_completions.values():
        if record['expires']:
            expiration_date = datetime.strptime(record['expires'], '%m/%d/%Y')
            if expiration_date < check_date:
                status = "expired"
            elif check_date <= expiration_date <= soon_date:
                status = "expires soon"
            else:
                continue
            results[record['name']].append({
                "training_name": record['training_name'],
                "completion_date": record['completion_date'],
                "expires": record['expires'],
                "status": status
            })
    return dict(results)

def save_json(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    data = load_data(INPUT_FILE)
    recent_completions = get_most_recent_completions(data)

    completion_counts = task_1_completion_counts(recent_completions)
    save_json(completion_counts, OUTPUT_FILE_1)

    fiscal_year_completions = task_2_fiscal_year_completions(recent_completions, FISCAL_YEAR)
    save_json(fiscal_year_completions, OUTPUT_FILE_2)

    expired_or_expiring = task_3_expired_or_expiring_trainings(recent_completions, CHECK_DATE_STR)
    save_json(expired_or_expiring, OUTPUT_FILE_3)

if __name__ == "__main__":
    main()
