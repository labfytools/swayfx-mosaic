# STEP20C — complétion native OOM root et nested CORE-C V2

2026-10-15. Rapport expérimental du ticket
`SWAYFX_MOSAIC_STEP20C_COREC_V2_FULLSCREEN_OOM_GLES_NATIVE_CLOSURE_BATCH_V1`.
OM-ROOT et OM-NESTED sont **PARTIALLY_FEASIBLE**, avec disponibilité
**SAMPLED_ONLY**. Ils complètent deux oracles hiérarchiques nouveaux ; le
O1 **INCONCLUSIVE** de la [décision historique V2](STEP20C_COREC_V2_INTEGRATION_DECISION.md)
et son cleanup scientifique rejeté restent inchangés.

## Provenance et périmètre natif

Le [kit de suivi source-only](../../tooling/probes/step20c-corec-v2-followup/README.md)
a été publié au commit `c55373eab3c53132bf1157acc9cfc9edd451156e` avant
les runs. Le [manifeste V2](evidence/step20c-native-closure/source-manifest-v2.json)
porte le SHA256 `2e9fe75a48466fa1a9e3081137146d5cfffb35145c1749160e2c4f350bc6e5b7`,
digest `f21ea193aedfada620c251f0cf6a22375fb993483905129208864e22e535b140`.
La [revue de delta](evidence/step20c-native-closure/source-delta-review.json)
accepte les octets corrigés et 66 tests ; trois findings de la soumission
initiale ont été corrigés, sans effacer cette première revue.
Les reçus de [publication](evidence/step20c-native-closure/source-publication.json)
et de [clone](evidence/step20c-native-closure/clone-validation.json)
conservent 49/49 fichiers/modes, 66 tests et six clients compilés.

Les deux runs utilisent le **même ELF OOM natif V2 conservé**, sans rebuild :
SHA256 `6067946bd79ad6fd8da7669ab9b0b3bacfd2638f5d3d8382002b9118db20d835`,
Build ID `9bc3dc9055106b343c80a51ded111a382e98442d`.
L'injection est une panne sidecar ciblée par PID, nonce et rôle, pas un
épuisement global de mémoire. Le fournisseur partagé exact est
`/usr/lib/libwlroots-0.20.so`, SHA256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
Le LAB neuf `/var/tmp/swayfx-mosaic-step20c-native-closure-qseaqp39` conserve
les observations ; le LAB parent clos reste en lecture seule, 12 runs et
102 captures historiques inchangés.

## Première et deuxième réservations effectivement ciblées

| Mesure | OM-ROOT | OM-NESTED |
| --- | --- | --- |
| PID compositeur | 3494614 | 3497491 |
| Nonce unique | `0a825259ea7740c5a7704f149dfa0649` | `39b4767924344003ad80fb9b87da4e20` |
| Rôle échoué | `root_popup` A | `nested_popup` B |
| matched / failures | 1 / 1 | 1 / 1 |
| successes avant panne | 0 | 1, root A |
| initialized / listeners / published du chemin échoué | 0 / 0 / 0 | 0 / 0 / 0 |
| children du parent existant | 0 | 1 |
| Résultat caller lié au même xdg/parent/PID | NULL | NULL |
| Mapping client du rôle échoué | A jamais MAP ; B non créé | B jamais MAP ; A déjà MAP |
| Ordre effectif de destruction | A→TOPLEVEL | B→A→TOPLEVEL |
| Fermeture owner | Normale, `EXIT error=0`, SHM 1/1 | Normale, `EXIT error=0`, SHM 2/2 |
| `no_memory` disconnect | NOT_OBSERVED | NOT_OBSERVED |

Le compteur `children=1` nested désigne les enfants du **parent existant** ;
il ne décrit pas un nœud échoué partiellement publié. Le root A réussit et
est mappé avant l'injection B ; le xdg du root natif correspond au
`xdg_parent` du B échoué. Les lignes natives de factory et de résultat caller
sont corrélées. Les compteurs n'autorisent pas à substituer un schéma IPC
popup inexistant à cette preuve source/native.

Avant le clic extérieur du voisin, A reste peint et reçoit réellement une
paire bouton droit press/release au point global `[-215,108]` dans OM-NESTED,
corroborée par le wire et les coordonnées locales. L'oracle root ne réclame
pas un B qui n'a jamais été créé. L'oracle nested exige le root préalable et
la séquence B→A→TOPLEVEL. Les deux clients ferment normalement : aucun code
d'erreur protocolaire `no_memory` n'est inventé à partir du NULL natif.

## Disponibilité archivée avant cleanup et pixels

Chaque run sauvegarde **avant cleanup** l'identité du même PID : `/proc/exe`,
SHA ELF, Build ID, mappings et wlroots exact ; les réponses `get_tree` et
`get_outputs` passent par le socket privé explicite. Le certificat
`oom-availability-live.json` conserve aussi une vraie paire bouton du voisin,
avec exclusivité et fraîcheur de livraison wire. Cette archive post-injection
est plus précise que les maps de startup seules d'O1 ; elle ne prouve pas
une disponibilité générale sous toutes les pannes OOM.

H1 est à `[-800,0,800,600]`, H2 à `[0,0,800,600]`, scale 1, transform normal.
Les huit captures de chaque run comprennent H2 référence entière et les
échantillons pré/post/final : H2 est exacte à chaque comparaison. Aucune
couleur du rôle échoué n'est observée sur H1/H2 ; les captures finales après
fermeture ne contiennent aucune couleur A/B. Ces égalités stables n'établissent
ni toutes les frames damage ni une identité native de buffer présenté.

La [revue indépendante non GPU](evidence/step20c-native-closure/nongpu-results-review.json)
rejoue les validateurs sur les bruts, y compris les vrais événements wire et
les pixels RGB exacts. Deux contre-exemples de pixels échoués et quatre
mutations hors bornes sont rejetés ; la
[validation offline](evidence/step20c-native-closure/offline-validation.json)
en conserve le périmètre. Le reçu original de revue du LAB,
`reviews/nongpu-results/receipt.json`, porte le SHA256
`a8a9ea6c9c1fab09687c1b43378d53d7add0eb421a9b2e626d60d59445578e86`.

## Budget et terminaison

| Run | Captures output / plafond nommé | Durée ledger | Durée outcome |
| --- | --- | ---: | ---: |
| OM-ROOT | 8/10 | 17,761603037 s | 17,750482999021187 s |
| OM-NESTED | 8/10 | 20,408873591 s | 20,39799604000291 s |

Chacun consomme une seule réservation et un hook ciblé, sans retry. Le
[ledger](evidence/step20c-native-closure/ledger.json) et le
[résumé runtime](evidence/step20c-native-closure/runtime-summary.json)
séparent les codes : clients, pointeur et compositeur tous 0 ; cleanup
scientifique et mécanique PASS ; aucun rescue ni watchdog ; runtimes privés
supprimés après collecte. `swaymsg` terminal 1 avec fin de réponse/EOF demeure
distinct du compositeur 0. Les quatre runs non GPU totalisent 32 captures
et quatre réservations ; cette somme ne qualifie aucune campagne GPU.

Les bruts sont sous `graphics-runs/{OM-ROOT,OM-NESTED}/run/` : mesures natives,
`oom-measurements.json`, certificats `oom-availability-*`, snapshots IPC,
`oom-rootA-post-input.json`, événements, logs et captures ; les enveloppes
commandes sont `execution/{OM-ROOT,OM-NESTED}-command.json`. Les artefacts
lourds restent dans le LAB hors Git.

## Politique encore indécise et limites

| Option | Propriété / coût à décider | État de preuve |
| --- | --- | --- |
| A abort | Fail-closed par arrêt du processus ; disponibilité sacrifiée | Option source historique, recovery non qualifié |
| B bool + masque | Recovery et masque fail-closed à qualifier ; callers/setters à traiter | Pas de nouvelle qualification native ici |
| C préallocation | Réservation avant init/publication, NULL en panne ; setter sans allocation | Root/nested ciblés PARTIALLY_FEASIBLE, disponibilité SAMPLED_ONLY |

La réservation C coûte un sidecar de 64 octets par arbre de factory, y compris
inactif/non Mosaic, plus overhead allocateur **NOT_MEASURED** ; lookup linéaire,
coût global et performance **NOT_MEASURED**. Cette disponibilité ciblée ne
choisit pas la politique production. `OOM_PRODUCTION_POLICY=UNDECIDED`.
L'absence universelle de stale listeners, un état popup partiel via IPC sans
schéma natif, la génération atomique, le damage complet, l'identité des buffers
natifs et GPU completion restent **NOT_PROVEN**. Les autres pannes et matrices
non exécutées restent **NOT TESTED**.

Les licences restent **LEGAL_NOT_APPROVED** ; responsables release, sécurité
et maintenance SceneFX statique **UNASSIGNED**. Aucun résultat de ces injections
ne décide une UX popup/offscreen. STEP20A DONE, STEP20B EXPERIMENTAL,
STEP20C NEXT, STEP20D–G PLANNED ; production multi-output
**NOT_YET_SUPPORTED**, `PRODUCTION_AUTHORIZED=FALSE`.

La [gate fullscreen](STEP20C_COREC_V2_FULLSCREEN_COMPARATIVE_GATE.md), la
[migration/refocus](STEP20C_COREC_V2_MIGRATION_REFOCUS_GATE.md) et la
[décision V4](STEP20C_COREC_V2_INTEGRATION_DECISION_V4.md) gardent les
conclusions séparées. Aucune readiness production ni conclusion GPU globale
n'est déduite de cette complétion native bornée.
