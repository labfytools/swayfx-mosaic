# STEP20C — noyau privé minimal source-only

> EXPERIMENTAL — édition du 2026-10-14. Ticket `SWAYFX_MOSAIC_STEP20C_SAVED_LIFETIME_INPUT_EPOCH_AND_GPU_CAUSALITY_BATCH_V1`. Revue finale indépendante du dossier complet : ACCEPTED / audit PASS pour la fidélité expérimentale ; publication PREPARED à cette édition, reçu final hors Git après push. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT YET SUPPORTED. Aucun contrat UX, package ou production adopté.

LAB désigne `/home/fy59/swayfx-mosaic-saved-input-gpu-pz4z428f`, laboratoire privé hors Git. Les chemins LAB sont des références locales, pas un kit distribué. Le [dossier V2](STEP20C_GATE_CLOSURE_DECISION_V2.md) fixe la provenance commune et les limites. Les rapports historiques restent immuables.

## Provenance et portée

Candidat privé SOURCE_ONLY, hors dépôt et sans build/runtime. Parents : Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754`, SceneFX `37ccd723bef49e6891156ffafce8f549f01446cc`. Huit patches historiques fonctionnels plus deux patches de commentaires sont reconstruits ; il ne s’agit pas de dix patches fonctionnels. Le noyau inclut clip natif/input, owner-derived root/nested popup, hidden-owner guard, retirement/standard layout et lifetime fonctionnelle. Aucune instrumentation PI/C3/OPT ni nouveau compteur de génération n’est ajoutée. Quatre statements de log intrinsèques restent ; leur neutralité n’est pas prouvée.

## Corrections privées et revue bornée

Deux cycles resolver/revue ont corrigé les blockers : échec allocation→abort préservant ABI void ; translation arithmétique large ; suppression des clips sur tous les ancêtres fullscreen courants. Le second delta rejette l’intersection popup disjointe avant soustraction large, évitant l’overflow montré par le helper box historique sur INT_MIN face à800. Aucun wlroots système n’est modifié. Les helpers caméra préexistants convertissent scroll vers int64 avant casts concernés ; cela ne qualifie pas un pipeline NaN/Inf complet.

`LAB/reviews/core-final-source-and-runtime-review.json` est ACCEPTED pour les sources exactes et les cinq runs antérieurs réellement exécutés, sans les imputer au noyau : 417 fichiers Mosaic/85 SceneFX, 30 hashes source, 309 bindings et trois forward-apply checks PASS. Les tests numériques/source et rejets hors ligne ne remplacent pas un test C effectif. Build, runtime, UBSan et injection OOM C du core : NOT RUN ; zéro build core.

| Artefact privé | SHA256 |
| --- | --- |
| Dossier final | `794ef350bd82f6c8b633f8c17f3aeae47a2b5b9f3ba137d8d4306c85150fca92` |
| Mosaic transaction | `e5066df7808a1633c635582c052ba89931c2856a54f6b471ff1009a4b455ef6c` |
| Scene source | `99992429f9a1d2754042989d89904fb6d705f963d74f4456d737fc9da3e0927d` |
| Patch Mosaic final | `af680be7322a9257769cadc137c487b7f9f880a0b0d66df7701ae26b8baf1fe6` |
| Patch SceneFX final | `750337f75f9dc5ca655d3cd10f49bdd04169cca4dc53459d7f0d9eb8ad4db25a` |

Meson core ne contient pas `static:true` : sélection d’archive privée reste une étape future, pas un lien réalisé. SOURCE_REVIEW=ACCEPTED ne signifie pas BUILDABLE ou runtime FEASIBLE. Aucun patch core/C/client/GPU ni fork complet n’est publié avec la fixture Python commune.

## Gates futures

Avant tout nouveau SHA : autorisation distincte du build privé, choix effectif archive, compilation C/UBSan/OOM, modèle/ELF/ABI/stage, contrôle pristine et matrice headless pertinente, requalification clipping/input/fullscreen/standard return/timeout/damage/lifetime. Les résultats A/G/C3/GPU ne se transfèrent pas au core. Contrats canoniques avant éventuelle production ; aucune intégration ni STEP20D autorisée ici.
