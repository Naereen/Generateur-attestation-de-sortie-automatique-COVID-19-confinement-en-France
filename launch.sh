#!/usr/bin/env bash

echo "Nouvelle attetation de sortie en cours de génération..."
notify-send "Nouvelle attetation de sortie en cours de génération..."
cd /home/lilian/publis/Generateur-dattestation-de-sortie-automatique.git/
python3 ./generateur_attestation_sortie_automatique.py

ls -larth *.pdf

dateNow="$(date '+%Y-%m-%d')"
#namePDF=$(echo attestation-${dateNow}_*.pdf)
namePDF="$(ls -larth attestation-${dateNow}*pdf | tail -n1 | grep -o 'attestation.*.pdf')"

if [ ! -f "$namePDF" ]; then
	exit 1;
fi

# Generate a PNG image from the PDF
# http://askubuntu.com/questions/50170/ddg#50180
namePNG="${namePDF%.pdf}"
pdftoppm "${namePDF}" "${namePNG}" -png -f 1 -singlefile
namePNG="${namePNG}.png"

# now compress both PDF and PNG
PDFCompress "${namePDF}"
advpng -z -2 "${namePNG}"

echo CP "${namePDF}" "${namePNG}" "${Szam}attestations/${dateNow}/"
CP "${namePDF}" "${namePNG}" "${Szam}attestations/${dateNow}/"

echo "Une nouvelle attestation vient d'être générée à ${dateNow}, elle est désormais disponible ici : https://perso.crans.org/besson/attestations/${dateNow}/${namePDF} et https://perso.crans.org/besson/attestations/${dateNow}/${namePNG}"
notify-send "Une nouvelle attestation vient d'être générée à ${dateNow}, elle est désormais disponible ici : https://perso.crans.org/besson/attestations/${dateNow}/${namePDF} et https://perso.crans.org/besson/attestations/${dateNow}/${namePNG}"
echo FreeSMS.py "Une nouvelle attestation vient d'être générée à ${dateNow}, elle est désormais disponible ici : https://perso.crans.org/besson/attestations/${dateNow}/${namePDF} et https://perso.crans.org/besson/attestations/${dateNow}/${namePNG}"
FreeSMS.py "Une nouvelle attestation vient d'être générée à ${dateNow}, elle est désormais disponible ici : https://perso.crans.org/besson/attestations/${dateNow}/${namePDF} et https://perso.crans.org/besson/attestations/${dateNow}/${namePNG}"

# make clean
