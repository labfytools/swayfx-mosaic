# STEP20C — décision d’intégration production, draft

> EXPERIMENTAL — édition du 2026-10-14. Ticket `SWAYFX_MOSAIC_STEP20C_SAVED_LIFETIME_INPUT_EPOCH_AND_GPU_CAUSALITY_BATCH_V1`. Revue finale indépendante du dossier complet : ACCEPTED / audit PASS pour la fidélité expérimentale ; publication PREPARED à cette édition, reçu final hors Git après push. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT YET SUPPORTED. Aucun contrat UX, package ou production adopté.

LAB désigne `/home/fy59/swayfx-mosaic-saved-input-gpu-pz4z428f`, laboratoire privé hors Git. Les chemins LAB sont des références locales, pas un kit distribué. Le [dossier V2](STEP20C_GATE_CLOSURE_DECISION_V2.md) fixe la provenance commune et les limites. Les rapports historiques restent immuables.

La recommandation unique reste **PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE**. Ce draft remplace les réponses devenues obsolètes du ticket antérieur, sans modifier ses rapports immuables. Les vingt questions ci-dessous explicitent le dossier de décision du nouveau ticket ; elles ne constituent pas des décisions production. Le [dossier V2](STEP20C_GATE_CLOSURE_DECISION_V2.md) lie résultats, budget et preuves, les rapports saved/input/GPU/native/core en détaillent la portée.

## 1. Un saved buffer naturel est-il retiré sur C3/A/G ?

C3 : instance 15 créée/dessinée puis SD_REMOVE/SD_NODE_DESTROY après timeout natif et avant post-capture. A/G : timeout wire/RGB propre validé, retrait natif NOT OBSERVABLE. Aucun transfert C3.

## 2. Le clipping saved et H2 entière sont-ils établis ?

Oui aux captures des trois runs : target crossing H1 réel, held avant deadline, H2 entière RGB exacte durant held/timeout/final. Cela qualifie le timeout expérimental5 000 ms et les états échantillonnés ; pas tous les frames ni timeout ordinaire 200 ms.

## 3. Les épisodes natifs restent-ils fiables malgré reuse ?

Oui pour le replay dérivé :23 instances non chevauchantes, cible15 ; adresse réutilisable, owner/tree/source/intervalle corrélés. Ce récit observé ne crée aucune génération native.

## 4. Le lifetime CPU saved est-il entièrement clos ?

Non : lock 3→4 et retrait cible observés,17 records release globaux non ambigus et12 signaux natifs distincts, conservés sous 24 rattachements ambigus conservés. Release de retraite cible NOT OBSERVED ; pas d’attribution arbitraire.

## 5. Le lifetime GPU est-il qualifié ?

Non. Saved node_destroy/unlock/SHM release/readback ne démontrent pas GPU completion. Aucun fence ni identité exacte du buffer présenté : NOT PROVEN.

## 6. L’input reste-t-il fidèle après mutation focus/caméra ?

PARTIALLY_FEASIBLE sur A/G propres :full→empty→full, focus filler→owner, deux mutations caméra et six clics/treize moves chacun. L’origine temporellement compatible explique le replay historique (-314,30)→(324,5) avec origine(-638,25), sans rows[-1] arbitraire.

## 7. Le retour standard est-il terminé ?

Oui pour les deux nouveaux runs input, ciblé splith, input standard puis close owner/error0 et H2 exacte. Runtime global INCONCLUSIVE/IPC1 et helper error32 teardown restent séparés.

## 8. Une atomicité particulière est-elle nécessaire à une tranche minimale ?

Le contrat exige même état appliqué pour rendu/input. Le mécanisme particulier compteur atomique reste UNDECIDED ; aucun design adopté, ATOMIC_GENERATION NOT PROVEN.

## 9. La cause whole-H1 A/B/A est-elle identifiée ?

Le mécanisme local FBO history est PARTIALLY_SUPPORTED :down-1 queue hors domaine, première divergence fraîche down-2, cinq supports divergents/11 et contribution fraîche différentielle0. Whole-field et événements historiques restent INCONCLUSIVE/NOT PROVEN ; whole-H1 FAIL 34 323/max 6 conservé.

## 10. Pristine a-t-il été touché ?

Non. Résultats antérieurs pristine 37 252/max 6 immuables ; aucun run GPU/pristine optionnel. Le modèle froid positif/max33 n’est pas un historique natif : queues préchauffées natives plus sombres.

## 11. Un correctif SceneFX est-il justifié ou autorisé ?

Aucun correctif shader/cache autorisé par ce résultat local. Champ FBO entier/précision effective et requalification distincte sont nécessaires avant changement causal. Aucun seuil ou sampler ajusté.

## 12. Quels buffers sont réellement identifiés ?

SHM wire/source, instance saved dérivée C3 et ROI GPU avec identité intra-pass. Up0/result/cache RGBA exact local ; presubmitRGB formule exacte. Aucun outputbuffer présenté ni lifetime persistant complet identifié.

## 13. Quelle instrumentation résiduelle change la provenance ?

CORRECTION explicite :fx_pass_submit bind-before-failed était déjà pristineScene37, fichier SHA398d594ace7257f4b69319290be7c1f14dc1ded446545ceb337404f5caab0cd3 identique pristine/base/core. L’ancien draft prétendant un ordre différent est réfuté ; rapports historiques non réécrits. PI/listeners/logs/readback restent perturbateurs.

## 14. Quelle instrumentation peut être supprimée sans perte de garantie ?

Core privé omet PI/C3/OPT et conserve quatre logs intrinsèques. Retrait source revu, aucune garantie de neutralité ou qualification runtime héritée. A/G diffèrent dans sept fichiers source C, pas huit ; aucun nouveau counter adopté.

## 15. Le noyau source-only privé est-il acceptable ?

SOURCE_REVIEW ACCEPTED après deux cycles corrections allocation failure/arithmétique/fullscreen/intersection disjointe.417 fichiers Mosaic/85 SceneFX/30 hashes/3 forward checks. Aucun build/runtime/UBSan/OOM C effectué, archive statique future non sélectionnée par static:true.

## 16. Que prouvent commit/present et damage ?

Nouveaux six logs 414/400/14, missing cause UNKNOWN ; cinq logs 340/330/10. Damage 38 transitions :7 covered by sampled union/26 no change/5 NOT OBSERVABLE. Ni tous frames, ni régions minimales, ni présentation exacte. Ordering optionnel NOT_EXERCISED.

## 17. Quelles décisions UX empêchent encore intégration ?

Offscreen popup hide/dismiss/reposition et click-through sous grab UNDECIDED. Aucun universal click-through ni nouvelle règle focus/taille/animation ; UX canonique inchangée.

## 18. Quelles décisions release/security/notice/ABI restent ouvertes ?

Exact-pair seulement85 overlaps/34 bindings/17 structs/6 offsets/121 headers. Stages A/G5 fichiers, inventories895/894 ; notices nouvelle GPU non qualifiées. Full package NOT RUN, bit-reproducibility NOT PROVEN, legal HUMAN_REVIEW_REQUIRED ; release/security à nommer, sans SLA inventé.

## 19. Quelles requalifications sont obligatoires pour un nouveau SHA ?

Build/C/UBSan/OOM privés, modèle/ELF/ABI/pair exact/stage, pristine et matrice clipping/input/timeout/fullscreen/standard/damage/lifetime. Notices/package/legal avant distribution ; contrats canoniques avant production. Les résultats précédents ne se transfèrent pas.

## 20. Quelle décision et quelle plus petite suite retenir ?

PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE ; global PARTIALLY_ADVANCED, P1 GPU whole-field/lifetime/génération/damage ouverts. Revue finale ACCEPTED / audit PASS ; publication PREPARED à cette édition, reçu final hors Git après push. Aucun scope production/STEP20D ; suite documentaire puis nouveaux scopes explicites pour champ FBO/précision et core C/headless.
