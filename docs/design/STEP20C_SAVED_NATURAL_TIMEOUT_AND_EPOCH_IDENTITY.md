# STEP20C — saved natural timeout et identité d’épisode

> EXPERIMENTAL — édition du 2026-10-14. Ticket `SWAYFX_MOSAIC_STEP20C_SAVED_LIFETIME_INPUT_EPOCH_AND_GPU_CAUSALITY_BATCH_V1`. Revue finale indépendante du dossier complet : ACCEPTED / audit PASS pour la fidélité expérimentale ; publication PREPARED à cette édition, reçu final hors Git après push. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT YET SUPPORTED. Aucun contrat UX, package ou production adopté.

LAB désigne `/home/fy59/swayfx-mosaic-saved-input-gpu-pz4z428f`, laboratoire privé hors Git. Les chemins LAB sont des références locales, pas un kit distribué. Le [dossier V2](STEP20C_GATE_CLOSURE_DECISION_V2.md) fixe la provenance commune et les limites. Les rapports historiques restent immuables.

## Contrat effectivement exercé

Trois runs distincts C3/A/G ont démarré avec `-Dtxn-timeout=5000`, valeur réellement acceptée. Cette durée expérimentale de cinq secondes ne qualifie pas le timeout ordinaire de 200 ms. H1 est à (-800,0), H2 à (0,0), chacun 800×600, scale 1, transform normal ; le client H2 statique est #303038. Le trigger `gaps inner current set 30` modifie les géométries IPC et produit un configure wire réel. Le validateur utilise les géométries exposées et n’exige plus le champ absent `workspace.gaps.inner`.

ACK initial 30 puis held serial réellement lu 39, dimensions 636×573→636×513 : le serial n’est pas codé en dur. Le held PNG est antérieur au deadline. Une ligne native de timeout apparaît client encore vivant, sans ACK du serial tenu, avant fermeture explicite. H2 entier est RGB exact entre références, held, post-timeout et final ; H1 post-timeout est stable aux captures mesurées. Les trois propriétaires terminent normalement, code 0/error0.

## Instance native C3 et retrait naturel

L’instance cible 15 est créée après la commande, lock source 3→4, dessinée sur H1 puis `SD_REMOVE` et `SD_NODE_DESTROY` apparaissent après le timeout naturel et avant capture post-timeout. Le retrait est donc observé hors teardown. L’instance dérivée corrèle owner, parent/tree, adresse node, source et intervalle create→destroy ; elle ne représente aucune génération native ajoutée.

L’analyse complète `LAB/audit/C3-full-lifetime.json` accepte 23 instances et les réemplois d’adresse séquentiels non chevauchants. Elle conserve 12 signaux natifs distincts, conservés sous 24 rattachements ambigus et 17 records globaux release non ambigus. La release propre à la retraite saved cible est NOT OBSERVED ; aucune libération GPU complète ne s’en déduit. Les samples après destroy et instances simultanées à même adresse sont rejetés hors ligne.

A/G ont leurs propres wire, RGB et timeout, mais identité native saved/removal NOT OBSERVABLE. Leur conformité mesurée n’hérite pas du récit natif C3. Les événements SHM release, unlock CPU, buffer_destroy et GPU completion restent distincts.

## Statuts et limites

| Propriété | C3 | A | G |
| --- | --- | --- | --- |
| Configure tenu réel, held RGB et timeout naturel | PASS mesuré | PASS mesuré | PASS mesuré |
| Retrait naturel instance saved | OBSERVED | NOT OBSERVABLE | NOT OBSERVABLE |
| H2 RGB entier held/timeout/final | PASS mesuré | PASS mesuré | PASS mesuré |
| GPU completion/lifetime complet | NOT PROVEN | NOT PROVEN | NOT PROVEN |

measurements_pass=PASS ; les trois outcomes globaux runtime restent INCONCLUSIVE avec runner1/IPC terminal1, processus0 et cleanup mécanique PASS. Owner error0 ne suffit pas : reference/filler error32 au teardown compositeur gardent scientific_cleanup INCONCLUSIVE. Le verdict architectural reste PARTIALLY_FEASIBLE. Logging/listeners perturbent le temps et aucune neutralité n’est promise.

Preuves : `LAB/runs/saved-*/run/outcome.json`, `LAB/audit/initial-runtime-summary.json`, `LAB/audit/C3-full-lifetime.json`, manifestes liés au dossier V2. Aucun run supplémentaire ni nouveau build C3 n’est effectué par cette restitution.
