# STEP20C — present natif, damage et lifetime

> EXPERIMENTAL — édition du 2026-10-14. Ticket `SWAYFX_MOSAIC_STEP20C_SAVED_LIFETIME_INPUT_EPOCH_AND_GPU_CAUSALITY_BATCH_V1`. Revue finale indépendante du dossier complet : ACCEPTED / audit PASS pour la fidélité expérimentale ; publication PREPARED à cette édition, reçu final hors Git après push. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT YET SUPPORTED. Aucun contrat UX, package ou production adopté.

LAB désigne `/home/fy59/swayfx-mosaic-saved-input-gpu-pz4z428f`, laboratoire privé hors Git. Les chemins LAB sont des références locales, pas un kit distribué. Le [dossier V2](STEP20C_GATE_CLOSURE_DECISION_V2.md) fixe la provenance commune et les limites. Les rapports historiques restent immuables.

## Pairage natif

Le pairage utilise (output, commit_seq) et conserve les logs manquants. Cinq runs saved/input : 340 commits, 330 jumelés, 10 sans present connu. Avec GPU : 414/400/14. Les anciens totaux 821/789/32 et 57/55/2 restent immuables. Missing signifie cause UNKNOWN faute de preuve réelle ; ce n’est pas automatiquement une frame abandonnée ou teardown.

Le run ordering natif conditionnel n’a pas été exercé : NATIVE_ORDERING_DISCRIMINANT=NOT_EXERCISED. Un matching commit/present n’identifie pas les pixels du buffer présenté ni GPU completion, et ne prouve aucune atomicité générationnelle.

## Damage échantillonné

`LAB/audit/damage-five-runs.json` analyse 38 transitions : sept différences contenues dans l’union des extents physiques échantillonnées, vingt-six sans changement RGB, cinq NOT OBSERVABLE. Une union d’extents sur des captures stabilisées ne prouve ni toutes les frames, ni région minimale/pixman exacte, ni absence exhaustive de stale pixels, ni identité présentée. Les vingt-six no-change ne sont pas des mesures de couverture damage positive.

## Identités distinctes

SHM source client, saved scene node, référence CPU wlr_buffer, texture/FBO/cache, output-state buffer, commit/present et fin GPU ont des contrats distincts. C3 identifie un épisode de vie observé, pas un numéro de génération ; ses signaux release ambigus ne sont pas attribués arbitrairement. Les ROI GPU ont une identité intra-pass, pas une identité persistante complète ni un buffer présenté. OUTPUT_BUFFER_IDENTITY, NATIVE_BUFFER_LIFETIME, ATOMIC_GENERATION et GPU_COMPLETION restent NOT_PROVEN ; NATIVE_DAMAGE_COVERAGE=PARTIALLY_FEASIBLE.

La cohérence rendu/input avec le même état appliqué reste requise par Architecture ; un mécanisme particulier de compteur atomique n’est pas adopté. Les mesures compatibles, terminal IPC1 et nettoyage scientifique ont les statuts séparés exposés dans les rapports saved/input/GPU. Aucun rerun optionnel n’est consommé pour augmenter le nombre de couples.
