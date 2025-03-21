import json
import os

import requests
import time
import csv
import argparse
import pytz
from datetime import datetime

API_URL = "https://atlas.ripe.net/api/v2/probes/{}"
tz = pytz.timezone('Europe/Paris')

def get_probe_info(probe_id):
    """Récupère et structure les informations d'un probe via l'API RIPE Atlas."""
    url = API_URL.format(probe_id)
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Gestion de geometry
        geometry = data.get("geometry")
        longitude, latitude = ("N/A", "N/A")
        if geometry and "coordinates" in geometry:
            longitude, latitude = geometry["coordinates"]

        # Gestion des timestamps
        def format_timestamp(ts):
            return datetime.fromtimestamp(ts, tz).strftime('%Y-%m-%d %H:%M:%S') if ts else "N/A"

        return {
            "ID": data.get("id", "N/A"),
            "IPv4": data.get("address_v4", "N/A"),
            "ASN": data.get("asn_v4", "N/A"),
            "Pays": data.get("country_code", "N/A"),
            "Longitude": longitude,
            "Latitude": latitude,
            "Status": data.get("status", {}).get("name", "Unknown"),
            "First Connected": format_timestamp(data.get("first_connected")),
            "Last Connected": format_timestamp(data.get("last_connected")),
            "Tags": ", ".join(tag["name"] for tag in data.get("tags", [])) if data.get("tags") else "N/A"
        }
    return None

def get_output_filename(base_name, output_format):
    """Génère un nom de fichier correspondant au format de sortie."""
    ext = {"csv": ".csv", "json": ".json", "txt": ".txt"}.get(output_format, ".csv")
    return os.path.splitext(base_name)[0] + ext  # Remplace l'extension si déjà présente

def export_data(probes, filename, output_format):
    """Exporte les données dans le format spécifié (CSV, JSON, TXT)."""
    if not probes:
        print("❌ Aucune donnée à exporter.")
        return

    if output_format == "csv":
        keys = probes[0].keys()
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(probes)

    elif output_format == "json":
        with open(filename, mode="w", encoding="utf-8") as file:
            json.dump(probes, file, indent=4, ensure_ascii=False)

    elif output_format == "txt":
        with open(filename, mode="w", encoding="utf-8") as file:
            for probe in probes:
                file.write(f"ID: {probe['ID']}\n")
                file.write(f"IPv4: {probe['IPv4']}\n")
                file.write(f"ASN: {probe['ASN']}\n")
                file.write(f"Pays: {probe['Pays']}\n")
                file.write(f"Longitude: {probe['Longitude']}, Latitude: {probe['Latitude']}\n")
                file.write(f"Status: {probe['Status']}\n")
                file.write(f"First Connected: {probe['First Connected']}\n")
                file.write(f"Last Connected: {probe['Last Connected']}\n")
                file.write(f"Tags: {probe['Tags']}\n")
                file.write("-" * 40 + "\n")

    print(f"✅ Exporté avec succès dans {filename}")


def filter_probes(probes, country, connected, first_connected_after, last_connected_after):
    """Filtre les probes selon les critères donnés."""
    filtered = []

    for probe in probes:
        if country and probe["Pays"] != country:
            continue
        if connected is not None and (probe["Status"] == "Connected") != connected:
            continue
        if first_connected_after and probe["First Connected"] != "N/A":
            first_time = datetime.strptime(probe["First Connected"], '%Y-%m-%d %H:%M:%S')
            if first_time < first_connected_after:
                continue
        if last_connected_after and probe["Last Connected"] != "N/A":
            last_time = datetime.strptime(probe["Last Connected"], '%Y-%m-%d %H:%M:%S')
            if last_time < last_connected_after:
                continue

        filtered.append(probe)

    return filtered


def main():
    """Récupère les probes et applique les filtres via arguments CLI."""
    parser = argparse.ArgumentParser(description="Récupération des probes RIPE Atlas avec filtres.")
    parser.add_argument("--start-id", type=int, default=1, help="ID de départ des probes")
    parser.add_argument("--end-id", type=int, default=50, help="ID de fin des probes")
    parser.add_argument("--country", type=str, help="Filtrer par pays (ex: FR, US, DE)")
    parser.add_argument("--connected", type=int, choices=[0, 1], help="1 = connectés, 0 = déconnectés")
    parser.add_argument("--first-connected-after", type=str,
                        help="Filtrer par date de première connexion (format: YYYY-MM-DD)")
    parser.add_argument("--last-connected-after", type=str,
                        help="Filtrer par date de dernière connexion (format: YYYY-MM-DD)")
    parser.add_argument(
        "--format", type=str, choices=["csv", "json", "txt"], default="csv",
        help="Format de sortie des données (csv, json, txt)"
    )
    parser.add_argument(
        "--output", type=str, default="filtered_probes",
        help="Nom du fichier de sortie (sans extension, qui sera ajoutée automatiquement)"
    )

    args = parser.parse_args()

    # Conversion des dates si présentes
    first_connected_after = datetime.strptime(args.first_connected_after,
                                              "%Y-%m-%d") if args.first_connected_after else None
    last_connected_after = datetime.strptime(args.last_connected_after,
                                             "%Y-%m-%d") if args.last_connected_after else None
    connected_filter = bool(args.connected) if args.connected is not None else None

    probes = []
    for probe_id in range(args.start_id, args.end_id + 1):
        info = get_probe_info(probe_id)
        if info:
            probes.append(info)
        time.sleep(0.25)

    # Application des filtres
    filtered_probes = filter_probes(
        probes,
        country=args.country,
        connected=connected_filter,
        first_connected_after=first_connected_after,
        last_connected_after=last_connected_after
    )

    # Export data
    output_filename = get_output_filename(args.output, args.format)
    export_data(filtered_probes, output_filename, args.format)

if __name__ == "__main__":
    main()
