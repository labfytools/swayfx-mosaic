# SWAYFX_MOSAIC_STEP20C_TARGETED_CLOSURE_DECISION

> EXPERIMENTAL — édition du 2026-10-14, clôture documentaire des quatorze runs ciblés, diagnostic C3 inclus. Revue finale indépendante : ACCEPTED, audit PASS pour la fidélité de l’évidence expérimentale. Publication documentaire autorisée et préparée, non exécutée à cette édition. C3 exécuté : INCONCLUSIVE, observations natives partielles sans transfert à A/G. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED. Multi-output de production : NOT YET SUPPORTED. Aucune intégration, installation ou décision UX.

## Recommandation et autorité

**PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE** reste la recommandation, non une décision appliquée. L’évidence ciblée avance plusieurs cellules privées, mais les gates saved/lifetime, génération/damage, restauration GPU, input temporel, neutralité, ABI maintenue et distribution restent ouverts. L’état scientifique global reste **PARTIALLY_ADVANCED** ; aucun READY/PRODUCTION_READY n’est revendiqué.

LAB = `/home/fy59/swayfx-mosaic-targeted-7gge6h8b` ; HIST = `/home/fy59/swayfx-mosaic-overnight-mcolx0gq`, lecture seule. Ces répertoires privés contiennent images, logs, maps, binaires, archives et reçus non distribués. Les [sources ciblées](../../tooling/probes/step20c-targeted/README.md) sont un protocole scellé, pas un compte rendu post-exécution. Les résultats sont consignés ici, séparément des sources figées.

Le closeout historique SHA `dba268a6aa415bd07c26371ec1ba9e66e4b54b5b51bd24ae05bd1d281bd27a3a` et son manifeste primaire `cdf034e1f8466a9ae8a0e0a33aa8d0d0195273f0d1bc782667b50c3bcf682505` ont été revalidés :6138 entrées PASS, 18 runs uniques/196 captures. Le résultat historique reste PARTIALLY_ADVANCED ; aucun rapport ancien n’est corrigé rétroactivement. Le point de départ documentaire est main `30dc3182`, initialement identique à origin/github.

## Identités exactes

| Binaire | SHA256 exécutable | Build ID |
| --- | --- | --- |
| A annoté | `979dcd95ab43fa1e465d6e9d262485b73d186cedacd0f957059dd24f482ce6f4` | `fabfeb823754a0f5107f83eb077323ad17ddedd1` |
| G release-shape | `8063478b2d5948da3eb8b1a329978882dc1d045cf36932cc2145a78af20ba76a` | `83896fdb36f3fd21522becec0e8c5219e15f4b8e` |
| pristine | `8ac865481bc0487344210cd0e16d8e6c7655b29db887cd58ddc11b0ca22fe494` | `298a9626b331139ff2f081ade9c4efdde2d4fb19` |

Chemins réels : A `HIST/stage-static/usr/bin/swayfx-mosaic`, G `HIST/release-shape/stage-static/usr/bin/swayfx-mosaic`, pristine `/home/fy59/swayfx-mosaic-optimized-edge-a55yjb8n/pristine-build/sway/sway`. Aucun binaire n’a été reconstruit pour les treize runs. Chaque run retient argv et `proc-maps.txt`, hash du binaire et bibliothèque wlroots exacte. Aucun objet SceneFX partagé distinct n’est revendiqué. C3 possède un build/stage distinct, LAB `diagnostic/build-stage.json`, SHA `9c0dc0e94ccc7fcbd7a6cddf14e90f1bb7b7bf385a0740e85ec7d0e1c1c1e705`, build ID `67a4bcb6a37e8ec691a0da5099d12275429a7076`. Son runtime est INCONCLUSIVE après rejet du prédicat d’adresse unique ; création/rendu/teardown sont partiellement observés, sans transfert à A/G.

## Matrice unique des quatorze runs

Tous les outcomes runtime bruts sont **INCONCLUSIVE**, terminal IPC exit1, tous les codes des processus enregistrés0, reaped/runtime_removed vrais, aucun rescue/watchdog. Ces faits mécaniques ne remplacent pas le scientific cleanup. Les comptes PNG proviennent du registre réel, y compris les captures réservées sur les runs interrompus. `native` = commits/paired/missing ; `budget` = captures réservées/plafond local, puis nombre total de réservations d’action. Tous les détails et hashes d’artefacts proviennent de LAB `parent/run-summary.json` (treize initiaux), les plafonds et actions de `budget.json`. Le résumé final et C3 sont LAB `parent/run-summary-final.json` et `parent/c3-observations.json`.

| Run / binaire | PNG / budget / actions | Géométrie et grabs | Input observé | native | Mesure ; architecture | Scientific cleanup |
| --- | --- | --- | ---: | --- | --- | --- |
| `FX-A` / A | 16 / 16/16 / 61 | H1 -800,800×600 ; 0 grab | 0 | 81/77/4 | PARTIALLY_FEASIBLE ; PARTIALLY_FEASIBLE | PASS |
| `FX-G` / G | 16 / 16/16 / 61 | H1 -800,800×600 ; 0 grab | 0 | 80/76/4 | PARTIALLY_FEASIBLE ; PARTIALLY_FEASIBLE | PASS |
| `FX-pristine` / pristine | 16 / 16/16 / 57 | H1 -800,800×600 ; 0 grab | 0 | 0/0/0 | PARTIALLY_FEASIBLE ; PARTIALLY_FEASIBLE | PASS |
| `G-R90-G` / G | 9 / 9/10 / 35 | H1 -800 ; R90 physique750×1000 scale1,25 ; 35/44 | 4 | 80/78/2 | PASS ; FEASIBLE | PASS |
| `G-dynamic-G` / G | 14 / 14/14 / 50 | H1 -800,800×600→960→800 ; H1/H2/H1 ; 42/51 | 6 | 119/113/6 | PASS ; PARTIALLY_FEASIBLE | PASS |
| `G-hidden-G` / G | 12 / 12/12 / 45 | H1 -800,800×600 ; 61/70 | 4 | 91/89/2 | PASS ; FEASIBLE | PASS |
| `input-A` / A | 5 / 5/12 / 26 | H1 -800,800×600 ; 0 grab | 3 | 58/56/2 | INCONCLUSIVE ; PARTIALLY_FEASIBLE | INCONCLUSIVE |
| `input-G` / G | 5 / 5/12 / 26 | H1 -800,800×600 ; 0 grab | 3 | 59/57/2 | INCONCLUSIVE ; PARTIALLY_FEASIBLE | INCONCLUSIVE |
| `input-pristine` / pristine | 8 / 8/12 / 32 | H1 -800,800×600 ; 0 grab | 4 | 0/0/0 | INCONCLUSIVE ; FEASIBLE standard (PI NOT OBSERVABLE) | PASS |
| `saved-A` / A | 2 / 2/10 / 19 | H1 -800,800×600 ; 0 grab | 0 | 31/29/2 | INCONCLUSIVE ; INCONCLUSIVE | INCONCLUSIVE (error32 après teardown) |
| `saved-G` / G | 2 / 2/10 / 19 | H1 -800,800×600 ; 0 grab | 0 | 31/29/2 | INCONCLUSIVE ; INCONCLUSIVE | INCONCLUSIVE (error32 après teardown) |
| `scale-A` / A | 9 / 9/12 / 35 | H1 -800 ; physique1000×750 scale1,25 ; 35/44 | 4 | 79/77/2 | PASS ; FEASIBLE | PASS |
| `scale-G` / G | 9 / 9/12 / 35 | H1 -800 ; physique1000×750 scale1,25 ; 35/44 | 4 | 79/77/2 | PASS ; FEASIBLE | PASS |
| `saved-diagnostic-A` / C3 | 2 / 2/10 / 19 | H1 -800,800×600 ; 0 grab ; HELD39 | 0 | 33/31/2 | INCONCLUSIVE ; lifecycle partiellement observé, clipping INCONCLUSIVE | INCONCLUSIVE (error32 après teardown) |

Total : **14 runs uniques, 125 captures, 520 événements réservés**. Les treize runs initiaux représentent 13/123/501, le C3 consommé ajoute 1/2/19. Campagnes scale 2/18, saved 3/6, FX 3/48, input 3/18, G 3/35. Aucun retry/remboursement ; le budget accepte au plus 14 tentatives et 174 PNG, le diagnostic a été consommé sous son binding séparé. La durée de mesure réelle va de 3,045 à 9,172 s, watchdog 143 s/cleanup 150 s ; elle ne constitue pas une couverture temporelle exhaustive. Les chemins individuels de runtime des treize runs initiaux n’ont pas été conservés ; C3 retient son runtime privé `/tmp/m20-75jrtuws` et ses sockets dans son reçu ; aucun PID probe ni socket LAB ou `/tmp/m20-*` restant n’a été trouvé, et les répertoires temporaires non attribuables restent intacts.

Le validateur runtime indépendant en lecture seule, LAB `reviews/runtime-validation-13.{md,json}`, rapporte **PASS 681 checks** sur les treize runs initiaux, 469 bindings d’entrée/441 hashes d’artefacts et cinq commandes readelf. SHA script `97dc45cd4b606e1208c0a7671937c9b8a21c96425f45f94f165124ccb6443647`. Freeze `ba30fb2298b4ed9b11e807741541ce99b337e00d6086840ecac9714a55f927d5`, revue fixture `5843196534ab88188f0c9b942b4c28a7bd49b35fea9da82b19215125c3442747`. Validation des observations ne signifie pas PASS runtime ni clôture de production.

## Résultats discriminants et limites

- [Scale/popups](STEP20C_TARGETED_SCALE_AND_POPUP_GATE.md) : chacun A/G possède deux vrais grabs, A et B franchissant x=0, B visible délivré, B interdit non délivré/dismissal, H2 entier exact. Association source bornée ; pas de join natif host/owner ID ni retour standard dans cette allocation.
- [Saved lifecycle](STEP20C_TARGETED_SAVED_BUFFER_LIFECYCLE.md) : configure 39 tenu après ACK 30,636×573→636×513 prouvé, mais fixture champ IPC absent ; timeout/held PNG/native saved IDs/normal close non exercés. `error32` au teardown interdit scientific cleanup PASS. C3 distinct observe création/rendu/teardown partiels mais rejet d’identité par réutilisation d’adresse ; clipping INCONCLUSIVE.
- [Effets/cache](STEP20C_TARGETED_EFFECTS_CACHE_DIAGNOSIS.md) : classique réellement filtrant ; whole-H1 retour FAIL 37252 pristine/34323 A/G, max 6. Les seize images A/G RGB exactes ; modèle history 68969/fresh 0 diverge du signe natif. Causalité GPU INCONCLUSIVE.
- [Input/ordre](STEP20C_TARGETED_INPUT_NATIVE_ORDERING.md) : contrôle pristine terminé ; A/G caméra change durant troisième clic, coordonnées wire égales à dernière origine native. Suite input arrêtée ; aucune panne produit ou atomicité démontrée.821 commits/789 paired/32 missing au total final (treize initiaux : 788/758/30), pas d’identité buffer/pixels commune.
- [G/ABI/package](STEP20C_RELEASE_SHAPE_EXTENDED_MATRIX.md) : nouveaux runs dynamiques/caché/R90 propres à G ; neutralité résiduelle INCONCLUSIVE. Stage privé exact cinq fichiers, metadata/source verification/patch checks PASS ; full package build NOT RUN, droit de distribution HUMAN_REVIEW_REQUIRED.

## C3 consommé, stop fixture conservé

Le C3 dure3,682s et s’arrête sur bounded wait, jamais sur timeout naturel de
transaction. Le prédicat frozen `unique unreused saved node` rejette une adresse
réutilisée : une tree owner 10 antérieure à gaps puis une nouvelle tree owner 10
après gaps. Le held39 reste réel. La nouvelle création source-buffer/saved-node,
locks 3→4, draw H1/intersection héritée puis destruction/release/destroy au
teardown sont observés. Le découpage offline create→next destroy est descriptif,
sans génération native inventée. Owner EXIT error32/code0 ; scientific cleanup
INCONCLUSIVE, aucune capture held/live ou H2 held, normal close/timeout
NOT EXERCISED. Voir le [détail saved lifecycle](STEP20C_TARGETED_SAVED_BUFFER_LIFECYCLE.md).
Clipping INCONCLUSIVE, lifetime GPU NOT PROVEN, aucun transfert à A/G.

## Damage hors ligne, observation bornée

LAB `parent/damage-envelopes.json` rapporte 99 comparaisons de captures
adjacentes par output sur les treize runs initiaux, RGB entier sans masque : 18 différences contenues dans
l’union d’enveloppes physiques A ; 79 NOT OBSERVABLE (trace absente ou intervalle
vide) ;deux changements de dimensions NOT COMPARABLE. Le source audit distingue
les damage extents, `scene_output_damage`, le buffer soumis et le present natif.
Les unions couvrent un intervalle large entre captures ; elles ne démontrent ni
région exacte pixman/minimale, ni chaque frame, ni contenu du buffer présenté.
Résultat PARTIALLY_FEASIBLE pour l’observation, complete damage NOT PROVEN.

## Risques et conditions de clôture

La priorité exprime le risque de qualification, pas une panne prouvée. Pour chaque ligne, la source et le reproducer sont les artefacts privés et sources hashées de la campagne ; aucun problème sans preuve n’est classé P0.

| ID / priorité | Observation et source reproductible | Binaire / conditions | Impact | Reste à faire et dépendance de clôture / décision humaine |
| --- | --- | --- | --- | --- |
| R00 / P0 | aucun défaut P0 clip/input démontré ; runtime-validation13 | A/G, échantillons headless | absence de preuve universelle | conserver gates ouverts ; aucune adoption automatique |
| R01 / P1 | whole-H1 RGB FAIL ; FX diagnosis/source/dumps | pristine/A/G, ABA optimisé | restauration GPU non qualifiée | readback natif borné et interprétation revue ; nouveau budget GPU autorisé |
| R02 / P1 | error32 ; saved logs/native-lifetime audit | A/G, held39, teardown avant timeout | lifetime saved/GPU non prouvée | C3 distinct : création/rendu/teardown partiels, prédicat adresse unique rejeté ; timeout/held pixels/normal close et lifetime GPU non clos, revue sans transfert |
| R03 / P1 | commits/paired/missing ; native audit | A/G, headless | génération atomique/damage exhaustif non prouvés | fenêtre discriminante, buffers/pixels/hit liés, tous frames ; contrat temporel à décider |
| R04 / P1 | origine change durant click ; input logs | A/G, fullrestore/focus | fixture temporel et couverture input incomplets | mesurer mutation pendant livraison et suite camera/layout ; nouvel essai autorisé |
| R05 / P1 | saved/input G partiels ; propres outcomes | G SHA exact | couverture release-shape incomplète | exact-SHA saved/lifetime/input, autres chemins pertinents ; pas de PASS A transféré |
| R06 / P2 | PI loops/listeners/logs et FBO bind-before-failed ; ABI audit | G versus pristine | neutralité timing/failure indéterminée | audit/retrait privé mesuré et requalification ; budget distinct |
| R07 / P2 |85 overlaps/34 bindings, 17 structs/six offsets/121 headers | paire SceneFX 0,5/wlroots 0,20,2 | maintenance/semantics ABI liées à paire | requalifier chaque changement ; responsable release/security à désigner |
| R08 / P2 | notices895/894 entrées et stage5 ; package/ABI audit | A/G, copies privées | incorporation exacte/legal/package build non clos | exact preprocessing/archive extraction, full package build et revue juridique humaine |
| R09 / P2 | aucun nom/SLA ; contrat privé existant | futur artefact distribué | suivi fixes non attribué | nominations release/security et politique publication distincte |
| R10 / P2 | IPC terminal1 / runtime paths individuels absents ; validation13 | les 14 runs | résultat runtime et attribution cleanup bornés | transport robuste/receipt paths dans futur fixture ; préserver raw exit1 |
| R11 / P3 | matrices physiques plus larges absentes ; dossiers historiques | autres backends/scales/transformations | généralisation non qualifiée | cellules pertinentes explicites NOT TESTED ; autorisation/budget séparés |

Popup offscreen hide/dismiss/reposition et click-through sous grab sont des décisions humaines encore ouvertes. La maintenance exacte de SceneFX, ses notices et la paire wlroots ont un contrat privé approuvé, mais aucun maintainer nommé ni avis juridique final. La première tranche de production éventuelle exige d’abord décisions, fermeture des gates pertinents et contrats canoniques Architecture/UX/Packaging/Upstream/Development, puis delta opt-in native clip/owner guard revu avec restauration standard workspace-local. Elle n’est pas autorisée ici et ne comprend aucun STEP20D.

La [provenance publique compacte](../../tooling/probes/step20c-targeted-results/RESULTS.json)
est présente et vérifiée. Le [README des résultats](../../tooling/probes/step20c-targeted-results/README.md)
explique sa portée ; le [manifeste d’artefacts](../../tooling/probes/step20c-targeted-results/ARTIFACTS.json)
lie460 fichiers retenus. Ils comprennent125 captures output et trois PNG sources
de markers, donc128 fichiers PNG ; les trois sources ne sont pas facturées comme
captures output. Les plafonds de captures ne sont pas atteints. Les deux PNG C3
sont des références H2, sans preuve de damage pendant hold ; les99 transitions
de damage restent limitées aux treize runs initiaux.

## Revue indépendante et publication préparée

L’unique revue finale indépendante est **ACCEPTED**, audit PASS pour la fidélité
et le gel de l’évidence expérimentale : zéro BLOCKING, un NON_BLOCKING (N-01,
deux coquilles corrigées ici) et trois FUTURE_SCOPE. Elle rapporte43 tests hors
ligne PASS (14 core, six FX,23 C3) et22 mutations additionnelles rejetées.
Cette acceptation ne change aucun résultat runtime, scientifique ou de production.
Rapport privé : `/home/fy59/swayfx-mosaic-targeted-7gge6h8b/reviews/targeted-final-review.md`,
SHA256 `73f06404ccfaa985cd6e279e606debeb8899bd1dd9079c88fdf5a01be98354ec`.
Reçu privé : `/home/fy59/swayfx-mosaic-targeted-7gge6h8b/reviews/targeted-final-review.json`,
SHA256 `28f868a0d956e70290db0515f59404e9f930e7180a89e326bcabda9ff6ea47ae`.
Le [supplément public de revue](../../tooling/probes/step20c-targeted-results/REVIEW.json)
lie cette acceptation et les limites de sa finalisation administrative ; il est
créé séparément par le parent. Les snapshots pré-review et leurs manifestes sont conservés.

La publication du dossier est autorisée et préparée, mais **non exécutée à cette
édition**. L’état observé et les refs finales origin/github appartiendront au
closeout privé LAB et à la restitution finale ; aucun SHA futur ou PASS de
publication n’est inventé ici. Publication d’évidence et intégration/distribution
production restent des actes distincts.

## Marqueurs de clôture à cette édition

| Marqueur | État et portée exacte |
| --- | --- |
| HISTORICAL_REPLAY | PASS, 6138 entrées/18 runs196 PNG, historique immuable |
| FIXTURE_REVIEW | PASS/ACCEPTED indépendant pour les bytes des treize initiaux ; C3 possède son binding et sa revue préflight distincts |
| OFFLINE_CORE | PASS 14 tests `offline-final.json` ; runtime NOT RUN par ces tests |
| OFFLINE_FX | PASS 6 tests `fx-offline.json` ; runtime NOT RUN par ces tests |
| TARGETED_REPLAY | PASS `replay-final.json`, données historiques réelles ; pas de nouveau runtime |
| RUNTIME_VALIDATION_13 | PASS 681 checks de fidélité des preuves, aucun upgrade de résultat runtime |
| TARGETED_MEASUREMENTS | PARTIALLY_ADVANCED ; FAIL entier FX et stops saved/input conservés |
| RUNNER_EXIT | INCONCLUSIVE, 14 IPC terminal1 malgré tous processus 0 |
| SCIENTIFIC_CLEANUP | PASS scope positif ; saved/input A/G et C3 INCONCLUSIVE, voir matrice |
| OPTIONAL_C3 | BUILD/STAGE validés ; runtime/mesures INCONCLUSIVE, lifecycle partiellement observé, clipping INCONCLUSIVE |
| FINAL_INDEPENDENT_REVIEW | ACCEPTED, audit PASS pour la fidélité expérimentale ; 0 BLOCKING,1 NON_BLOCKING,3 FUTURE_SCOPE ;43 tests et22 mutations rejetées |
| PUBLICATION | Autorisée et préparée, non exécutée à cette édition ; refs finales dans closeout privé et restitution, aucun SHA futur inventé |
| PRODUCTION_INTEGRATION | NOT AUTHORIZED ; STEP20C NEXT / NOT YET SUPPORTED |

Les checks et scripts runtime mentionnés sont des commandes **déjà enregistrées dans le LAB**. Cette tranche d’écriture ne les relance pas. La validation documentaire vérifie liens, cohérence des comptes/statuts et `git diff --check`. Ni commit/push, ni build/run/install/session live ne sont effectués par cette tranche.
