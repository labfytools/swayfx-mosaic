# STEP20C — lifecycle ciblé des saved buffers

> EXPERIMENTAL — édition du 2026-10-14, clôture documentaire des quatorze runs ciblés, diagnostic C3 inclus. Revue finale indépendante : ACCEPTED, audit PASS pour la fidélité de l’évidence expérimentale. Publication documentaire autorisée et préparée, non exécutée à cette édition. Le diagnostic C3 est exécuté : résultat INCONCLUSIVE, observations natives partielles sans transfert à A/G. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED. Multi-output de production : NOT YET SUPPORTED. Aucune intégration, installation ou décision UX.

L’autorité brute est le LAB privé `/home/fy59/swayfx-mosaic-targeted-7gge6h8b` ; HIST désigne `/home/fy59/swayfx-mosaic-overnight-mcolx0gq`. Les chemins LAB/HIST sont des artefacts externes locaux, pas des fichiers distribués. Le [rapport de clôture](STEP20C_TARGETED_CLOSURE_DECISION.md) donne les identités exactes, la matrice des quatorze runs et les limites. Les sources de [fixture ciblé](../../tooling/probes/step20c-targeted/README.md) restent des entrées expérimentales ; elles n’ajoutent aucune dépendance de production. Les rapports historiques et leurs verdicts restent inchangés.

## Configure réellement obtenu, gate incomplet

Deux runs distincts, `saved-A` et `saved-G`, ont chacun deux PNG de référence H2. La demande réelle `gaps inner current set 30` provoque un nouveau configure serial 39 après ACK 30 : 636×573 devient 636×513. Le client annonce HELD, aucun ACK 39 n’est enregistré. Le validateur partagé puis son replay confirment la propriété `HELD_WIRE_VALIDATED` ; le trigger de configure est FEASIBLE pour les données observées.

La fixture s’arrête néanmoins sur `Ambiguous: same ws1 owner and requested runtime gaps`, car elle exige le champ workspace IPC `gaps` absent. L’audit source confirme l’action runtime et les deux argv contiennent `-Dtxn-timeout=2500`. Aucun timeout naturel n’est observé : la connexion est détruite par le teardown du compositeur, et le client écrit `EXIT ... mapped=1 held=1 error=32`, malgré son code de processus 0. Le `cleanup_pass=true` mécanique ne devient donc pas scientific cleanup PASS. Résultat runtime, scientific cleanup et campagne : **INCONCLUSIVE**. Images pendant hold/timeout, normal owner close et identité native saved-node/render : **NOT EXERCISED / NOT OBSERVABLE**.

## Identités et propriété native

L’audit `parent/native-lifetime-audit.json` est **SOURCE_AUDIT_ONLY**. `view_save_buffer_iterator` crée un autre `wlr_scene_buffer` sous l’arbre saved, copie destination/source-box/transform et référence le buffer de la scène live. SceneFX déverrouille l’ancienne référence, invalide la texture cached et locke le nouveau `wlr_buffer`. Le saved tree est frère de content_tree ; retirer les saved nodes détruit leur arbre et réactive le live. La destruction d’un scene buffer libère sa référence. Ces chemins source ne sont pas une preuve de release GPU au runtime.

Il faut distinguer SHM client, wl_buffer release client, nœud saved natif, texture/cache, output-state buffer, commit/present et fin GPU. Ni A ni G n’offrent les identités natives saved/locks/releases recherchées. Les traces d’un autre binaire historique ne leur sont pas transférées. Lifetime GPU, références exhaustives, commit rejeté et cohérence atomique restent **NOT PROVEN**.

## C3 réellement consommé — observation native partielle

C3 (`saved-diagnostic-A`) utilise un troisième binaire privé avec un seul
build Mosaic stage1, sans nouveau build SceneFX. LAB
`diagnostic/build-stage.json` lie le SHA
`9c0dc0e94ccc7fcbd7a6cddf14e90f1bb7b7bf385a0740e85ec7d0e1c1c1e705`
et build ID `67a4bcb6a37e8ec691a0da5099d12275429a7076`.
LAB `parent/c3-observations.json` et `parent/run-summary-final.json` enregistrent
la tentative consommée, sans réparation de fixture ni relance.

Le runtime et la mesure sont **INCONCLUSIVE**, runner exit1 : le bounded wait
expire après une durée totale de run de 3,682 s. Ce stop n’est **pas** le timeout
naturel d’une transaction. Le prédicat figé `saved_identity` rejette
`unique unreused saved node` : l’adresse de nœud est réellement réutilisée.
Une première tree owner 10 précède la commande gaps runtime ; une nouvelle tree
owner 10 est créée après cette commande. Exiger une adresse globalement unique
était trop strict pour cette lifetime ; l’analyse hors ligne ne répare ni
requalifie le prédicat original.

Après gaps, le wire retient configure 39 HELD sans ACK,636×573→636×513.
`SD_CREATE` observe owner 10, tree `0x55f011797c80`, saved node
`0x55f011792290`, source buffer `0x55f01170eae0`, destination 636×573 et
locks 3→4. Un vrai draw H1 de ce nœud/source et un sample natif sont retenus :
bbox globale[-318,25,636,573], intersection héritée[-318,25,318,573], clip
viewport global[-800,0,800,600] ; le draw output-local va de(482,25) à(800,598).
Ce sont des observations de création/rendu de saved node, distinctes des PNG
client ou d’une identité de buffer réellement présenté.

`SD_NODE_DESTROY`, `SD_RELEASE` à locks 0 et `SD_BUFFER_DESTROY` apparaissent
uniquement pendant le teardown après l’arrêt anticipé. Le client owner termine
`EXIT error=32` malgré code de processus 0. Natural transaction timeout,
normal owner close, PNG held puis live et contrôle H2 pendant hold :
**NOT EXERCISED**. Scientific cleanup **INCONCLUSIVE**, GPU completion et
identité source-SHM/output **NOT PROVEN**. Processus0/reaped/runtime_removed
et IPC terminal1 restent enregistrés séparément.

Le découpage offline create→next destroy est descriptif, avec source pointer
et ancestor tree ; il n’invente ni génération native ni identité valable à
toute réutilisation d’adresse. **SAVED_NODE_LIFECYCLE : partiellement observé
(création/rendu/teardown)** ; clipping **INCONCLUSIVE**, sans PNG held H2 ;
native GPU lifetime **NOT PROVEN**. Aucun résultat C3 ne se transfère à A/G.
La revue finale indépendante est **ACCEPTED**, audit PASS pour la fidélité du dossier expérimental. La publication documentaire est autorisée et préparée, non exécutée à cette édition.

Preuves A/G : LAB `runs/saved-{A,G}/run/`, `parent/run-summary.json`,
`parent/native-lifetime-audit.json`, `reviews/runtime-validation-13.json`.
Preuves C3 : LAB `runs/saved-diagnostic-A/run/`, `parent/c3-observations.json`,
`parent/run-summary-final.json`. Total campagne final 14 runs/125 PNG/520 événements ;
les treize runs initiaux et leurs preuves restent intacts.
