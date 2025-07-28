# Multi-Source Anomaly Metadata Extraction for Industrial Control Systems

## Repo Setup
```
python3.12 -m venv venv/
source venv/bin/activate
pip install -r requirements.txt
pre-commit install
cp .env.development .env
```

## Attack Techniques
```shell
cd attack-techniques/
python extract_attack_technique.py
```

## Equipment List
```shell
cd equipment-list/
python extract_equipment_list.py 9a083ae4-3fae-4619-91e8-6a3d13513372
```
