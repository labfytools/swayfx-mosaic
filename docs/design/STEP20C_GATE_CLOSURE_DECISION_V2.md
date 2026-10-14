# SWAYFX_MOSAIC_STEP20C_SAVED_LIFETIME_INPUT_EPOCH_AND_GPU_CAUSALITY_BATCH_V1

> EXPERIMENTAL — édition du 2026-10-14. Ticket `SWAYFX_MOSAIC_STEP20C_SAVED_LIFETIME_INPUT_EPOCH_AND_GPU_CAUSALITY_BATCH_V1`. Revue finale indépendante du dossier complet : ACCEPTED / audit PASS pour la fidélité expérimentale ; publication PREPARED à cette édition, reçu final hors Git après push. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT YET SUPPORTED. Aucun contrat UX, package ou production adopté.

LAB désigne `/home/fy59/swayfx-mosaic-saved-input-gpu-pz4z428f`, laboratoire privé hors Git. Les chemins LAB sont des références locales, pas un kit distribué. Le [dossier V2](STEP20C_GATE_CLOSURE_DECISION_V2.md) fixe la provenance commune et les limites. Les rapports historiques restent immuables.

## Décision et provenance

**PARTIALLY_ADVANCED** scientifiquement ; recommandation unique **PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE**. La progression porte sur timeout naturel, instance saved fiable malgré reuse, input en mutation et mécanisme FBO local. Les P1 causalité entière/GPU lifetime/génération/damage demeurent ouverts. Le volume de tests ne décide pas du verdict.

Point de départ main `ed9375797e717e31325456970a8cfbc4fd148df4`. Ancien ticket TARGETED_CLOSURE :14 runs/125 captures/520 réservations consommés et immuables ; audit baseline vérifie566 checks. Le nouveau lot est distinct : six nouveaux runs sur plafond8, 59 captures sur96 (saved30/input18/GPU11), 240 réservations. Deux tokens optionnels ordering/pristine restent inutilisés, sans discriminant scientifique nouveau justifié ; ce rapport n’autorise aucune reprise. SceneFX GPU1/Mosaic GPU1/stage GPU1, aucun build input/core. Maximum durée9,487s sur150.

Les 42 tests communs et six tests GPU passent. Les validations rejettent preuves fabriquées, ACK faux, timeout teardown, adresses simultanées, mauvaises identités/coordonnées, faux present et readback/restauration/epoch invalide. Gel commun SHA `ea46a021d1453fc4842e2815faa488b0a6560ae66bc3e7900b55b8db9ac1ed7a`,309 bindings ; gel GPU SHA `49baa41f0afe78b13de8d8272039081fcd9551d814d4241786720517f68bded3`,118 bindings. Revues préflight/delta indépendantes ACCEPTED ; ce sont des revues bornées, pas la revue finale du dossier complet.

`LAB/audit/run-artifacts-six.json`,241 fichiers, SHA `7ff6e0b1abfedca7493278d0dcae1afe557434a1f10700faacc28106561b8703`, lie les preuves brutes. `LAB/audit/batch-validation.{md,json}` contient commandes/tests/protections. Les petits reçus publics [provenance](../../tooling/probes/step20c-saved-input-gpu-batch/provenance.json), [résultats](../../tooling/probes/step20c-saved-input-gpu-batch/results.json), [résumé scientifique GPU](../../tooling/probes/step20c-saved-input-gpu-batch/gpu-native-summary.json) sont des indices ; images/binaires/logs/C privés ne sont pas distribués.

## Matrice d’observation

| Campagne nouvelle | Runs/captures | measurements_pass | runtime_exit | scientific_cleanup | architecture_verdict |
| --- | --- | --- | --- | --- | --- |
| Saved C3/A/G | 3/30 | PASS |runner1, IPC1, processus0 ; global INCONCLUSIVE|INCONCLUSIVE (helpers error32 au teardown, owner0)|PARTIALLY_FEASIBLE |
| Input A/G | 2/18 | PARTIALLY_FEASIBLE |runner1, IPC1, processus0 ; global INCONCLUSIVE|INCONCLUSIVE (helpers error32, owner0)|PARTIALLY_FEASIBLE |
| GPU nouveau SHA | 1/11 | PARTIALLY_FEASIBLE |runner0, IPC1, processus0 ; global INCONCLUSIVE|PASS, quatre clients error0|PARTIALLY_FEASIBLE |

Cleanup mécanique PASS, PIDs reaped et sockets/runtime dirs propriétaires absents. Ces propriétés n’établissent aucune fin GPU. Revue GPU locale indépendante et analyses CPU n’ajoutent aucun run. A/G/C3 ont les identités exactes du [dossier historique](STEP20C_TARGETED_CLOSURE_DECISION.md) ; GPU a son nouveau SHA dans le [rapport](STEP20C_GPU_FBO_CACHE_CAUSALITY.md). Aucun succès natif C3/GPU ne se transfère à A/G.

## Gates finales de cette édition

```text
STEP20C_TARGETED_REPLAY_AND_ASSERTIONS=PASS
SAVED_EPOCH_IDENTITY_REPLAY=PASS
SAVED_REAL_HELD_CONFIGURE=PASS
SAVED_HOLD_RGB=PASS
SAVED_NATURAL_TIMEOUT=PASS
SAVED_C3_NATIVE_EPOCH=OBSERVED_DERIVED_LIFETIME_INSTANCE
SAVED_A_RGB_TIMEOUT=PASS
SAVED_G_RGB_TIMEOUT=PASS
SAVED_NATURAL_RETIREMENT=C3_OBSERVED_A_G_NOT_OBSERVABLE
SAVED_NATIVE_RELEASES=PARTIALLY_OBSERVED_TARGET_RETIREMENT_RELEASE_NOT_OBSERVED
SAVED_CPU_SIGNAL_LIFETIME=PARTIALLY_FEASIBLE
SAVED_GPU_COMPLETION=NOT_PROVEN
INPUT_EVENT_TIME_CORRELATION=PARTIALLY_FEASIBLE
INPUT_STANDARD_RETURN=FEASIBLE_SAMPLED_A_G
GPU_READBACK_DESIGN_REVIEW=ACCEPTED
GPU_DIAGNOSTIC_RUNTIME=INCONCLUSIVE_TERMINAL_IPC_1
FBO_CONTENT_IDENTITY=SAMPLED_NATIVE_ROIS_WITH_INTRA_PASS_IDENTITY
CACHE_FRESH_DOMAIN=OUTSIDE_DOMAIN_HISTORY_OBSERVED_LOCALLY
CACHE_A_RETURN_CAUSALITY=INCONCLUSIVE_WHOLE_FIELD
CACHE_LOCAL_FBO_HISTORY=PARTIALLY_SUPPORTED_LOCAL_FBO_HISTORY
OUTPUT_BUFFER_IDENTITY=NOT_PROVEN
NATIVE_ORDERING_DISCRIMINANT=NOT_EXERCISED
NATIVE_COMMIT_PRESENT=414_COMMITS_400_PAIRED_14_MISSING_CAUSE_UNKNOWN
NATIVE_BUFFER_LIFETIME=NOT_PROVEN
NATIVE_DAMAGE_COVERAGE=PARTIALLY_FEASIBLE_SAMPLED_EXTENTS
ATOMIC_GENERATION=NOT_PROVEN
STEP20C_MINIMAL_PRIVATE_SOURCE_REVIEW=ACCEPTED
STEP20C_CORE_BUILD=NOT_RUN
STEP20C_CORE_RUNTIME=NOT_RUN
STEP20C_ABI_MAINTENANCE_AUDIT=PARTIALLY_FEASIBLE_EXACT_PAIR_ONLY
STEP20C_PACKAGING_DRAFT_AUDIT=PARTIALLY_FEASIBLE_FULL_PACKAGE_NOT_RUN
STEP20C_FINAL_INDEPENDENT_REVIEW=ACCEPTED
STEP20C_DOCUMENTARY_PUBLICATION=PARTIAL
SWAYFX_MOSAIC_STEP20C_SAVED_LIFETIME_INPUT_EPOCH_AND_GPU_CAUSALITY_BATCH_V1=PARTIALLY_ADVANCED
STEP20A=DONE
STEP20B=EXPERIMENTAL
STEP20C=NEXT
STEP20D–G=PLANNED
PRODUCTION_MULTI_OUTPUT=NOT_YET_SUPPORTED
```

Final review ACCEPTED / audit PASS ; publication PREPARED à cette édition explique le marqueur PARTIAL. Les refs et le reçu final hors Git attestent les pushes réellement effectués ; aucune publication PASS anticipée. Le marqueur whole-field ne remplace pas le reçu validateur INCONCLUSIVE par l’interprétation locale scientifique.

## ABI, package et décisions encore ouvertes

Audit `LAB/audit/abi-package` :85 overlaps,34 bindings,17 structs/six offsets,121 headers,sept sources historiques vérifiées. A/G stage cinq fichiers chacun ; inventories895/894, chemins uniques894/893. Qualification de la paire exacte seule, aucun ABI-safe général. Le nouveau GPU possède88 headers source/12 bindings shaders générés/56 tokens flags dans son build ; l’ancien inventaire de notices ne qualifie pas l’incorporation du nouveau binaire. Full package NOT RUN, bit-reproducibility NOT PROVEN, notices/legal HUMAN_REVIEW_REQUIRED ; release/security non nommés.

La cohérence scène/input appliquée est nécessaire ; un compteur atomique spécifique reste UNDECIDED. Popup offscreen hide/dismiss/reposition et click-through universel restent UNDECIDED. Source-only core ACCEPTED après deux cycles ne signifie pas qualification runtime. Aucun pristine source modifié, shader/cache fix, dépendance, public ABI, source de production, UX, package ou patch cumulatif changé.

## Plus petite suite justifiée

Effectuer la publication réelle du jeu documentaire accepté. Une éventuelle suite scientifique exige scope explicite : champ FBO entier/précision native et vraie build/C/UBSan/OOM/headless requalification du core, puis génération/damage/lifetime exactes, ABI/package/legal/maintenance et décisions UX. Les deux tokens optionnels ne donnent aucune autorisation permanente. Les documents [saved](STEP20C_SAVED_NATURAL_TIMEOUT_AND_EPOCH_IDENTITY.md), [input](STEP20C_INPUT_EVENT_TIME_AND_APPLIED_CAMERA.md), [GPU](STEP20C_GPU_FBO_CACHE_CAUSALITY.md), [native](STEP20C_NATIVE_PRESENT_DAMAGE_LIFETIME.md), [core](STEP20C_MINIMAL_PRIVATE_INTEGRATION_CORE.md) et [draft](STEP20C_PRODUCTION_INTEGRATION_DECISION_DRAFT.md) détaillent les frontières.

## Revue finale et synchronisation des métadonnées

La revue indépendante `/root/batch_final_audit` (Astra high, isolée, lecture seule) est ACCEPTED / audit PASS : zéro BLOCKING, un NON_BLOCKING, trois FUTURE_SCOPE. Elle vérifie 33 fichiers/325046 octets avant synchronisation, relance 42 tests communs, rejette onze falsifications supplémentaires des métadonnées GPU réelles et recorrèle dix livraisons input positives. Le [reçu](../../tooling/probes/step20c-saved-input-gpu-batch/final-review.json) est une transcription structurée fidèle matérialisée par le parent, pas un verbatim. La correction non bloquante compte 12 signaux natifs distincts sous 24 rattachements ambigus. Les sources exécutables, gels et preuves brutes restent inchangés. Les hashes des métadonnées dérivées après cet avis sont enregistrés séparément dans `LAB/audit/post-review-public.json` ; ils ne sont pas présentés comme les octets des 33 fichiers revus. La publication de cette édition est PREPARED ; reçu final/refs après push hors Git pour éviter une auto-référence du commit.
