import json
import csv
import os

IN_FILE = 'wave1_sending_results.json'
OUT_DIR = 'logs'
OUT_FILE = os.path.join(OUT_DIR, 'wave1_sending_results.csv')

os.makedirs(OUT_DIR, exist_ok=True)

with open(IN_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

rows = []
for r in data.get('results', []):
    rows.append({
        'index': r.get('index'),
        'name': r.get('name'),
        'company': r.get('company'),
        'email': r.get('email'),
        'status': r.get('status'),
        'erro': r.get('erro', ''),
        'timestamp': r.get('timestamp')
    })

with open(OUT_FILE, 'w', newline='', encoding='utf-8') as csvf:
    writer = csv.DictWriter(csvf, fieldnames=['index','name','company','email','status','erro','timestamp'])
    writer.writeheader()
    writer.writerows(rows)

print('Export complete:', OUT_FILE)
