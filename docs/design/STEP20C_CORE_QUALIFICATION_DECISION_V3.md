# STEP20C — décision de qualification CORE V3

> EXPERIMENTAL — édition du 2026-10-14, avant audit final et publication. Ticket `SWAYFX_MOSAIC_STEP20C_CORE_RECOVERY_OOM_AND_DCC_QUALIFICATION_BATCH_V1`. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT_YET_SUPPORTED ; PRODUCTION_AUTHORIZED=FALSE. Aucun contrat production, UX ou package adopté.

LAB désigne `/home/fy59/swayfx-mosaic-core-recovery-qmhckba5`, hors Git. Le [dossier V3](STEP20C_CORE_QUALIFICATION_DECISION_V3.md), la [fixture source-only](../../tooling/probes/step20c-core-recovery/README.md), ses [résultats compacts](../../tooling/probes/step20c-core-recovery/evidence/results.json) et sa [provenance](../../tooling/probes/step20c-core-recovery/provenance.json) fixent les identités, budgets et limites. Les chemins LAB sont des références locales ; les binaires, PNG et traces restent privés. Aucun résultat historique n’est réécrit.

## Décision et édition

La recommandation unique est **PRIVATE_CORE_NEEDS_TARGETED_EVIDENCE**, ticket **PARTIALLY_ADVANCED**. Les contrôles standard, retour horizontal, vertical, hidden-return et fermeture saved progressent sur le CORE exact ; fullscreen traversant, disponibilité OOM, cohérence native/lifetime, whole-field GPU, maintenance et distribution empêchent une qualification d’intégration.

Cette édition est un snapshot **avant audit final/publication**. Les revues limitées sont acceptées dans leur périmètre ; CORE_FINAL_INDEPENDENT_REVIEW reste NOT_PROVEN et CORE_DOCUMENTARY_PUBLICATION PARTIAL ici. L’audit final, le commit réel, les remotes vérifiés et les marqueurs postpublication appartiennent au reçu privé ultérieur, sans promesse de PASS anticipée.

Le baseline est `main` à `70954e26f62fb3df25995e31b0c615762ff85a60`. Le LAB historique `/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_/` reste fermé,12/14 runs,88 output PNG et90 PNG avec sources. Le nouvel audit vérifie4688 entrées/4250 fichiers, octets/modes/types et ensemble de chemins ; les digests de contenu de répertoires ne sont pas recalculés. Les trois hashes closeout/manifest/publication restent respectivement `5166d6442aae8dfa2a5e939eb5e83141f83c55e7be89f93670eb381e9956df0a`, `4fd7ccedf00a59754db447d015fdca35fbcdda5b7de3820c3655b6e433765ce8` et `45396f706af9374547bda0d76edcb704298bca10a4ea300ae69b4fdb076de655`.

## Identités exactes et absence de transfert

| Objet | SHA256 | Identité / portée |
| --- | --- | --- |
| CORE existant | `29baf31aa3eeed259825c87d0799fa5d3dc83710afb967154604eb1c6657f965` | Build ID1b42e557e38db3440ae8dcf7ac967e4132223365 ; SceneFX0.5 statique |
| Pristine | `8ac865481bc0487344210cd0e16d8e6c7655b29db887cd58ddc11b0ca22fe494` | SwayFX0.6, basefd71a6bdc061bd633b488ae7b83e8a6981d22f86 |
| G1 historique | `1905a20fa72ebcc7ec47d1584a4653654280288096a20005199eb75673ac0383` | Diagnostic GPU distinct ; Build ID1505e31c3dc08d2a7799c2ee9e1b2705eb61f5fe |
| wlroots installé | `7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837` | libwlroots-0.20.so, version0.20.2 exacte |

/proc/PID/exe, maps et renderer sont relevés par lancement. Le renderer observé est FX OpenGL3.2 Mesa26.2.4-arch1.1 AMD Radeon780M. Les diagnostics PI/C3/G1 possèdent une observabilité et des SHAs distincts : leurs identités buffer/saved ne se transfèrent pas au CORE.

## Registre nouveau et qualification

| Runs nouveaux | PNG effectifs / réservés | Résultat ciblé |
| --- | --- | --- |
| S0-pristine-standard / S1-core-standard |24 /24 | Douze RGB homologues exactes ; overflow standard/input B/A/close |
| S2-core-horizontal |16 /18 | Deux chaînes, quatre grabs, splith vivant puis B-close/A-survie/final |
| S3-pristine-vertical / S4-core-vertical |16 /24 | Y600 réellement traversé ; overflow pristine et exclusion CORE |
| S5-pristine-fullscreen / S6-core-fullscreen |24 /28 | Ancêtre non feuille réel ; traversée NOT_EXERCISED, comparaison INCONCLUSIVE |
| S7-core-hidden-return |12 /14 | Même chaîne et serials conservés, aucun dismissal durant hide, retour RGB exact |
| S8-core-saved |10 /12 | Timeout avant release/ACK ; normal-close, SHM3/3 et H2 finale exacte |
| G2 GPU / native ordering optionnel |0 /0 | NOT_RUN : acquisition GPU non défendable / aucun discriminant natif |
| Total |102 /120 |9/11 runs ; cap output160 ; zéro retry |

Les neuf runners sortent0 et les neuf transports IPC terminaux1 ; tous les compositeurs et clients sortent0. Les fermetures scientifiques explicites et le nettoyage mécanique passent. Les reçus bruts architecture INCONCLUSIVE restent distincts de la qualification ciblée PARTIALLY_FEASIBLE. Chaque argv, durée, owner/workspace, protocole/grabs, hash de capture, code et reçu de fermeture est conservé dans les résultats compacts et les chemins per-run LAB. Chaque run reste sous150s et18 PNG. Aucun build compositeur/GPU, staging ni installation nouveau.

Les [contrôles standard/vertical/fullscreen](STEP20C_CORE_STANDARD_VERTICAL_FULLSCREEN_RECOVERY.md) et le [lifecycle hidden/saved](STEP20C_CORE_HIDDEN_SAVED_LIFECYCLE_RECOVERY.md) détaillent la matrice. La limite X/0 du champ brut vertical est conservée et expliquée ; le prédicat exécuté Y/600 et les bornes démontrent la traversée. S5/S6 restent non comparables, sans défaut UX déduit. Les cases non exercées ne sont pas reclassées.

## Tests et revues limitées

La [première revue](../../tooling/probes/step20c-core-recovery/evidence/preflight-initial.json) demandait correction sur la fausse réussite possible de fermeture SHM. Un seul delta R1 est [accepté](../../tooling/probes/step20c-core-recovery/evidence/graphics-delta-accepted.json), manifesteed0c2be50d067f273e884c338b607a47d066d3a290432df99a513c620346fbc7,565 entrées. Les20 tests graphics,36 GPU et5 native offline passent dans les reçus de cette campagne. La [revue runtime](../../tooling/probes/step20c-core-recovery/evidence/runtime-evidence-accepted.json) vérifie les102 captures et neuf fermetures ; la [revue OOM](../../tooling/probes/step20c-core-recovery/evidence/oom-initial-accepted.json) reproduit40 commandes attendues et six mutants. Les résumés publics sont des transcriptions structurées fidèles matérialisées par le parent, non des fichiers rédigés par les reviewers ni des verbatim.

La [validation GPU](STEP20C_GPU_DCC_MODIFIER_AWARE_VALIDATION.md) répare le prédicat par plan, mais le replay complet rejette effective halfpixel ; read_success NOT_PROVEN/queue GL UNOBSERVED empêchent G2 avec le même binaire sous zéro build. Les [options OOM](STEP20C_MANDATORY_CLIP_OOM_POLICY_OPTIONS.md) restent une étude source-only ; la politique de disponibilité demeure UNDECIDED. Les erreurs transitoires de setup/extraction sont archivées séparément des résultats finaux.

## Ordering, damage et lifetime

`LAB/audit/historical-native.json` conserve les tuples `(LAB,run,output,commit_seq)` et hashes des logs. Les groupes sont rejoués séparément, sans sommer les logs redondants :

| Groupe / LAB | Commits / presents appariés / sans present observé | Cause des absences |
| --- | --- | --- |
| Initial, swayfx-mosaic-overnight-mcolx0gq |57 /55 /2 | UNKNOWN |
| Targeted, swayfx-mosaic-targeted-7gge6h8b |821 /789 /32 | UNKNOWN |
| Saved/input/GPU, swayfx-mosaic-saved-input-gpu-pz4z428f |414 /400 /14 | UNKNOWN |

Les comptes par output et les seq absents sont conservés dans le reçu, y compris seq2 ; ce gap n’est pas automatiquement un bug ou un teardown prouvé. Les nouveaux S n’ont pas de hooks PI : aucun compte natif équivalent n’est inventé. L’ordering optionnel est NOT_RUN faute de nouveau discriminant ; CORE_NATIVE_ORDERING reste INCONCLUSIVE.

Les mutations demandées, état owner/workspace/current, scène applied, hits et damage sont corrélés seulement quand les identifiants et fenêtres temporelles existent. SPIKE_DAMAGE observe des extents soumis aux rings et des RGB stabilisées ; ni toutes les régions/frames, ni contenu exact présenté, ni GPU completion ne sont prouvés. CORE_SAMPLED_DAMAGE=PARTIALLY_FEASIBLE ; CORE_BUFFER_IDENTITY et CORE_ATOMIC_GENERATION restent NOT_PROVEN. L’exigence canonique rendu/input sur même état appliqué demeure ; aucun compteur atomique particulier n’est choisi.

## ELF, stage existant et décisions ouvertes

`LAB/audit/elf-stage.json` revérifie le CORE exact ELF64 PIE, SceneFX statique sans DT_NEEDED SceneFX ni RPATH/RUNPATH et sans relocation non résolue. Le Stage1 historique vérifié contient exactement `/usr/bin/swayfx-mosaic` mode755 et quatre notices mode644 sous `/usr/share/licenses/swayfx-mosaic/`, aucun lien/fichier supplémentaire ; il n’est pas recréé. Notices **PARTIAL/LEGAL_NOT_APPROVED**, full future package et bit-reproducibility non acquis. Les mesures historiques43 bindings/40 symboles scène, node112/tree128 et offsets parent8/enabled32/visible88/children112 sont locales à cette paire, pas une ABI future garantie. Les85 overlaps ne démontrent seuls ni85 défauts ni la sûreté.

L’intégration reste bloquée par OOM availability/P1, observabilité/cohérence native et lifetime, complete damage/effects/whole-field GPU, maintenance SceneFX/wlroots exacte et distribution/licences. Offscreen-popup et fullscreen UX restent UNDECIDED ; aucun click-through universel. Release/security owners et reviewer juridique humain restent à désigner. Le [draft d’intégration actualisé](STEP20C_PRODUCTION_INTEGRATION_DECISION_DRAFT.md) propose uniquement les étapes de décision.

Le contrôle post-runtime `LAB/audit/post-runtime-safety.json` vérifie hashes PKGBUILD, patch production, /usr/bin/sway et wlroots inchangés, Sway quotidien PID2325/start2833 inchangé,52 spawns possédés sans PID vivant et tous runtimes privés supprimés. Aucune session quotidienne ni IPC implicite utilisée ; aucun déploiement ou rollback réel.

## Validation documentaire et exception de provenance

Le ticket précédent signalait `git diff --cached --check` exit2 sur les archives byte-identiques. Le contrôle readonly `git diff 70954e26^ 70954e26 --check` reproduit exit2 avec huit lignes de diagnostic dans `LAB/audit/previous-published-whitespace-check.json`. Il compare un commit publié ; il ne reconstruit pas l’ancien index. Les archives historiques restent intactes.

Trois nouvelles copies publiques Python ont seulement leur suffixe de lignes vides final normalisé pour satisfaire le nouveau contrôle whitespace. Les octets exécutés et le manifeste LAB demeurent immuables ; `evidence/public-source-eof-normalization.json` lie hashes avant/après, suffixe réversible et équivalence AST. L’identité repo/LAB constatée par les revues s’applique à leur édition avant ce formatage. Cette exception permet de reconstruire les octets exécutés et ne constitue ni nouveau run, ni changement du SHA CORE, ni changement du corps source. Le contrôle final des nouveaux fichiers doit passer ; sa validation et la revue finale sont consignées dans le reçu ultérieur, sans préjuger leur résultat ici.

## Marqueurs de cette édition avant publication

```text
CORE_HISTORICAL_REPLAY=PASS
CORE_STANDARD_FIXTURE_OFFLINE=PASS
CORE_VERTICAL_FIXTURE_OFFLINE=PASS
CORE_FULLSCREEN_FIXTURE_OFFLINE=PASS
CORE_HIDDEN_FIXTURE_OFFLINE=PASS
CORE_SAVED_PHASED_FIXTURE_OFFLINE=PASS
CORE_STANDARD_CONTROL=PARTIALLY_FEASIBLE
CORE_HORIZONTAL_RETURN=PARTIALLY_FEASIBLE
CORE_VERTICAL_CROSSING=PARTIALLY_FEASIBLE
CORE_HIDDEN_RETURN=PARTIALLY_FEASIBLE
CORE_SAVED_EPOCH=PARTIALLY_FEASIBLE
CORE_SAMPLED_DAMAGE=PARTIALLY_FEASIBLE
CORE_FULLSCREEN_COMPARISON=INCONCLUSIVE
CORE_NATIVE_ORDERING=INCONCLUSIVE
CORE_BUFFER_IDENTITY=NOT_PROVEN
CORE_ATOMIC_GENERATION=NOT_PROVEN
CORE_OOM_C_TESTS=PARTIALLY_FEASIBLE
CORE_OOM_ALTERNATIVES_REVIEW=ACCEPTED
CORE_PRODUCTION_OOM_POLICY=UNDECIDED
CORE_PRIVATE_ABI_PACKAGE=PARTIALLY_FEASIBLE
GPU_MODIFIER_AWARE_OFFLINE=INCONCLUSIVE
GPU_DCC_DESIGN_REVIEW=NOT_PROVEN
GPU_DCC_RUNTIME=NOT_RUN
GPU_WHOLE_FIELD_CAUSALITY=INCONCLUSIVE
CORE_FINAL_INDEPENDENT_REVIEW=NOT_PROVEN
CORE_DOCUMENTARY_PUBLICATION=PARTIAL
SWAYFX_MOSAIC_STEP20C_CORE_RECOVERY_OOM_AND_DCC_QUALIFICATION_BATCH_V1=PARTIALLY_ADVANCED
STEP20A=DONE
STEP20B=EXPERIMENTAL
STEP20C=NEXT
STEP20D_G=PLANNED
PRODUCTION_MULTI_OUTPUT=NOT_YET_SUPPORTED
PRODUCTION_AUTHORIZED=FALSE
```

La plus petite suite justifiée est la revue indépendante du diff documentaire/fixtures exact, puis la décision humaine sur un futur scope ciblé fullscreen équivalent ou OOM natif/observabilité GPU. Les deux jetons non consommés ne sont pas une autorisation de retry, ni une ouverture STEP20D.
