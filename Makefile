run:
	ipython3 < generateur_attestation_sortie_automatique.py

watch_run:
	watch -n 3300 'ipython3 < generateur_attestation_sortie_automatique.py'

clean:
	trash geckodriver.log
	trash attestation*.pdf
