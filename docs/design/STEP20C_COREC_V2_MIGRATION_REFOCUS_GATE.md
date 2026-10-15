# STEP20C — migration et refocus CORE-C V2

2026-10-15. Rapport expérimental du ticket
`SWAYFX_MOSAIC_STEP20C_COREC_V2_FULLSCREEN_OOM_GLES_NATIVE_CLOSURE_BATCH_V1`.
DY-C est **PARTIALLY_FEASIBLE**, avec niveau de preuve **SAMPLED_ONLY**.
Il apporte des mesures nouvelles après quatre mutations et ne réécrit pas le
C7 **INCONCLUSIVE** de la [décision historique V2](STEP20C_COREC_V2_INTEGRATION_DECISION.md).

## Sources, binaire et oracle

Le [kit source-only de suivi](../../tooling/probes/step20c-corec-v2-followup/README.md)
était publié au commit `c55373eab3c53132bf1157acc9cfc9edd451156e` avant
réservation. Le [manifeste source V2](evidence/step20c-native-closure/source-manifest-v2.json)
porte le SHA256 `2e9fe75a48466fa1a9e3081137146d5cfffb35145c1749160e2c4f350bc6e5b7`
et le digest `f21ea193aedfada620c251f0cf6a22375fb993483905129208864e22e535b140`.
La [revue de delta](evidence/step20c-native-closure/source-delta-review.json)
accepte la version corrigée et ses 66 tests ; les trois findings initiaux
restent conservés. La [publication](evidence/step20c-native-closure/source-publication.json)
et la [reprise depuis clone](evidence/step20c-native-closure/clone-validation.json)
documentent les 49/49 fichiers, modes, 66 tests et six clients compilés.

DY-C réutilise le CORE-C V2 conservé, sans nouveau build CORE : SHA256
`91f48aae2675331e0a2c60ec2fedf983745c521c75232c704a6516a4140801fb`,
Build ID `d5d304533f2c8db9d738365e9bd7f2c96779ef8d`, PID privé `3492726`.
Les identités runtime, mappings et fournisseur wlroots sont archivés dans le
LAB neuf `/var/tmp/swayfx-mosaic-step20c-native-closure-qseaqp39`.
Le fournisseur exact reste `/usr/lib/libwlroots-0.20.so`, SHA256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.

L'oracle recalcule depuis chaque snapshot IPC courant les largeurs, les bornes
de scroll et le refocus natif. Il conserve la distinction explicite
`IPC_PENDING_CANDIDATE; native generation NOT_OBSERVABLE` : l'IPC lu à cet
instant n'est pas une observation native de génération APPLIED. Les pixels
stabilisés et l'input livré corroborent séparément les états échantillonnés.
Sway garde arbre, focus, caméra, transactions, scène et IPC ; Row 0 emprunte
`workspace->tiling`.

## Quatre mutations effectivement mesurées

Le workspace conserve l'ID `6`, l'ordre `[8,9,10]` et le focus `10` ; chaque
cellule mesure 640 px, contenu total 1920 px, gap 0. La cellule focalisée
occupe les bornes logiques 1280..1920. Après migration, son refocus impose
1120 pour un viewport de 800 ; l'ancien attendu 800 de C7 omettait ce refocus.

| État après mutation | Output / viewport logique `[x,y,w,h]` | Scroll recalculé et observé | Nouveau point B global |
| --- | --- | ---: | --- |
| Resize 800→960 | H1 `[-960,0,960,600]` | 800 | `[-273,168]` |
| Retour 960→800 | H1 `[-800,0,800,600]` | 800 | `[-113,168]` |
| Migration H1→H2 | H2 `[0,0,800,600]` | 1120 | `[366,168]` |
| Retour H2→H1 | H1 `[-800,0,800,600]` | 1120 | `[-434,168]` |

Les quatre points B sont redérivés après invalidation des anciennes coordonnées.
Chaque point correspond au contenu peint sur l'output courant et reçoit une
vraie paire press/release, corroborée par le wire et les coordonnées locales
du pointeur. Les mêmes objets TOPLEVEL/A/B demeurent identifiés ; deux grabs
XDG réels sont comptés. Il ne s'agit pas d'une seule assertion synthétique
de l'oracle géométrique.

Les captures vérifient l'exclusion des couleurs popup hors viewport. H2 entière
est exacte contre sa référence aux deux resize et au retour H1. Pendant que
le workspace owner est réellement sur H2, la comparaison avec une H2 vide
est **NOT_APPLICABLE** ; sa présence y est attendue. Après fermeture, H2 est
exacte et aucun résidu A/B n'est observé sur H1 ni H2. Ces captures stables
ne couvrent pas toutes les frames de transition.

## Consommation, fermeture et revue

DY-C consomme une réservation, 16/16 captures output, quatre mutations,
six clics et deux grabs. Le ledger mesure **35,995476057 s** ; outcome mesure
35,98416800098494 s. Le [ledger](evidence/step20c-native-closure/ledger.json)
et le [résumé runtime](evidence/step20c-native-closure/runtime-summary.json)
conservent les compteurs. La fermeture réelle suit B→A→TOPLEVEL, avec
`EXIT error=0`, SHM 3/3 pour l'owner ; les autres clients ferment aussi normalement.
Tous les processus, compositeur et pointeur inclus, sortent à 0, sans rescue
ni watchdog ; cleanup scientifique/mécanique PASS et runtime privé supprimé.
L'IPC terminal `swaymsg=1` avec fin de réponse/EOF est enregistré séparément
du code compositeur 0.

La [revue indépendante non GPU](evidence/step20c-native-closure/nongpu-results-review.json)
recalcule les quatre caméras, les pixels et les livraisons wire ; elle accepte
la conclusion **SAMPLED_ONLY/PARTIALLY_FEASIBLE**. Le reçu original du LAB,
`reviews/nongpu-results/receipt.json`, a pour SHA256
`a8a9ea6c9c1fab09687c1b43378d53d7add0eb421a9b2e626d60d59445578e86`.
La [validation offline](evidence/step20c-native-closure/offline-validation.json)
et cette revue conservent les négatifs : quatre mutations de clamp hors
bornes et deux mutations de pixels échoués sont rejetées. Ce rejeu des
validateurs n'est pas une nouvelle exécution headless.

Les bruts sont `graphics-runs/DY-C/run/` : `dynamic-ownership.json`, snapshots
des quatre étapes, `events.jsonl`, `owner.log`, `compositor.log`, captures et
`dynamic-final-restoration.json`, plus `execution/DY-C-command.json`.
Les artefacts lourds restent hors Git. L'ancien LAB clos, ses 12 runs et
102 captures restent inchangés.

## Portée de la conclusion

```text
DYNAMIC_MIGRATION_APPLIED=PARTIALLY_FEASIBLE
DYNAMIC_INPUT_AFTER_MIGRATION=PARTIALLY_FEASIBLE
ATOMIC_GENERATION=NOT_PROVEN
COMPLETE_DAMAGE=NOT_PROVEN
NATIVE_BUFFER_IDENTITY=NOT_PROVEN
GPU_COMPLETION=NOT_PROVEN
```

Le marqueur APPLIED décrit la corroboration échantillonnée rendu/input ; aucune
génération native atomique n'est exposée par cette fixture. Les topologies ou
mutations hors de cette séquence restent **NOT TESTED**. STEP20A DONE,
STEP20B EXPERIMENTAL, STEP20C NEXT, STEP20D–G PLANNED ; multi-output production
**NOT_YET_SUPPORTED**, `PRODUCTION_AUTHORIZED=FALSE`.
La [gate fullscreen](STEP20C_COREC_V2_FULLSCREEN_COMPARATIVE_GATE.md) reste
non exercée ; la [complétion OOM](STEP20C_COREC_V2_NATIVE_OOM_COMPLETION.md)
et la [décision V4](STEP20C_COREC_V2_INTEGRATION_DECISION_V4.md) gardent leurs
périmètres distincts. Aucune conclusion GPU globale n'est tirée ici.
