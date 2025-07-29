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

## PID Diagrams
```shell
cd pid-diagrams/
python extract_pid_diagrams.py 5c2ae8f2-1ab4-4db5-a358-26bd1188d6a9
```

## Testbed Overview
```shell
cd testbed-overview/
python extract_stage_list.py e2b9b8e4-d6fe-49ea-bbdf-adb171a0d2a1
```
