# ripe-atlas-atlas
Réalisé dans le cadre d'un projet universitaire centré sur le partage d'informations.

Root API Directory : https://atlas.ripe.net/api/v2/root/

Récupération des probes RIPE Atlas avec filtres.

options:
```
  -h, --help            show this help message and exit
  --start-id START_ID   ID de départ des probes
  --end-id END_ID       ID de fin des probes
  --country COUNTRY     Filtrer par pays (ex: FR, US, DE)
  --connected {0,1}     1 = connectés, 0 = déconnectés
  --first-connected-after FIRST_CONNECTED_AFTER
                        Filtrer par date de première connexion (format: YYYY-MM-DD)
  --last-connected-after LAST_CONNECTED_AFTER
                        Filtrer par date de dernière connexion (format: YYYY-MM-DD)
  --format {csv,json,txt}
                        Format de sortie des données (csv, json, txt)
  --output OUTPUT       Nom du fichier CSV de sortie
```
