# STEP20C — décision d’intégration production, draft

> EXPERIMENTAL — mise à jour ciblée du 2026-10-14. Revue finale indépendante du nouveau dossier : ACCEPTED, audit PASS pour la fidélité de l’évidence expérimentale. Publication documentaire autorisée et préparée, non exécutée à cette édition. C3 exécuté : INCONCLUSIVE, observations natives partielles sans transfert à A/G. Les verdicts historiques restent inchangés. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED. Multi-output de production : NOT YET SUPPORTED. Aucune intégration, installation ou décision UX.

La recommandation reste **PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE**. Le [rapport de clôture](STEP20C_TARGETED_CLOSURE_DECISION.md) lie les quatorze runs ciblés, les identités exactes et leurs risques à LAB `/home/fy59/swayfx-mosaic-targeted-7gge6h8b`. L’ancien LAB `/home/fy59/swayfx-mosaic-overnight-mcolx0gq` reste en lecture seule, PARTIALLY_ADVANCED, 18 runs/196 captures. Les [fixtures](../../tooling/probes/step20c-targeted/README.md) sont des sources scellées, pas des résultats de production. Les vingt réponses ci-dessous enregistrent l’évidence disponible, sans auto-approbation.

## 1. G est-il qualifié au-delà du smoke horizontal ?

Oui, pour de nouveaux échantillons sur son propre SHA `8063478b2d5948da3eb8b1a329978882dc1d045cf36932cc2145a78af20ba76a`, build ID `83896fdb36f3fd21522becec0e8c5219e15f4b8e` : scale, FX, input, saved, dynamic, hidden, R90. [Matrice G](STEP20C_RELEASE_SHAPE_EXTENDED_MATRIX.md) : dynamic PARTIALLY_FEASIBLE, hidden/R90/scale FEASIBLE échantillonné ; saved/input restent incomplets, whole-H1 FX FAIL. Aucun all-matrix PASS et aucun résultat A transféré.

## 2. Le scale 1,25 est-il réel avec input et grabs ?

Oui. [A/G séparément](STEP20C_TARGETED_SCALE_AND_POPUP_GATE.md) : mode physique1000×750, logique800×600, scale1,25, markers PNG, deux vrais grabs35/44, root/nested franchissant x=0, B visible livré, bouton interdit non livré/dismissal et H2 entier exact. Neuf PNG/quatre clics par run ; association bornée source, pas de join natif host/owner ID. Retour standard NOT EXERCISED dans cette allocation. Runtime brut INCONCLUSIVE sur IPC terminal1.

## 3. Un saved buffer réel a-t-il été observé ?

Un nouveau configure réel tenu sans ACK est prouvé sur A/G : ACK 30 puis serial 39,636×573→636×513, HELD_WIRE_VALIDATED. Cela établit le trigger et le hold client ; [identité native saved-node/render](STEP20C_TARGETED_SAVED_BUFFER_LIFECYCLE.md) NOT OBSERVABLE dans ces deux runs. Les anciens saved nodes d’autres binaires restent historiques. C3 distinct observe un saved node réel créé après gaps, sa référence source et un draw H1 ; le prédicat figé unique unreused saved node rejette l’adresse réutilisée. Création/rendu/teardown partiellement observés, runtime INCONCLUSIVE, sans transfert à A/G.

## 4. Son clipping est-il correct ?

Il n’est pas qualifié par les nouveaux saved-A/G : chacun s’arrête après deux références H2 sur le champ workspace IPC gaps absent. Aucun PNG pendant hold/timeout, aucun saved render natif lié. Saved clipping INCONCLUSIVE, sans FAIL produit démontré et sans PASS rétroactif. C3 observe draw/intersection héritée sur H1 mais aucun PNG held/live ou contrôle H2 pendant hold : clipping INCONCLUSIVE. Les preuves saved historiques ne se transfèrent pas aux SHA A/G ou C3.

## 5. Le lifetime est-il prouvé ou partiellement observé ?

L’audit natif est SOURCE_AUDIT_ONLY : création d’un nœud saved distinct, référence wlr_buffer lockée, destruction/unlock et réactivation live. Les runs FX ont normal close/error0/releases SHM avant compositeur ; saved-A/G terminent error32 pendant teardown malgré processus 0. C3 trace locks 3→4 puis destruction/release/destroy au teardown seulement ; owner error32/code0, sans timeout naturel ni normal close. Son découpage create→next destroy reste descriptif, sans génération native inventée. Lifetime complet buffers/textures/cache/GPU et commit rejeté NOT PROVEN. Cleanup mécanique, scientifique et lifetime restent distincts.

## 6. Le classic blur a-t-il vraiment filtré l’image ?

Oui dans pristine/A/G : [4096 pixels](STEP20C_TARGETED_EFFECTS_CACHE_DIAGNOSIS.md) de ROI centrale prospective changent à source SHM constante, contraste adjacent12,783069→0,090278. Fond haute fréquence XRGB, filler transparent et verre prémultiplié0x88442010 sont retenus. EXERCISED ; l’ancien filler opaque explique les anciens pixels uniformes selon source audit seulement, bytes historiques absents.

## 7. La restauration A/B/A passe-t-elle sur H1 entière ?

Non. Sans masque ni ROI opportuniste : FAIL 37252 pixels pristine/34323 A/G, max 6, signes natifs non positifs ; bbox pristine[400,0,800,600], A/G[480,0,800,600]. Centre exact et source A 1/A 3 byte-exact ne changent pas ce verdict. Le modèle donne68969 pixels history/0 fresh mais signe positif max 33 différent du natif négatif max 6 ; causalité native INCONCLUSIVE.

## 8. Les différences sont-elles communes au pristine ?

Oui, le nouveau pristine reproduit le retour whole-H1 imparfait. Les géométries visibles pristine/Mosaic diffèrent, donc les comptages ne démontrent pas une régression clip. Les seize captures A/G homologues sont RGB exactes et état/source normalisés égaux. Cela réduit une hypothèse visible propre aux traces A ; la causalité GPU et la neutralité temporelle restent NOT PROVEN.

## 9. L’input suit-il l’origine appliquée après les mutations ?

Les observations obtenues sont cohérentes avec la dernière origine native. Au troisième clic A/G : globale(-314,30), origine pré-capturée(-318,25), dernière native(-638,25), motion(324,5), boutons45/46 livrés. La camera change via focus pendant clic ; [fixture ambigu](STEP20C_TARGETED_INPUT_NATIVE_ORDERING.md), suite camera/layout NOT EXERCISED. Pristine contrôle standard complet ; aucune panne produit ni atomicité démontrée.

## 10. Les couples commit/present sont-ils correctement corrélés ?

Le replay utilise (output, commit_seq). Total final 14 runs : 821 commits,789 paired,32 missing (treize initiaux788/758/30 ; C3 ajoute 33/31/2) ; pristine PI NOT OBSERVABLE. F historique complet : 57 commits, 55 paired, 2 missing(seq 2 H1/H2), sans réécrire son ancien sous-ensemble 10/12. Le pairage correct ne lie pas contenu/pixels/GPU ; fenêtre naturelle mutation entre matching commit/present NOT EXERCISED.

## 11. Quels buffers sont réellement identifiés ?

Les buffers SHM client/wire, dimensions et dumps sources sont identifiés dans leur espace propre. Les callbacks output portent output/commit_seq ; A FX identifie un pointeur cache/FBO choisi, sans readback contenu. A/G n’identifient pas un saved-node/buffer GPU avec locks/releases ni l’image exacte présentée. C3 identifie un nœud/source dans l’intervalle descriptif de sa création à la prochaine destruction et un draw, sans identité de génération ou preuve GPU completion. wl_buffer release, saved node, texture/cache, output-state buffer, present et fin GPU restent distincts.

## 12. Quelles preuves de damage restent insuffisantes ?

Les captures stabilisées et traces disponibles restent échantillonnées. Le nouvel audit `parent/damage-envelopes.json` compare99 transitions d’images adjacentes entières des treize runs initiaux : 18 différences contenues dans des enveloppes physiques A, 79 NOT OBSERVABLE(trace absente/intervalle vide), deux changements de dimensions NOT COMPARABLE. Une enveloppe extents ne prouve pas région exacte/minimale, tous frames/stale pixels, ni liaison à un buffer présenté ou génération atomique.

## 13. Quel risque d’instrumentation résiduelle demeure dans G ?

PI listeners, traversées scène/owner/popup, clocks et logs restent ; logging peut bloquer/allouer.26 statements OPT/helpers retirés ne rendent pas G uninstrumented. FBO bind-before-failed reste différent de pristine ; failure semantics NOT TESTED.16 images A/G exactes limitent une différence visible dans le scope, neutralité timing/GPU INCONCLUSIVE. Audit/retrait et requalification futurs exigent budget distinct.

## 14. Les tests graphiques G permettent-ils une revue d’intégration ?

Ils permettent une revue plus informée du candidat privé, pas une approbation production. Dynamic 14 PNG resize 960/back/migrationH1/H2/H1/input frais lorsque popup_done, hidden 12 PNG même chaîne/emptyclip/retourB, R90 neuf PNG 750×1000 physique/scale1,25/logique800×600/markers sont propres à G. Saved/input partiels, FX FAIL, lifetime/damage/génération ouverts. Revue finale indépendante du dossier ciblé ACCEPTED, audit PASS pour la fidélité expérimentale ; aucune approbation d’intégration production.

## 15. Quelles limites ABI persistent ?

Paire locale SceneFX 0,5 commit 37ccd723bef49e6891156ffafce8f549f01446cc / wlroots 0,20,2 commitd783533489e1f75d6886c2ab5c5960090ef268f8, libSHA7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837,121 headers vérifiés.17 structs/six offsets égaux, 85 overlaps caractérisés, 34 bindings dont31 vers executable/trois wlroots. Ni incompatibilité prouvée ni safety complète ; toutes autres paires NOT QUALIFIED. Maintenance projet approuvée privé, release/security à nommer.

## 16. Quels points packaging restent ouverts ?

Syntaxe, septchecksums, makepkg --printsrcinfo/--verifysource local, forwardchecks deux patches PASS ; stage privé exact cinq fichiers réguliers sans symlink, DT_NEEDED sans SceneFX shared. Fullmakepkgbuild NOT RUN, reproductibilité bit à bit NOT PROVEN. Inventories895/894 entrées, 894/893 chemins uniques ; doublons/testlog ne prouvent pas incorporation. Préprocesseur/extraction archive/notices exactes et revue juridique HUMAN_REVIEW_REQUIRED. PKGBUILD réel inchangé, aucune installation/distribution.

## 17. Quelles décisions UX popup restent nécessaires ?

Offscreen hide/dismiss/reposition et click-through sous grab restent UNDECIDED. Les comparaisons contrôlées et routing/dismissal échantillonnés ne définissent pas une règle universelle. Aucun changement docs/UX ni bindings/configuration personnelle ; Mosaic reste opt-in dans workspace Sway ordinaire.

## 18. Quels travaux exigent encore un changement de code ?

Le fixture input doit mesurer/autoriser la mutation pendant livraison ; la mesure saved exige un predicate IPC adéquat et observabilité native bornée. Un discriminant GPU nécessite readback FBO/cache/output natif autorisé. Un éventuel retrait résiduel G et l’intégration clip/owner guard exigent revue exacte et requalification. Aucun correctif de produit causal n’est établi par PNG seuls ; aucun code production n’est modifié ici. C3 est un travail privé distinct consommé, runtime INCONCLUSIVE : son prédicat d’adresse globalement unique est trop strict pour la réutilisation observée. Aucun fixture gelé réparé, aucune relance.

## 19. Quelle plus petite tranche production est éventuellement envisageable ?

Après décisions humaines et fermeture des gates pertinents seulement : clip natif optionnel, owner-popup/hidden guard et retour standard workspace-local, Row0 empruntant workspace->tiling. Contrats Architecture/UX/Packaging/Upstream/Development avant code, puis delta petit/revu/testé sur nouveau SHA. Tests build/model/headlessIPC/pristine et matrice pertinente, ABI/header/providers, stage/notices/package complet et patch export/apply/source-equivalence/checksum. Fallback standard SwayFX indépendant,/usr/bin/sway intact, sans provides/conflicts/replaces ni remplacement système/config ; déploiement/rollback décision distincte. Aucun STEP20D ni tranche autorisée ici.

## 20. Quels risques imposent de différer toute intégration ?

P1 whole-H1GPU, lifetime saved/génération/damage, input temporel et couverture G ; P2 neutralité/ABI-maintenance, package/notices/legal, nominations, IPCterminal/attribution runtimepaths ; P3 sorties physiques plus larges. Aucun P0 prouvé. Les [risques sourcés](STEP20C_TARGETED_CLOSURE_DECISION.md) gardent critères de clôture et décisions humaines. C3 INCONCLUSIVE ; final review ACCEPTED, publication documentaire préparée/non exécutée à cette édition ; recommandation PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE, production NEXT/NOT YET SUPPORTED.
