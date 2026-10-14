# STEP20C — événement input et caméra appliquée

> EXPERIMENTAL — édition du 2026-10-14. Ticket `SWAYFX_MOSAIC_STEP20C_SAVED_LIFETIME_INPUT_EPOCH_AND_GPU_CAUSALITY_BATCH_V1`. Revue finale indépendante du dossier complet : ACCEPTED / audit PASS pour la fidélité expérimentale ; publication PREPARED à cette édition, reçu final hors Git après push. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT YET SUPPORTED. Aucun contrat UX, package ou production adopté.

LAB désigne `/home/fy59/swayfx-mosaic-saved-input-gpu-pz4z428f`, laboratoire privé hors Git. Les chemins LAB sont des références locales, pas un kit distribué. Le [dossier V2](STEP20C_GATE_CLOSURE_DECISION_V2.md) fixe la provenance commune et les limites. Les rapports historiques restent immuables.

## Correction du contrat de corrélation

La séquence historique est conservée : global (-314,30), origine pré-injection (-318,25), origine native ultérieure (-638,25), local (324,5). Le local concorde avec l’origine ultérieure. Le replay abandonne le seul rectangle initial comme référence obligatoire et ne sélectionne jamais `rows[-1]` sans preuve temporelle. Un état appliqué doit être compatible avec l’intervalle réel de livraison ; plusieurs états possibles rendent l’attribution INCONCLUSIVE.

Deux nouveaux runs A/G exacts accomplissent input-region full→empty→full, focus filler→owner, deux mutations caméra par run, retour ciblé splith et fermeture normale owner. Chaque run contient six clics, treize moves et neuf captures ; H2 entière reste RGB exacte. Vrais enters/motions, destinataire, serial press/release et snapshots avant/après sont conservés. Les tests négatifs rejettent mauvais owner, serial, coordonnées, origine, état décalé et destinataire inventé.

## Portée observée

INPUT_EVENT_TIME_CORRELATION=PARTIALLY_FEASIBLE ; INPUT_STANDARD_RETURN=FEASIBLE pour ces deux échantillons ; INPUT_ATOMIC_GENERATION=NOT_PROVEN. Les états temporellement compatibles ne constituent ni un compteur atomique commun ni une preuve scène/input/présentation indivisible. Aucun nouveau binaire input n’a été nécessaire ; aucun ordering natif optionnel n’a été exécuté.

measurements_pass=PARTIALLY_FEASIBLE, mais runtime_exit est runner1/IPC1 et outcome global INCONCLUSIVE ; processus0 reaped et cleanup mécanique PASS. Owner close/error0 est réel ; reference/filler error32 au teardown conserve scientific_cleanup INCONCLUSIVE. architecture_verdict=PARTIALLY_FEASIBLE. Aucune erreur produit n’est extrapolée du transport terminal et aucun succès scientifique global ne le masque.

Preuves : `LAB/runs/input-*/run`, `LAB/audit/initial-runtime-summary.json`, fixture dérivée [README](../../tooling/probes/step20c-saved-input-gpu-batch/README.md). Le contrat canonique exige rendu/input cohérents avec le même état appliqué ; la nécessité d’un mécanisme particulier de compteur atomique reste UNDECIDED.
