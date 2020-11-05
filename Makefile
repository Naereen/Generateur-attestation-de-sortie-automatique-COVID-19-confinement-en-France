# Makefile to send this project to Szam
SHELL=/usr/bin/env /bin/bash

all:	send

send:	send_zamok
send_zamok: clean
	CP --exclude=.ipynb_checkpoints --exclude=.git --exclude=details*json --exclude=attestation* ./ ${Szam}publis/Generateur-dattestation-de-sortie-automatique.git/

run:
	#ipython3 < generateur_attestation_sortie_automatique.py
	./launch.sh

watch_run:
	#watch -n 3300 'ipython3 < generateur_attestation_sortie_automatique.py'
	watch -n 3300 './launch.sh'

clean:
	-trash geckodriver.log
	-trash attestation*.pdf attestation*.png
