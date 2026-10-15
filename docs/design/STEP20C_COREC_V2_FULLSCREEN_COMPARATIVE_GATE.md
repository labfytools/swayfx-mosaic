# STEP20C — gate comparative fullscreen CORE-C V2

2026-10-15. Preuve expérimentale du nouveau ticket
`SWAYFX_MOSAIC_STEP20C_COREC_V2_FULLSCREEN_OOM_GLES_NATIVE_CLOSURE_BATCH_V1`.
Ce rapport complète la [décision historique V2](STEP20C_COREC_V2_INTEGRATION_DECISION.md)
sans réécrire P1/C8, leurs captures ni leurs budgets clos.
Les contrats canoniques gardent leur autorité.

```text
FULLSCREEN_PRISTINE_NEW=NOT_EXERCISED
FULLSCREEN_COREC_V2_NEW=NOT_RUN
FULLSCREEN_COMPARABILITY=NOT_EXERCISED
```

## Périmètre et provenance

Le [kit de suivi source-only](../../tooling/probes/step20c-corec-v2-followup/README.md)
dérive une fixture prospective, avec admission indépendante avant réservation.
La [revue de delta](evidence/step20c-native-closure/source-delta-review.json)
accepte les octets corrigés : 66 tests offline, zéro échec à cette version.
La première soumission avait trois findings corrigés ; cette acceptation ne
transforme pas la soumission initiale en succès.
Le [manifeste source V2](evidence/step20c-native-closure/source-manifest-v2.json)
a pour SHA256 `2e9fe75a48466fa1a9e3081137146d5cfffb35145c1749160e2c4f350bc6e5b7`
et source digest `f21ea193aedfada620c251f0cf6a22375fb993483905129208864e22e535b140`.

La [publication source](evidence/step20c-native-closure/source-publication.json)
au commit `c55373eab3c53132bf1157acc9cfc9edd451156e` précède les quatre
nouveaux runs non GPU. La [reprise depuis clone](evidence/step20c-native-closure/clone-validation.json)
vérifie 49/49 fichiers et leurs modes, 66 tests et six clients compilés.
Ces preuves source/offline ne qualifient pas la comparabilité runtime.

FS-P réutilise l'ELF pristine conservé, sans le reconstruire :
SHA256 `b7fa32116e3c42706b9b02da7df12f27e76d82dd253deb8bdec81519eed145f6`,
Build ID `ba9751c82e73d4043b7651354f20936d070c2227`, PID privé `3491656`.
Le LAB neuf est `/var/tmp/swayfx-mosaic-step20c-native-closure-qseaqp39`.
Le LAB parent `/var/tmp/swayfx-mosaic-corec-v2-i516p6po` demeure clos,
en lecture seule : ses 12 runs et 102 captures restent historiques.

## Arrêt observé et diagnostic borné

`graphics-runs/FS-P/run/fullscreen-not-exercised.json` donne exactement
`reason="actual fullscreen client executable"`. Le guard s'arrête avant la
création du groupe non-feuille et l'activation fullscreen ; aucune capture
output n'est acquise. Une fenêtre toplevel démarrée ne constitue pas le groupe
fullscreen demandé. Aucun débordement fullscreen nouveau n'est mesuré.
FS-C n'a aucune réservation : sa dépendance à un FS-P qualifié n'est pas
satisfaite. La comparaison pristine/CORE-C V2 est donc **NOT_EXERCISED**.

Le [probe contrôlé de dumpability](evidence/step20c-native-closure/fullscreen-dumpability-probe.json)
est hors campagne headless. Avec `dumpable=1`, `readlink(/proc/<PID>/exe)`
et `Path.resolve(strict=False)` trouvent l'exécutable ; avec `dumpable=0`,
readlink retourne `errno=13` et resolve conserve le chemin `/proc/<PID>/exe`
non résolu. C'est une explication cohérente et bornée du guard appliqué à un
client protégé par `PR_SET_DUMPABLE=0`. L'errno original FS-P n'a pas été
enregistré : **la causalité précise de cet arrêt reste NON_PROUVÉE**.
Ce probe ne démontre aucun défaut fullscreen natif du compositeur.
Il ne répare pas FS-P et n'autorise aucun retry.

## Budget et fermeture

| Élément | Observation conservée |
| --- | --- |
| Réservation FS-P | Une, consommée ; 0/12 captures output |
| Durée ledger | 6,097521916 s, de réservation à clôture |
| Durée outcome | 6,086245531041641 s, mesure interne du runner |
| Durée commande | 6,631161108 s, enveloppe `execution/FS-P-command.json` |
| Code commande runner | 1, avec statut scientifique NOT_EXERCISED |
| Cleanup scientifique / mécanique | PASS / PASS dans les reçus |
| Compositeur, clients, pointeur | Tous sortis à 0 ; aucun rescue ni watchdog |
| IPC terminal | `swaymsg` 1, fin de réponse/EOF ; distinct du compositeur 0 |
| Runtime privé | Supprimé après collecte |
| FS-C | NOT_RUN, non réservé, aucune capture |

Ces trois durées ont des bornes différentes ; elles ne sont pas interchangeables.
Le [ledger](evidence/step20c-native-closure/ledger.json) et le
[résumé runtime](evidence/step20c-native-closure/runtime-summary.json)
conservent la consommation réelle. L'espace inutilisé ne rembourse aucun jeton.

## Revue et limites

La [revue indépendante non GPU](evidence/step20c-native-closure/nongpu-results-review.json)
accepte cette restitution bornée ; son reçu original
`reviews/nongpu-results/receipt.json`, sous le LAB neuf, porte le SHA256
`a8a9ea6c9c1fab09687c1b43378d53d7add0eb421a9b2e626d60d59445578e86`.
Les bruts sont `graphics-runs/FS-P/run/{outcome.json,events.jsonl,owner.log,compositor.log}`
et `execution/FS-P-command.json`. Images, builds et logs lourds restent hors Git.

P1 historique reste informatif sur son groupe pristine 400/400 ; C8 historique
reste INCONCLUSIVE. Aucun succès offline ne ferme cette comparaison runtime.
Identité des buffers natifs, génération atomique, damage complet et GPU
completion restent **NOT_PROVEN**. Les autres cellules non exercées restent
**NOT TESTED**. STEP20A DONE, STEP20B EXPERIMENTAL, STEP20C NEXT,
STEP20D–G PLANNED ; multi-output production **NOT_YET_SUPPORTED**,
`PRODUCTION_AUTHORIZED=FALSE`.

La [migration/refocus](STEP20C_COREC_V2_MIGRATION_REFOCUS_GATE.md) et la
[complétion OOM](STEP20C_COREC_V2_NATIVE_OOM_COMPLETION.md) sont indépendantes
de cet arrêt. La [décision V4](STEP20C_COREC_V2_INTEGRATION_DECISION_V4.md)
doit conserver cette gate ouverte ; toute nouvelle preuve fullscreen exige
une autorisation distincte, sans réutilisation du jeton FS-P.
