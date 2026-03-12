# tools/update_dataset.py

import requests
import os

os.makedirs('./backend/data', exist_ok=True)

DATASETS = [
    {
        'name': 'ipsum',
        'url': 'https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt',
        'path': './backend/data/ipsum.txt'
    },
    {
        'name': 'Emerging Threats',
        'url': 'https://rules.emergingthreats.net/blockrules/compromised-ips.txt',
        'path': './backend/data/emerging_threats.txt'
    },
    {
        'name': 'Firehol Level 1',
        'url': 'https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset',
        'path': './backend/data/firehol.txt'
    }
]

def update_all():
    print("Updating all threat intelligence datasets...\n")

    for dataset in DATASETS:
        print(f"Downloading {dataset['name']}...")
        try:
            r = requests.get(dataset['url'], timeout=15)
            with open(dataset['path'], 'w') as f:
                f.write(r.text)

            lines = [l for l in r.text.split('\n')
                     if l and not l.startswith('#')]
            print(f"✅ {dataset['name']}: {len(lines)} entries\n")

        except Exception as e:
            print(f"❌ {dataset['name']} failed: {e}\n")

    print("All datasets updated!")

if __name__ == "__main__":
    update_all()