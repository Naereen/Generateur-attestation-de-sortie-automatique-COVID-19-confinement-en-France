#!/usr/bin/env bash

cd /home/lilian/publis/Generateur-dattestation-de-sortie-automatique.git/
python3 ./generateur_attestation_sortie_automatique.py

ls -larth *.pdf

dateNow=$(date '+%Y-%m-%d')
namePDF=$(echo attestation-${dateNow}_*.pdf)
echo CP ${namePDF} ${Szam}attestations/${dateNow}/
CP ${namePDF} ${Szam}attestations/${dateNow}/

echo "Une nouvelle attestation vient d'être générée à ${dateNow}, elle est désormais disponible ici : https://perso.crans.org/besson/attestations/${dateNow}/${namePDF}"
notify-send "Une nouvelle attestation vient d'être générée à ${dateNow}, elle est désormais disponible ici : https://perso.crans.org/besson/attestations/${dateNow}/${namePDF}"
echo FreeSMS.py "Une nouvelle attestation vient d'être générée à ${dateNow}, elle est désormais disponible ici : https://perso.crans.org/besson/attestations/${dateNow}/${namePDF}"
FreeSMS.py "Une nouvelle attestation vient d'être générée à ${dateNow}, elle est désormais disponible ici : https://perso.crans.org/besson/attestations/${dateNow}/${namePDF}"
