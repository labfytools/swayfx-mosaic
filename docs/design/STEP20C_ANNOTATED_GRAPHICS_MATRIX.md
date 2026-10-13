# STEP20C — matrice graphique du binaire annoté

> EXPERIMENTAL — édition documentaire du 2026-10-14, après revue finale ACCEPTED / audit PASS du dossier expérimental ; publication préparée, non exécutée à cette édition. Les résultats concernent des laboratoires privés ; aucune intégration production, installation ou décision UX. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED. Multi-output de production : NOT YET SUPPORTED. Les anciens rapports restent historiques et leurs résultats ne se transfèrent pas à un nouveau SHA.

L’autorité brute est le LAB privé `/home/fy59/swayfx-mosaic-overnight-mcolx0gq`. Les chemins LAB ci-dessous sont des références locales de preuve, pas des fichiers distribués. Les sources de fixture préservées se trouvent dans [tooling/probes/step20c-overnight](../../tooling/probes/step20c-overnight/qualification/README.md). La [provenance compacte](../../tooling/probes/step20c-overnight/qualification/provenance.json) lie les identités et reçus sans publier logs, images, binaires, archives ou patches candidats.

## Matrice réellement exécutée

18 tentatives uniques, aucun retry, 196 captures compositeur. Chaque run utilise un runtime/socket privé. Le renderer observé dans les startups est SceneFX FX, OpenGL ES 3.2 Mesa 26.2.4-arch1.1, AMD Radeon 780M ; `WLR_RENDERER=pixman` demandé ne constitue pas une preuve pixman. Identités de spawn et proc maps contrôlées.

| Identité | SHA256 | Build ID |
| --- | --- | --- |
| A annoté, utilisé C1/C2 et Mosaic D/E/F | `979dcd95ab43fa1e465d6e9d262485b73d186cedacd0f957059dd24f482ce6f4` | `fabfeb823754a0f5107f83eb077323ad17ddedd1` |
| G release-shape, smoke propre | `8063478b2d5948da3eb8b1a329978882dc1d045cf36932cc2145a78af20ba76a` | `83896fdb36f3fd21522becec0e8c5219e15f4b8e` |
| Contrôle pristine retenu | `8ac865481bc0487344210cd0e16d8e6c7655b29db887cd58ddc11b0ca22fe494` | `298a9626b331139ff2f081ade9c4efdde2d4fb19` |

Paire locale : SceneFX 0.5.0 statique privé, wlroots 0.20.2 partagé, bibliothèque SHA256 `7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`. Tous les autres builds/paires sont NOT QUALIFIED.

Géométries : C, D4, E, F et G ont H1 `[-800,0,800,600]`, H2 `[0,0,800,600]`, modes 800×600, scale1, normal ; D1 H1 `[0,0,800,600]`, H2 `[0,600,800,600]`. D2 H1 logique `[-800,0,800,600]`, mode1000×750, scale1,25/normal ; D3 même logique, mode750×1000, scale1,25/R90. H2 reste 800×600 scale1/normal. Les cinq marqueurs asymétriques réellement capturés établissent la frame PNG1000×750 avant les conversions D2/D3 : une conversion logique→PNG est appliquée une seule fois. La migration/resize D4 est une mutation mesurée, pas un autre run. Les rectangles utilisent des bornes half-open. Native SHM buffer, configure XDG, destination tiling/IPC assigned, scène applied et origine client globale, viewport logique, mode physique et pixels PNG restent des espaces distincts ; les mesures de destination ne sont pas une identité de buffer. Les adaptations de scale/rotation sont corroborées par marqueurs et wire, sans mélanger l’origine current et applied.

| Run | Binaire | PNG | Mesure / runtime / cleanup | Portée |
| --- | --- | --- | --- | --- |
| C0 | pristine | 10 | PASS / PASS / PASS | contrôle pristine horizontal |
| C1 | A | 10 | PASS / PASS / PASS | contrôle annoté splith |
| C2 | A | 17 | PASS / PASS / PASS | Mosaic, deux chaînes et retour standard |
| D1-pristine | pristine | 8 | PASS / INCONCLUSIVE / PASS | overflow vertical standard |
| D1-mosaic | A | 8 | PASS / INCONCLUSIVE / PASS | clip vertical + input/dismissal |
| D2-pristine | pristine | 9 | PASS / INCONCLUSIVE / PASS | scale1,25 standard + input |
| D2-mosaic | A | 7 | INCONCLUSIVE / INCONCLUSIVE / PASS | pixels/grabs ; association root fixture ambiguë |
| D3-pristine | pristine | 9 | PASS / INCONCLUSIVE / PASS | R90 standard + input |
| D4-pristine | pristine | 17 | PASS / INCONCLUSIVE / PASS | resize/migration standard |
| D4-mosaic | A | 17 | PASS / INCONCLUSIVE / PASS | resize/migration Mosaic ; input pendant migration non échantillonné |
| E1-mosaic | A | 12 | PASS / INCONCLUSIVE / PASS | hide/return même chaîne |
| E2-mosaic | A | 2 | INCONCLUSIVE / INCONCLUSIVE / PASS | saved configure non déclenché |
| E3-pristine | pristine | 16 | INCONCLUSIVE / INCONCLUSIVE / FAIL clients | ROI cache A/B/A ; full restoration échoue |
| E3-mosaic | A | 16 | INCONCLUSIVE / INCONCLUSIVE / FAIL clients | ROI/cache USE ; full restoration échoue |
| F-pristine | pristine | 8 | INCONCLUSIVE / INCONCLUSIVE / PASS | input regions ; sans trace privée native |
| F-mosaic | A | 4 | INCONCLUSIVE / INCONCLUSIVE / PASS | input regions ; assertion de géométrie périmée |
| G-smoke | G | 17 | PASS / PASS / PASS | preuve propre G horizontal seulement |
| D3-mosaic | A | 9 | PASS / INCONCLUSIVE / PASS | R90 v3 première exécution ; revue runtime acceptée |

Les trois runs C sont FEASIBLE dans leur scope ; D est PARTIALLY_FEASIBLE globalement. Les receipts structurés préservent serials réels, actions et géométries de chaque run dans la provenance compacte. Les mesures absentes ne sont pas inférées.

## Pixels, protocoles et input

C0/C1 : TOPLEVEL→A→B réel, deux grabs serial33/42, configure/ACK/SHM. A[-298,105,350,170], B[-198,165,300,130] traversent x0 ; entrée B puis A réelle sur H2. Huit images homologues C0/C1 entières exactement égales en RGB, sans masque ni tolérance. Fermeture B conservant A et fermeture owner normales, référence H2 finale exacte.

C2 : deux owners distincts, grabs33/42 puis91/100. A[-218,105,350,170], B[-118,165,300,130], owner appliqué[-318,25,636,573]. H1 conserve les pixels A/B ; H2 complet exact. B visible reçoit51/52 ; B-H2[91,195] ne reçoit aucun bouton, puis done/destroy B→A ; référence62/63 observée. Le retour splith du même owner/root/hierarchie est reconstitué sur deux callbacks old-Mosaic puis six applied-standard sans réactivation du clip, avec B111/112 puis A117/118. Aucun click-through universel.

D1 : A/B traversent y600 de75/115. Pristine H1 A21200/B2550 et H2 A6000/B19550 ; Mosaic H1 mêmes nombres, H2 A0/B0 et RGB exact. Grabs31/40 pristine,33/42 Mosaic. B H2 réel standard, absent côté Mosaic ; dismissal et référence62/63 observés. Le champ helper historique `crossing` x0 NOT EXERCISED n’est pas le prédicat vertical : revue y600 indépendante.

D2 : pristine H1 A45150/B40261, H2 A3120/B13260 ; Mosaic H1 A37650/B23961, H2 A0/B0, grabs35/44 réels. Le layer wallpaper de marqueurs crée avant l’owner un host descriptor POPUP ; le fixture exigeait à tort un root global unique/index1 alors que le root XDG est index2. Association source+temps+cardinalité, sans owner-ID natif direct. Arrêt consommé avec7 PNG et2 clics d’ouverture ; input B visible/interdit, dismissal et finals NOT EXERCISED. Aucun rerun D2 ni défaut compositor démontré.

D3 : pristine contrôle réel avec grabs35/44 et marqueurs. Mosaic v3 a été réparé/revu avant sa première exécution, freeze `7ae5f3ad8cc8cb738740c6a32fe7e1f336d20226b7813a03e22be3030d1507fb`, 1172 entrées ; archive v2 exécutée578 SHA conservée. Mesures runner PASS,9 PNG/4 clics/2 grabs35/44,1 caméra ; H1 A37650/B23961, H2 A0/B0 et480000 pixels exacts ; B visible, interdit puis dismissal final observés. La revue runtime indépendante `reviews/rotation-v3-runtime-review.md` est ACCEPTED / FEASIBLE_SAMPLED_R90 : 11 callbacks baseline avant target owner9 (les trois derniers concernent filler8), puis un callback mapped complet. Neuf négatifs sont refusés ; owner/root association bornée sans IDs natifs. Aucun retour splith testé dans D3.

D4 : resize H1→960 puis800, workspace/owner H1→H2→H1, IDs et ordre natif préservés, ancienne sortie restaurée exactement. Trois cellules, largeur minimale640/gap0, caméra demandée relative1920 clampée à960. Input durant migration NOT TESTED ; aucune identité de génération atomique.

G :17 PNG/8 clics/4 grabs,2 chaînes,2 caméras,1 retour splith. Maps G exact et absence SceneFX dynamique. Clips root/owner, H2 Mosaic/final exact, standard H2 A3120/B13260 et input wire corroborés ; cleanup propre. Verdict SMOKE_FEASIBLE horizontal, aucune matrice G complète ni neutralité héritée de A.

## Transport, limites et budgets

Toutes les IPC terminales ont code1 « Unable to receive IPC response », stdout vide, compositor0. Les politiques C/G permettent runtime PASS lorsque mesures/fermetures complètes ; matrix conserve runtime INCONCLUSIVE. Cette différence explicite n’est pas harmonisée et la cause de la perte de réponse n’est pas prouvée. E3 : deux clients par run code1/error32 après interruption, cleanup scientifique FAIL ; tous processus sont pourtant reaped et runtimes supprimés, sans watchdog/rescue. Les autres cleanups sont PASS.

Registre durable flock + remplacement atomique + fsync :2/2 SceneFX,2/2 Mosaic,2/2 stages,18/18 runs,196/220 captures, maximum20/run et12 pour F,150 s/run. Local C3,D1–D4 chacun2,E1=1,E2=1,E3=2,F=2,G=1. Quatre PNG de marqueurs générés sont des inputs séparés :200 nouvelles images ;78 copies d’assets upstream ne sont pas des captures. Aucun remboursement, reset ou relance. Hash final ledger `6ebedc65f30bf2c81f45b1487adf974a390a0049f632cfbb18bbbb00e3bfae3f`.

Revue indépendante C, premiers D et lifecycle/G acceptées pour ces faits seulement ; preuves/négatifs conservés même lorsqu’un premier script d’analyse a échoué puis été corrigé hors ligne. Revue R90 runtime acceptée ; revue finale du dossier expérimental ACCEPTED / audit PASS, distincte des gates production. Damage de toutes frames, lifetime GPU, génération atomique, sortie réelle non headless et UX popup universelle NOT PROVEN / NOT TESTED.

## Revue finale observée et publication préparée

Revue indépendante finale ACCEPTED / audit PASS pour la fidélité du dossier expérimental : 0 BLOCKING, 4 NON_BLOCKING, 3 FUTURE_SCOPE ; 180 checks hors ligne et 15 mutations de preuves réelles rejetées. Rapport privé `reviews/overnight-final-review.md`, SHA256 `bb4000dffb51b07b59e86f91e8dd76bc2c4f0b9513b48a52c9f6bd6c8c3f45af` ; reçu JSON SHA256 `72ba252092ca3375d344faae1c2026c8d5626fd190e87771d5c0c1ad8212c9b0`. Index scientifique post-exécution `seals/index.json`, SHA256 `cdf034e1f8466a9ae8a0e0a33aa8d0d0195273f0d1bc782667b50c3bcf682505`, contexte de preuve courant, pas un binding pré-exécution.

NB-01 est complété dans l’index compact depuis les grabs wire réels de chacun des huit runs concernés, avec lignes et hashes sources dans `parent/metadata-serial-completion.json`. Les stops fixtures, échecs E3 et incident IPC restent documentés. Les gates lifetime/génération/damage, couverture G, maintenance ABI/paquet/juridique et robustesse/coût des sidecars privés restent ouverts. L’acceptation documentaire ne qualifie pas la production et n’applique aucune décision. Publication préparée, pas encore exécutée à cette édition ; les refs/SHAs finaux et le résultat de publication feront foi dans le reçu privé et le handoff final.
