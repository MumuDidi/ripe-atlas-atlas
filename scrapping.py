import requests
import time

API_URL = "https://atlas.ripe.net/api/v2/probes/{}"

def get_probe_info(probe_id):
    """Récupère les informations d'un probe via l'API RIPE Atlas."""
    url = API_URL.format(probe_id)
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            "id": data.get("id"),
            "IPv4": data.get("address_v4"),
            "ASN": data.get("asn_v4"),
            "Pays": data.get("country_code"),
            "Tags": [tag["name"] for tag in data.get("tags", [])],
            "Status": data.get("status", {}).get("name")
        }
    else:
        return None

def main():
    """Parcourt une plage d'IDs et récupère les informations des probes actifs."""
    for probe_id in range(1, 50):  # Remplace 50 par une plage plus large si besoin
        info = get_probe_info(probe_id)
        if info:
            print(info)
        time.sleep(0.5)  # Pour éviter de surcharger l'API

if __name__ == "__main__":
    main()
