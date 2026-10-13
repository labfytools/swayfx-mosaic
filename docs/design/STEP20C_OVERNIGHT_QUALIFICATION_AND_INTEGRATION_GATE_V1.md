# SWAYFX_MOSAIC_STEP20C_OVERNIGHT_QUALIFICATION_AND_INTEGRATION_GATE_V1

> EXPERIMENTAL — édition documentaire du 2026-10-14, après revue finale ACCEPTED / audit PASS du dossier expérimental ; publication préparée, non exécutée à cette édition. Les résultats concernent des laboratoires privés ; aucune intégration production, installation ou décision UX. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED. Multi-output de production : NOT YET SUPPORTED. Les anciens rapports restent historiques et leurs résultats ne se transfèrent pas à un nouveau SHA.

L’autorité brute est le LAB privé `/home/fy59/swayfx-mosaic-overnight-mcolx0gq`. Les chemins LAB ci-dessous sont des références locales de preuve, pas des fichiers distribués. Les sources de fixture préservées se trouvent dans [tooling/probes/step20c-overnight](../../tooling/probes/step20c-overnight/qualification/README.md). La [provenance compacte](../../tooling/probes/step20c-overnight/qualification/provenance.json) lie les identités et reçus sans publier logs, images, binaires, archives ou patches candidats.

## Bilan proposé

Ticket exact : **SWAYFX_MOSAIC_STEP20C_OVERNIGHT_QUALIFICATION_AND_INTEGRATION_GATE_V1**. État global proposé **PARTIALLY_ADVANCED**, sous réserve de publication observée, recommandation **PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE** ; jamais PRODUCTION_READY. Aucun gate production fermé par ce ticket. Le budget est clos après18 tentatives uniques et196 captures, sans retry. A et G ont chacun build/stage propres ; les mesures positives et les limites ci-dessous restent simultanément vraies.

## Phases A–J et verdicts structurés

| Phase | Verdict enregistré | Preuve / limite |
| --- | --- | --- |
| A replay annoté | PASS | Pins archives pax,8 patches +2 commentaires,4 fichiers tokens équivalents ; nouveau SHA propre |
| A build/model/ELF | PASS local | SceneFX statique/Mosaic, modèle1/1, ELF/relocations/layouts ; ABI future non établie |
| A stage | STATIC_STAGE_WITH_LICENSES=PASS |5 fichiers exacts, DESTDIR privé ; legal PARTIAL |
| B préflight | PASS | Contrôles fixture/identité/budget prélaunch revus ; erreurs préflight corrigées hors ligne avant les runs concernés |
| C horizontal | FEASIBLE sampled |3 runs pristine/annotated-standard/Mosaic→standard ; preuve A propre |
| D géométries | PARTIALLY_FEASIBLE |D1/D3/D4 mesures positives, D2-Mosaic INCONCLUSIVE association fixture ; runtime tous INCONCLUSIVE |
| E1 hide/return | SAMPLED_MEASUREMENTS_PASS_RUNTIME_INCONCLUSIVE |Même hiérarchie, clips/pixels/input échantillonnés |
| E2 saved | NOT_EXERCISED_INCONCLUSIVE |Trigger defaults n’arrange pas courant, aucun configure HELD |
| E3 effets/cache | PARTIAL_RGB_FRESHNESS_WHOLE_RESTORATION_FAIL_INCONCLUSIVE |ROI A/B/A fraîche ; full-H1 return échoue dans les deux contrôles ; cleanup clients FAIL |
| F ordre/input | SAMPLED_INPUT_WITH_CEILINGS_INCONCLUSIVE |Assertion geometry stale, atomic/ref/release NOT PROVEN,10/12 pairs initiaux présents |
| G retrait/build | PASS local / BUILDABLE |26 logs/7 fichiers, revue delta exact ; PI/FBO ordering restent |
| G smoke | SMOKE_FEASIBLE |17 PNG, preuve G propre horizontale ; runtime PASS selon politique C/G avec IPC1 conservé |
| H package/maintenance | PARTIALLY_FEASIBLE |Recette syntaxe/inputs PASS, makepkg NOT RUN, notices/legal PARTIAL, nominations absentes |
| I décision intégration | DRAFT / PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE |22 réponses ; aucune décision appliquée |
| J docs/revue/publication | Revue finale ACCEPTED / audit PASS ; publication préparée, non exécutée |0 BLOCKING, 4 NON_BLOCKING, 3 FUTURE_SCOPE ; aucun commit/push revendiqué à cette édition |

## Évidence et discipline

[Reconstruction annotée](STEP20C_ANNOTATED_REBUILD_AND_PRIVATE_STAGE.md), [matrice graphique](STEP20C_ANNOTATED_GRAPHICS_MATRIX.md), [lifecycle/effets/native ordering](STEP20C_LIFECYCLE_EFFECTS_AND_NATIVE_ORDERING.md) et [22 réponses de décision](STEP20C_PRODUCTION_INTEGRATION_DECISION_DRAFT.md) sont les rapports de cette tranche. Ils ne réécrivent pas les freezes historiques. Provenance compacte liée dans leur en-tête ; source fixtures seulement, sans artefacts générés.

Préflight corrigé avant lancement : C inverse déco16 tests ; matrix association owner/root/temps et préservation transport33 tests ; R90 v3 association host38 tests ; G-SMOKE01/02 compteurs offline9 tests. Ledger5 tests avec rejets/concurrence ; revue runtime C7 mutations, premiers D14 négatifs, lifecycle32 checks, R90 runtime9 négatifs. Tous diagnostics initiaux et refus sont conservés. Correction offline de validateurs ne constitue pas un retry compositor. La revue source G et le smoke ont leur propre acceptation/gel.

Budget final : SceneFX2/2, Mosaic2/2, stages2/2, runs18/18, captures196/220 ; C3,D1–D4 chacun2,E1=1,E2=1,E3=2,F=2,G=1. Registre flock/atomique/fsync,18 tokens consommés une fois, aucun remboursement/reset.4 PNG marqueurs inputs séparés donnent200 nouvelles images ;78 assets upstream copiés ne sont pas des captures. Hash ledger `6ebedc65f30bf2c81f45b1487adf974a390a0049f632cfbb18bbbb00e3bfae3f`.

## Risques et critères de sortie proposés

Ce tableau est un registre de risques, pas une politique adoptée. P0 : aucun défaut bloquant confirmé dans l’échantillon. P1 : preuve essentielle avant intégration selon périmètre retenu ; P2 : maintenance/instrumentation/notice et décisions humaines ; P3 : couverture future hors tranche. Factuel ou hypothétique est indiqué. Tous environnements mesurés sont privés headless FX/GLES AMD780M et paire exacte A/G ; extrapolation interdite.

| ID / sévérité | Fait ou hypothèse / source / reproduction | Contrat affecté et travail minimal | Acceptation proposée / dépendance / humain |
| --- | --- | --- | --- |
| R-P0-01 / P0 |Aucun clip/input bloquant confirmé C/D1/D3/E1/G ; hypothèse de défaut ailleurs non testée ; replay PNG/wire |Ne pas conclure absence universelle ; conserver scope exact |Aucun P0 ouvert confirmé ; revue scientifique requise si nouvelle preuve |
| R-LIFE-01 / P1 |Refs/releases GPU/saved non observées ; source audit F-SOURCE-02/07 et E2 non exercé |Ownership/lifetime : fixture configure runtime attesté puis identités natives locks/releases/teardown |Protocole et critères lifetime avant nouveau budget ; dépend revue source/ABI ; reviewer humain |
| R-TXN-01 / P1 |F full→empty→full ;12 couples initiaux10 PAIRED/2 missing,57 commits ; fenêtre discriminante absente |État appliqué render/input/present : mesure native discriminante, sans forcer calendrier pour fabriquer PASS |Preuve d’identité et cohérence de génération selon contrat accepté ; dépend instrumentation/lifetime ; décision architecture |
| R-DAMAGE-01 / P1 |E3 full-H1 return33883 pristine/32132 Mosaic différences, ROI exact ; causalité ouverte |Damage/stale pixels : contrôle comparable et diagnostic fenêtres/effets, all-frame scope explicite |Critères full-frame/frames intermédiaires pertinents satisfaits, sans masque opportuniste ; dépend effets/txn ; revue scientifique |
| R-FIX-01 / P1 |D2 root ambiguity, E2 defaults, F rect stale ; sources/review raw reproductibles offline |Fixtures : owner-derived association, configure runtime attesté, geometry de la fenêtre appliquée |Nouveaux freezes/négatifs acceptés avant première exécution autorisée ; pas de retry du ticket ; reviewer |
| R-G-01 / P1 |G horizontal smoke seul, matrice étendue NOT TESTED |Qualification exact SHA G : relevant matrix complète et contrôles propres |Aucun héritage A ; dépend risque FBO/fixtures ; gate humain |
| R-ABI-01 / P2 |17 structs/6 offsets/121 headers/85 overlaps/34 bindings locaux, aucune ABI future |Paire épinglée ; audit headers/layout/providers/rebuild à chaque build pertinent |Nouvelle paire entièrement requalifiée ; dépend mainteneur/reviewer sécurité nommés |
| R-INST-01 / P2 |G retire26 logs mais PI listeners/FBO bind-before-failed conservés ; neutralité hypothétique |Auditer effets de callbacks/binds, comparer contrôles adéquats |Neutralité pertinente démontrée sans comparer des états non homologues ; dépend R-G/ABI ; reviewer |
| R-LIC-01 / P2 |895/894 inputs conservateurs, exact incorporation/legal PARTIAL |Textes/shaders/protocols/contributions conditionnelles et extraction archive |Inventaire incorporation et notices suffisantes examinés humainement avant distribution ; dépend package complet/release |
| R-PKG-01 / P2 |PKGBUILD.future syntaxe/inputs PASS, makepkg NOT RUN |Build paquet isolé, manifeste exact5 fichiers notices justifiées, coexistence |Validation intégrale source/package/stage et choix publication distinct ; dépend R-LIC/ABI ; release maintainer |
| R-ROLE-01 / P2 |Aucun release/security nominee/SLA ; H proposition privée |Veille/impact/rebuild/requalification/notices et décision release |Nominations humaines avant public distribution ; aucun SLA inventé |
| R-UX-01 / P2 |Hide/dismiss/reposition/click-through ouverts ; routing mesuré seulement |Décision UX explicite avant comportement shipped ; contracts first |Acceptation utilisateur puis docs UX/architecture pertinentes ; pas de changement ici |
| R-TRANSPORT-01 / P2 |IPC exit1 tous runs ; C/G runtime PASS policy, matrix INCONCLUSIVE |Conserver incident et distinguer fermeture process/réponse transport |Cause NOT PROVEN ; protocole futur doit documenter ce critère, sans silent upgrade ; reviewer |
| R-FUTURE-01 / P3 |Sorties physiques/backends autres, matrices exhaustives/future pairs NOT TESTED |Qualification au besoin, pas extension générale du fork |Scope et budget séparés ; STEP20D–G restent PLANNED ; décision utilisateur |

## État du dépôt et publication

HEAD initial `4ef16a40192149d353831695fd7dcaeb594fdf01`, branche main ; le répertoire source-only overnight était non suivi avant cette mise à jour. Sept fichiers protégés comparés avant/après identiques dans `parent/protected-integrity-before-publication.json`. Production, UX, Packaging, AGENTS, PKGBUILD, patch cumulatif et fixtures historiques préservés. Aucun stage Git/commit/push par l’auteur documentaire.

Audit parent `cleanup-after-graphs.json` : aucun PID/socket privé restant ; runtimes supprimés selon cleanup exécuté, chemins matrix individuels non consignés. Aucun live IPC, installation ou remplacement système. SceneFX système initial SHA non enregistré ; le SHA final ne permet pas une égalité initial/final inventée.

Revue finale indépendante ACCEPTED / audit PASS pour le dossier expérimental. Publication origin/github préparée, non exécutée à cette édition ; le reçu privé et le handoff final porteront le résultat réel et les SHAs finaux, sans autoréférence au futur hash de commit. La publication documentaire ne transforme pas la recommandation en décision production. Prochaine petite étape justifiée : validation du delta documentaire final et publication autorisée, puis gates ciblés dans une nouvelle tranche avant toute intégration.

## Revue finale observée et publication préparée

Revue indépendante finale ACCEPTED / audit PASS pour la fidélité du dossier expérimental : 0 BLOCKING, 4 NON_BLOCKING, 3 FUTURE_SCOPE ; 180 checks hors ligne et 15 mutations de preuves réelles rejetées. Rapport privé `reviews/overnight-final-review.md`, SHA256 `bb4000dffb51b07b59e86f91e8dd76bc2c4f0b9513b48a52c9f6bd6c8c3f45af` ; reçu JSON SHA256 `72ba252092ca3375d344faae1c2026c8d5626fd190e87771d5c0c1ad8212c9b0`. Index scientifique post-exécution `seals/index.json`, SHA256 `cdf034e1f8466a9ae8a0e0a33aa8d0d0195273f0d1bc782667b50c3bcf682505`, contexte de preuve courant, pas un binding pré-exécution.

NB-01 est complété dans l’index compact depuis les grabs wire réels de chacun des huit runs concernés, avec lignes et hashes sources dans `parent/metadata-serial-completion.json`. Les stops fixtures, échecs E3 et incident IPC restent documentés. Les gates lifetime/génération/damage, couverture G, maintenance ABI/paquet/juridique et robustesse/coût des sidecars privés restent ouverts. L’acceptation documentaire ne qualifie pas la production et n’applique aucune décision. Publication préparée, pas encore exécutée à cette édition ; les refs/SHAs finaux et le résultat de publication feront foi dans le reçu privé et le handoff final.
