# STEP20C — reconstruction annotée et staging privé

> EXPERIMENTAL — édition documentaire du 2026-10-14, après revue finale ACCEPTED / audit PASS du dossier expérimental ; publication préparée, non exécutée à cette édition. Les résultats concernent des laboratoires privés ; aucune intégration production, installation ou décision UX. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED. Multi-output de production : NOT YET SUPPORTED. Les anciens rapports restent historiques et leurs résultats ne se transfèrent pas à un nouveau SHA.

L’autorité brute est le LAB privé `/home/fy59/swayfx-mosaic-overnight-mcolx0gq`. Les chemins LAB ci-dessous sont des références locales de preuve, pas des fichiers distribués. Les sources de fixture préservées se trouvent dans [tooling/probes/step20c-overnight](../../tooling/probes/step20c-overnight/qualification/README.md). La [provenance compacte](../../tooling/probes/step20c-overnight/qualification/provenance.json) lie les identités et reçus sans publier logs, images, binaires, archives ou patches candidats.

## Reconstruction exacte A et portée H

A : PASS pour rejeu source, annotations, build, modèle, ELF, ABI locale et stage ; H : PARTIALLY_FEASIBLE pour préparation du paquet et maintenance. La compilation ne prouve pas un comportement graphique. Le nouveau A a ensuite ses propres preuves C/D/E/F ; G possède une identité et un smoke séparés.

| Source épinglée | Commit |
| --- | --- |
| SwayFX 0.6 | `fd71a6bdc061bd633b488ae7b83e8a6981d22f86` |
| Mosaic source historique | `cd550382b311efdbfe3ed892f4e1d281d852e754` |
| SceneFX 0.5 | `37ccd723bef49e6891156ffafce8f549f01446cc` |
| wlroots 0.20.2 | `d783533489e1f75d6886c2ab5c5960090ef268f8` |

La revue `reviews/phase-a-review.md` a vérifié les labels commit pax des quatre archives, leurs hashes et le rejeu strict. L’absence de `.git` dans une extraction n’invalide pas cette provenance ; l’avertissement initial d’inventaire est résolu par cette preuve. Huit patches fonctionnels/instrumentation sont rejoués dans l’ordre, puis deux patches de commentaires. `git apply --check` précède chaque application normale ; chaque arbre parent/résultat et les quatre fichiers annotés sont vérifiés. Une comparaison lexicale tenant compte des littéraux conserve tous les tokens C actifs. Les insertions peuvent décaler `__LINE__`. Le NOT REBUILT historique décrivait l’ancien D, pas A.

| Arbre / ordre | Patch | SHA256 |
| --- | --- | --- |
| scene-source / 0 | scenefx-popup-plus-base.patch | `c74c515b98da8f5f637e260e6a3755c7a75bd78d1c39e54a67850f1c383e30e7` |
| scene-source / 1 | scenefx-timing.patch | `7a7ef1875b559f65a3240a0016592da1da6a8537929d0e96b8aaa2d20ecd46fa` |
| scene-source / 2 | scenefx-cache-trace.patch | `a0fd5a64156a79b1605ff3b52bd9accb20390199b2b36e1970389f5086b68f39` |
| mosaic-source / 0 | mosaic-popup-plus-base.patch | `d416f6413ea097a48a44d231e50ffba363914f46c8687f0ea2e4dcacd5f31fe9` |
| mosaic-source / 1 | hidden-guard.patch | `35785a8f3e863b3c1fd87932d8ff0c2949b03cb04382cc34e1126170968f802b` |
| mosaic-source / 2 | mosaic-output-timing.patch | `4419059231e038675f50a6321889f27ba981c5d8df2779ccbc4a61e02f1d6668` |
| mosaic-source / 3 | presentation-events.patch | `dbf1f1d11c9c741b641916d25ac22bcb13c3455ee3002e1f534aa6794cd8a538` |
| mosaic-source / 4 | sway-source-trace.patch | `b83ff12bf24ee879cc713a134b0c312e9b8bd1b4034ecc2aea124d55a743ebb7` |
| annotations | scenefx-comments.patch | `21f057ff4180bb5dd35af35070aa4a95923be83f81abb864793e5bfb93643b01` |
| annotations | mosaic-comments.patch | `7fee137101abc0cd5024cea172c5904268ddf995bc5855c570e4dfabd643c970` |

| Identité | SHA256 | Build ID |
| --- | --- | --- |
| A annoté, utilisé C1/C2 et Mosaic D/E/F | `979dcd95ab43fa1e465d6e9d262485b73d186cedacd0f957059dd24f482ce6f4` | `fabfeb823754a0f5107f83eb077323ad17ddedd1` |
| G release-shape, smoke propre | `8063478b2d5948da3eb8b1a329978882dc1d045cf36932cc2145a78af20ba76a` | `83896fdb36f3fd21522becec0e8c5219e15f4b8e` |
| Contrôle pristine retenu | `8ac865481bc0487344210cd0e16d8e6c7655b29db887cd58ddc11b0ca22fe494` | `298a9626b331139ff2f081ade9c4efdde2d4fb19` |

Paire locale : SceneFX 0.5.0 statique privé, wlroots 0.20.2 partagé, bibliothèque SHA256 `7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`. Tous les autres builds/paires sont NOT QUALIFIED.

L’ancien D `616aa504334d88aada5b1596df624957f39b0f1ae975a1a04105fbf73aea6dd0` et l’ancien candidat C `f82557…` sont historiques. Aucun résultat de ces identités ne qualifie A ou G. Les patches cumulatifs annotés privés sont `candidate-cumulative.patch` (`8fea59b98907f5c57f841e624c53437d0fe886b56ccf80f472be8d08389b8ca0`) et `scenefx-cumulative.patch` (`7e1549d68d33945620690d26ee6b1a6cc2f3942e4000c9ac89d79a317f136302`) ; leurs hashes diffèrent volontairement des cumulatifs historiques non annotés.

## Reproduction bornée

Reconstituer les inputs vérifiés dans un nouveau LAB ; ne pas utiliser le checkout production comme pristine. Le point d’entrée source est `tooling/probes/step20c-overnight/replay_annotated.py LAB --historical HISTORICAL`, où HISTORICAL est le dossier privé `integration-candidate` retenu avec ses archives, patches et scripts (`/home/fy59/swayfx-mosaic-e2-completion-dk1hq9an/integration-candidate` dans cette campagne). Ce script initialise un nouveau registre, vérifie le rejeu et exécute les builds/stage ; son lancement n’est pas autorisé par ce rapport documentaire et ne doit jamais viser le LAB consommé. Les dépendances privées doivent être conservées et vérifiées avant une reproduction. Les commandes Meson ci-dessous décrivent celles du script, pas une voie permettant de contourner les réservations. Les scripts de fixture et leurs manifests décrivent le rejeu. Le registre réserve avant setup/build/stage, sans reset ni remboursement. Les commandes A effectivement enregistrées dans `raw/commands.jsonl` sont reproduites ci-dessous avec `LAB` désignant ce nouveau répertoire ; `PKG_CONFIG_PATH` reste limité à chaque processus.

```sh
meson setup "$LAB/scene-build" "$LAB/scene-source" --prefix=/usr \
  -Ddefault_library=static -Dexamples=false -Dwerror=false
meson compile -C "$LAB/scene-build" -j 8
PKG_CONFIG_PATH="$LAB/scene-build/meson-uninstalled" meson setup \
  "$LAB/mosaic-build" "$LAB/mosaic-source" --prefix=/usr --bindir=bin \
  -Dwerror=false -Dsd-bus-provider=libsystemd -Dmosaic-package=true \
  -Dswaybar=false -Dswaynag=false -Dman-pages=disabled -Ddefault-wallpaper=false
PKG_CONFIG_PATH="$LAB/scene-build/meson-uninstalled" meson compile -C "$LAB/mosaic-build" -j 8
meson test -C "$LAB/mosaic-build" --no-rebuild mosaic-model --print-errorlogs
meson install -C "$LAB/mosaic-build" --no-rebuild --destdir "$LAB/stage-static"
```

Les notices sont ajoutées par simulation privée du futur paquet, puis le manifeste complet est audité. A : SceneFX C23, Mosaic C11 ; audit de layouts C17 `-Wall -Wextra -Werror`. Les 132 commandes A, leurs dates Unix, durées et codes sont conservées ; les dates UTC exactes des setups/compilations figurent dans la provenance compacte. Compilation SceneFX environ 0,90 s, Mosaic environ 7,81 s ; setup séparé. Les deux `git diff --no-index` code 1 produisent les patches privés, sans échec de compilation. Les commandes ultérieures `g-*` dans le même journal ne font pas partie des 132 commandes A.

G : second build/stage autorisé, exécuté le 2026-10-14T00:35:52+02:00 avec les mêmes options et chemins `release-shape/`. Modèle 1/1, audit C17 et stage PASS. Sortie intégrale Meson/Ninja non conservée par l’adaptateur : les journaux/résultats/extraits existent, sans prétendre à un stdout complet. Les spans `.ninja_log` sont des timings internes et ne remplacent pas une durée murale. Un avertissement `LIBINPUT_CONFIG_SCROLL_CIRCULAR` dans `sway/ipc-json.c:1175` est conservé.

## ELF et ABI locale

A et G : ELF64 x86-64 PIE, aucune dépendance SceneFX DT_NEEDED, wlroots partagé attendu, RPATH/RUNPATH vides, `ldd -r` sans symbole indéfini, fonctions clip définies et appels directs inspectés. Comparaison locale de 17 structures et 6 offsets identique ; 121 headers wlroots épinglés ; 85 noms communs caractérisés, distincts des 34 bindings réellement observés par le loader diagnostique. Ni les 85 fournisseurs runtime universels ni l’ABI sémantique future, l’interposition générale ou la neutralité graphique ne sont démontrés.

## Stage et notices

Exactement cinq fichiers réguliers dans chacun des deux DESTDIR, binaire 0755 et notices 0644. Le manifeste A est ci-dessous ; G garde le même périmètre mais ses propres hashes, liés dans la provenance. Aucun système installé.

| Chemin | Octets A | SHA256 A |
| --- | --- | --- |
| `/usr/bin/swayfx-mosaic` | 6760288 | `979dcd95ab43fa1e465d6e9d262485b73d186cedacd0f957059dd24f482ce6f4` |
| `/usr/share/licenses/swayfx-mosaic/INCORPORATED-NOTICES` | 255102 | `cf69048aad394c4d3e3dc875c1b9aae1922946af861fec18e337f0b45aacd7fb` |
| `/usr/share/licenses/swayfx-mosaic/SceneFX-LICENSE` | 1096 | `ffd3737a478b83a8b51b42757d3bf909ef36694508355879722e11fc1fa6736b` |
| `/usr/share/licenses/swayfx-mosaic/SwayFX-LICENSE` | 1061 | `bd35722bff46327f5eded1d211207277bbe043d2a22048b282c42ef801593b8b` |
| `/usr/share/licenses/swayfx-mosaic/wlroots-LICENSE` | 1140 | `35d427c043dcafe8893b9e7247348f599847c81d9a067703587c80707f3d58df` |

L’inventaire A couvre conservativement 895 inputs, 599 headers, 12 shaders, 7 XML et 282 blocs de notice ; G 894 inputs, 598 headers, 12 shaders, 7 XML, 16 entrées générées et 282 blocs. `parent/package-input-verification.json` a vérifié les 895 hashes A et les cinq fichiers du stage sans mismatch. Ce sont des contributions potentielles de compilation, pas une preuve d’extraction exacte de chaque membre d’archive ni des branches préprocesseur réellement incorporées. Validation humaine juridique et distribution : PARTIAL / NOT QUALIFIED.

`PKGBUILD.future` reste privé, SHA256 `50b098411d1234bc42f1abc748b312ce1be7ada8efe24be7d9ddb29481cba43d`. Syntaxe shell et Python du heredoc, sept inputs sources et allowlist vérifiés PASS. `makepkg --printsrcinfo`, `--verifysource`, build complet et installation : NOT RUN. Recette reproductible au sens d’un dossier d’inputs local contrôlé seulement ; aucune reproductibilité binaire publique ou distribution Arch validée. Le PKGBUILD réel, le patch production et la dépendance système restent inchangés.

H propose surveillance, revue d’impact, rebuild/requalification de toute paire modifiée, notices, stage, décision séparée et rollback. Release maintainer et security reviewer non nommés ; aucun SLA. Voir [décision draft](STEP20C_PRODUCTION_INTEGRATION_DECISION_DRAFT.md).

## Revue finale observée et publication préparée

Revue indépendante finale ACCEPTED / audit PASS pour la fidélité du dossier expérimental : 0 BLOCKING, 4 NON_BLOCKING, 3 FUTURE_SCOPE ; 180 checks hors ligne et 15 mutations de preuves réelles rejetées. Rapport privé `reviews/overnight-final-review.md`, SHA256 `bb4000dffb51b07b59e86f91e8dd76bc2c4f0b9513b48a52c9f6bd6c8c3f45af` ; reçu JSON SHA256 `72ba252092ca3375d344faae1c2026c8d5626fd190e87771d5c0c1ad8212c9b0`. Index scientifique post-exécution `seals/index.json`, SHA256 `cdf034e1f8466a9ae8a0e0a33aa8d0d0195273f0d1bc782667b50c3bcf682505`, contexte de preuve courant, pas un binding pré-exécution.

NB-01 est complété dans l’index compact depuis les grabs wire réels de chacun des huit runs concernés, avec lignes et hashes sources dans `parent/metadata-serial-completion.json`. Les stops fixtures, échecs E3 et incident IPC restent documentés. Les gates lifetime/génération/damage, couverture G, maintenance ABI/paquet/juridique et robustesse/coût des sidecars privés restent ouverts. L’acceptation documentaire ne qualifie pas la production et n’applique aucune décision. Publication préparée, pas encore exécutée à cette édition ; les refs/SHAs finaux et le résultat de publication feront foi dans le reçu privé et le handoff final.
