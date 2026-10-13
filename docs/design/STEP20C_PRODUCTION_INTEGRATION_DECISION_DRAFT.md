# STEP20C — décision d’intégration production, draft

> EXPERIMENTAL — édition documentaire du 2026-10-14, après revue finale ACCEPTED / audit PASS du dossier expérimental ; publication préparée, non exécutée à cette édition. Les résultats concernent des laboratoires privés ; aucune intégration production, installation ou décision UX. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED. Multi-output de production : NOT YET SUPPORTED. Les anciens rapports restent historiques et leurs résultats ne se transfèrent pas à un nouveau SHA.

L’autorité brute est le LAB privé `/home/fy59/swayfx-mosaic-overnight-mcolx0gq`. Les chemins LAB ci-dessous sont des références locales de preuve, pas des fichiers distribués. Les sources de fixture préservées se trouvent dans [tooling/probes/step20c-overnight](../../tooling/probes/step20c-overnight/qualification/README.md). La [provenance compacte](../../tooling/probes/step20c-overnight/qualification/provenance.json) lie les identités et reçus sans publier logs, images, binaires, archives ou patches candidats.

## Recommandation soumise, non appliquée

**PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE**. L’état global proposé est PARTIALLY_ADVANCED, sous réserve de publication observée, jamais PRODUCTION_READY. Aucun défaut P0 clip/input confirmé dans le scope mesuré, mais les gates lifetime, damage/transactions, effets, ABI-maintenance, packaging/notices et politique humaine restent ouverts. L’issue globale scientifique est PARTIALLY_ADVANCED ; ce draft ne décide pas une intégration et n’autorise ni distribution ni STEP20D.

Les réponses sont liées aux [matrices exactes](STEP20C_ANNOTATED_GRAPHICS_MATRIX.md), au [build/stage](STEP20C_ANNOTATED_REBUILD_AND_PRIVATE_STAGE.md) et aux [limites lifecycle](STEP20C_LIFECYCLE_EFFECTS_AND_NATIVE_ORDERING.md). Elles distinguent preuve locale et contrat futur.

## 1. Le nouveau binaire annoté est-il réellement qualifié?

A est qualifié localement pour source/build/model/ELF/stage et possède ses propres mesures graphiques C/D/E/F. FEASIBLE pour C horizontal ; PARTIALLY_FEASIBLE globalement. Ni qualification production complète ni READY.

## 2. Quelles matrices ont été exercées?

18 runs uniques : C0/C1/C2 horizontal négatif ; D1 vertical pair ; D2 scale1,25 pair ; D3 R90/1,25 pair ; D4 resize/migration pair ; E1 hide/return ; E2 saved trigger ; E3 effets/cache pair ; F regions/ordering pair ; G smoke. Les limites et actions non exercées restent explicites dans la matrice.

## 3. Quels contrôles pristine sont disponibles?

C0 et D1/D2/D3/D4/E3/F pristine réellement exécutés sur le SHA retenu. C0/C1 full RGB égal aux huit états homologues ; D2/D3 markers et spill/input ordinary effectifs. Pristine F non modifié ne porte aucune PI privée. Ces contrôles ne qualifient pas un autre SHA.

## 4. Quels résultats restent partiels?

D2-Mosaic association root ambiguë avant input/final ; E2 saved NOT EXERCISED ; E3 full-H1 return FAIL dans les deux contrôles, classic NOT EXERCISED ; F géométrie fixture périmée et suite non exercée ; G horizontal smoke seul ; ABI future/notices/legal/package complets non qualifiés.

## 5. Existe-t-il un défaut bloquant de clipping ou d’input?

Aucun défaut bloquant démontré dans les fenêtres échantillonnées C/D1/D3/D4/E1/G. D2/F stops sont expliqués par le fixture, sans PASS rétroactif. Cela ne prouve pas l’absence universelle de défaut.

## 6. Existe-t-il un risque de lifetime non résolu?

Oui : identité native buffers, locks/références/releases GPU/saved, teardown exhaustif et scénarios de commit rejeté ne sont pas prouvés. Cleanup PID propre est une preuve de processus, pas de lifetime GPU. G garde FBO bind-before-failed potentiellement non passif.

## 7. Quel est l’état réel du damage?

Échantillons et traces extents conservés, H2 exact dans les états citées ; whole-H1 A-return effets échoue dans les deux contrôles. Damage exhaustif, minimal, stale pixels intermédiaires et contenu exact présenté NOT PROVEN.

## 8. Quelle est la portée des preuves de transactions?

Source applied clip et callbacks échantillonnés, regions full/empty/full observées. Sur12 couples initiaux F,10 PAIRED/2 MISSING_PRESENT ;57 commits bruts. Pas d’epoch atomique ni de fenêtre naturelle discriminante ni d’identité pixels/hit/present complète.

## 9. Le candidat release-shape existe-t-il?

Oui, G privé source/build/stage exact existe, SHA8063478b2d5948da3eb8b1a329978882dc1d045cf36932cc2145a78af20ba76a, build ID83896fdb36f3fd21522becec0e8c5219e15f4b8e. Aucun candidat binaire/package public distribué.

## 10. Son comportement est-il testé ou seulement compilé?

G est buildable et possède un smoke propre17 PNG/8 clics/4 grabs/retour splith, indépendamment revu. SMOKE_FEASIBLE horizontal seulement ; matrice G étendue et neutralité complète NOT TESTED/NOT PROVEN.

## 11. Quels patches fonctionnels doivent être conservés?

Dans le candidat privé : subtree clip SceneFX, clip owner-derived popup, guard owner totalement caché et delta natif Mosaic. Les commentaires token-equivalent sont acceptés. Une extraction de production exige encore revue exacte source/ownership/lifetime et décision, sans appliquer ces patches maintenant.

## 12. Quels patches de trace peuvent être retirés?

Seulement le retrait privé G déjà revu :26 logs/7 fichiers et helpers réellement orphelins. Timing/cache/PI ne se retirent pas en bloc sans audit ; PI listeners et FBO bind ordering restent. Aucun patch de production réécrit.

## 13. Quelle ABI SceneFX est réellement qualifiée?

SceneFX0.5 statique exact local, ELF appels clip directs,17 structs/6 offsets/85 overlaps/34 diagnostic bindings. Pas une ABI externe stable, ni tous providers runtime, ni une ABI future ou full semantic safety.

## 14. Quelle paire wlroots est réellement qualifiée?

Paire locale SceneFX37ccd723bef49e6891156ffafce8f549f01446cc + wlroots0.20.2 d783533489e1f75d6886c2ab5c5960090ef268f8, libSHA7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837 et121 headers épinglés. Tous autres builds/paires NOT QUALIFIED ; changement implique rebuild/requalification.

## 15. La future recette Arch est-elle reproductible?

Inputs privés hashés, syntaxe shell/Python et sources PASS ; makepkg metadata/source verification/build NOT RUN. Pas de reproductibilité binaire bit à bit ni de paquet distribution publique validé. PKGBUILD.future ne modifie pas PKGBUILD réel.

## 16. Quels textes de licence restent à valider?

Les quatre fichiers stage incluent LICENSE SceneFX/SwayFX/wlroots et INCORPORATED-NOTICES. Inventaires895 A/894 G conservateurs ; incorporation exacte, extraction archives et contributions conditionnelles puis suffisance juridique nécessitent validation humaine. Aucun legal PASS.

## 17. Qui devra assurer les releases et la sécurité?

Responsabilité projet pour SceneFX embarqué déjà approuvée dans le périmètre privé ; release maintainer et security reviewer doivent être désignés avant distribution. Aucun nom ni SLA inventé. Veille, impact, rebuild, tests, notices et publication documentés comme procédure proposée.

## 18. Quelle politique popup UX reste à décider?

Hide/dismiss/reposition de popup offscreen et comportement sous grab/click-through restent ouverts. Les observations de routing ne fixent pas une politique universelle. Aucun changement UX dans cette tranche.

## 19. Quelles corrections sont nécessaires avant une intégration dans main?

Nouveau fixture ciblé saved provoquant configure runtime attesté, diagnostic full-H1 effets avec contrôles, assertion input liée à géométrie appliquée, mesure lifetime/native refs/releases/temporal discriminante et neutralité G/FBO. Chaque gate pertinent doit avoir critères acceptés et nouvelle autorisation/budget ; aucun rerun dans le budget clos. Puis politiques humaines ABI/notices/release/security/UX, contrats canoniques avant code.

## 20. Quelle est la plus petite tranche de production envisageable après décision utilisateur?

Après décision humaine et gates pertinents clos seulement : clip natif optionnel dans workspace Sway ordinaire, Row0 empruntant workspace->tiling, owner popup clip et hidden-owner guard revus, restauration standard locale préservée. Contrats Architecture/UX/Packaging/Upstream/Development d’abord, puis petit delta revu/testé. Aucun STEP20D, ligne runtime additionnelle, animation ou taille finale ; aucune implementation ici.

## 21. Quels tests doivent impérativement être refaits après une intégration?

Nouveau exact SHA : compile/model/headless IPC et standard pristine, export cumulatif forward apply/source-equivalence/checksum, ELF/header/layout/providers/relocations, manifests stage/notices et package complet, toute matrice graphique C/D/E/F pertinente et smoke propre G, input/popups/grabs/retour standard, geometry scale/rotation/migration, saved/effects/damage/lifetime. Pas d’héritage automatique du LAB.

## 22. Quel plan de rollback protège SwayFX standard?

Proposition future : conserver package SwayFX et /usr/bin/sway indépendants, sélectionner sa session existante après quitter la candidate ; retirer seulement fichiers appartenant à Mosaic vérifiés. Aucun provides/conflicts/replaces, système lib/config/dotfiles remplacé. Déploiement et rollback nécessitent décision distincte, jamais exécutés ici.

## Conditions de décision

Ce dossier apporte un candidat et des preuves reviewables. La revue finale indépendante est ACCEPTED / audit PASS pour la fidélité de l’évidence expérimentale, sans adoption production. Publication documentaire préparée, non exécutée à cette édition. Publication des docs/fixtures et adoption en production sont des actes distincts ; le résultat réel et les SHAs finaux origin/github feront foi dans le reçu privé et le handoff final, sans faux hash futur dans ce draft.

## Revue finale observée et publication préparée

Revue indépendante finale ACCEPTED / audit PASS pour la fidélité du dossier expérimental : 0 BLOCKING, 4 NON_BLOCKING, 3 FUTURE_SCOPE ; 180 checks hors ligne et 15 mutations de preuves réelles rejetées. Rapport privé `reviews/overnight-final-review.md`, SHA256 `bb4000dffb51b07b59e86f91e8dd76bc2c4f0b9513b48a52c9f6bd6c8c3f45af` ; reçu JSON SHA256 `72ba252092ca3375d344faae1c2026c8d5626fd190e87771d5c0c1ad8212c9b0`. Index scientifique post-exécution `seals/index.json`, SHA256 `cdf034e1f8466a9ae8a0e0a33aa8d0d0195273f0d1bc782667b50c3bcf682505`, contexte de preuve courant, pas un binding pré-exécution.

NB-01 est complété dans l’index compact depuis les grabs wire réels de chacun des huit runs concernés, avec lignes et hashes sources dans `parent/metadata-serial-completion.json`. Les stops fixtures, échecs E3 et incident IPC restent documentés. Les gates lifetime/génération/damage, couverture G, maintenance ABI/paquet/juridique et robustesse/coût des sidecars privés restent ouverts. L’acceptation documentaire ne qualifie pas la production et n’applique aucune décision. Publication préparée, pas encore exécutée à cette édition ; les refs/SHAs finaux et le résultat de publication feront foi dans le reçu privé et le handoff final.
