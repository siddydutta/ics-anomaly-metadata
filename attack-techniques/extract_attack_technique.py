import json
import os
import traceback

import requests
from attack_technique import AttackTechnique
from bs4 import BeautifulSoup
from mitreattack.stix20 import MitreAttackData
from tqdm import tqdm

ATTACK_STIX_DATA_URL = "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/refs/heads/master/ics-attack/ics-attack-15.0.json"
RAW_DATA_FILE = "ics-attack.json"
OUTPUT_DIR = "attack_techniques_json"
OUTPUT_FILE = "attack-techniques.json"


def download_raw_data(filename: str) -> None:
    response = requests.get(ATTACK_STIX_DATA_URL)
    if response.status_code == 200:
        with open(filename, "w") as f:
            f.write(response.text)
    else:
        raise Exception(f"Failed to download data: {response.status_code}")


def extract_technique_data(technique: dict) -> tuple[AttackTechnique, str]:
    technique_id, technique_url = None, None
    for reference in technique["external_references"]:
        if reference["source_name"] == "mitre-attack":
            technique_id = reference["external_id"]
            technique_url = reference["url"]
            break
    json_path = os.path.join(OUTPUT_DIR, f"{technique_id}.json")
    if technique_id and os.path.exists(json_path):
        return None, technique_id
    name = technique["name"]
    description = technique["description"]
    tactics = []
    mitigations = []
    detections = []
    if technique_url is not None:
        response = requests.get(technique_url)
        soup = BeautifulSoup(response.content, "html.parser")
        tactics_card = soup.find("div", id="card-tactics")
        if tactics_card:
            tactic_links = tactics_card.find_all("a")
            tactics.extend([link.text.strip() for link in tactic_links])
        mitigations_table = soup.find("h2", id="mitigations").find_next("table")
        if mitigations_table:
            mitigation_rows = mitigations_table.find("tbody").find_all("tr")
            mitigations.extend(
                [row.find_all("td")[1].text.strip() for row in mitigation_rows]
            )
        detection = soup.find("h2", id="detection")
        if detection:
            detections_table = detection.find_next("table")
            if detections_table:
                detection_rows = detections_table.find("tbody").find_all("tr")
                detections.extend(
                    [row.find_all("td")[2].text.strip() for row in detection_rows]
                )
    attack_technique = AttackTechnique(
        technique_id=technique_id,
        name=name,
        description=description,
        tactics=tactics,
        detections=detections,
        mitigations=mitigations,
        url=technique_url,
    )
    return attack_technique, technique_id


def save_technique_json(attack_technique: AttackTechnique, technique_id: str) -> None:
    json_path = os.path.join(OUTPUT_DIR, f"{technique_id}.json")
    json_str = attack_technique.model_dump_json(indent=2)
    with open(json_path, "w") as f:
        f.write(json_str)


def combine_jsons(output_file: str) -> None:
    all_techniques = []
    for fname in os.listdir(OUTPUT_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(OUTPUT_DIR, fname), "r") as f:
                all_techniques.append(json.load(f))
    with open(output_file, "w") as f:
        json.dump(all_techniques, f, indent=2)


def main():
    download_raw_data(filename=RAW_DATA_FILE)
    mitre_attack_data = MitreAttackData(RAW_DATA_FILE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        techniques = mitre_attack_data.get_techniques(remove_revoked_deprecated=True)
        for technique in tqdm(
            techniques, desc="Processing techniques", unit="techniques"
        ):
            attack_technique, technique_id = extract_technique_data(technique)
            if attack_technique is not None and technique_id:
                save_technique_json(attack_technique, technique_id)
    except Exception:
        traceback.print_exc()
        print(technique_id)
    combine_jsons(OUTPUT_FILE)
    for fname in os.listdir(OUTPUT_DIR):
        if fname.endswith(".json"):
            os.remove(os.path.join(OUTPUT_DIR, fname))
    os.rmdir(OUTPUT_DIR)


if __name__ == "__main__":
    main()
