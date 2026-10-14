# STEP20C — matrice étendue release-shape

> EXPERIMENTAL — édition du 2026-10-14, clôture documentaire des quatorze runs ciblés, diagnostic C3 inclus. Revue finale indépendante : ACCEPTED, audit PASS pour la fidélité de l’évidence expérimentale. Publication documentaire autorisée et préparée, non exécutée à cette édition. Le diagnostic C3 est exécuté : résultat INCONCLUSIVE, observations natives partielles sans transfert à A/G. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED. Multi-output de production : NOT YET SUPPORTED. Aucune intégration, installation ou décision UX.

L’autorité brute est le LAB privé `/home/fy59/swayfx-mosaic-targeted-7gge6h8b` ; HIST désigne `/home/fy59/swayfx-mosaic-overnight-mcolx0gq`. Les chemins LAB/HIST sont des artefacts externes locaux, pas des fichiers distribués. Le [rapport de clôture](STEP20C_TARGETED_CLOSURE_DECISION.md) donne les identités exactes, la matrice des quatorze runs et les limites. Les sources de [fixture ciblé](../../tooling/probes/step20c-targeted/README.md) restent des entrées expérimentales ; elles n’ajoutent aucune dépendance de production. Les rapports historiques et leurs verdicts restent inchangés.

## Résultats graphiques propres à G

G possède son propre SHA et n’hérite d’aucun PASS de A. Le smoke horizontal historique reste historique ; les nouveaux runs sont scale-G, saved-G, FX-G, input-G et les trois cellules ci-dessous.

| Run G ciblé | PNG | Grabs wire A/B | Observations retenues | Verdict architecture |
| --- | ---: | --- | --- | --- |
| G-dynamic-G | 14 | 42/51 | resize 960 puis800, migration H1→H2→H1, quatre étapes et input frais | PARTIALLY_FEASIBLE |
| G-hidden-G | 12 | 61/70 | même hiérarchie conservée, owner pleinement caché/clip vide/aucun enter, retour et clic B | FEASIBLE pour l’échantillon |
| G-R90-G | 9 | 35/44 | transform R90 réel, mode physique750×1000, scale1,25, logique800×600, PNG1000×750/markers | FEASIBLE pour l’échantillon |

Le dynamique mesure de nouveaux clics toplevel lorsque `popup_done` a fermé la chaîne ; aucun popup n’est recréé. Il ne prouve pas une chaîne grabbed persistante durant chaque migration. R90 conserve B visible, exclusion du bouton interdit, dismissal et H2 final exact. Les mesures de ces trois runs sont PASS ; chaque résultat runtime reste INCONCLUSIVE (IPC terminal1), processus 0 et scientific cleanup PASS distincts. Standard return n’est pas exercé dans cette allocation. Les résultats saved/input/FX partiels figurent dans leurs rapports dédiés.

## Instrumentation résiduelle et ABI exacte

G a retiré26 statements OPT et des helpers orphelins ; il conserve listener commit, logs present, boucles scène/owner/popup et clocks. L’absence de nouveau lock/référence/allocation dans les callbacks PI est un audit source ; logging peut bloquer/allouer. `fx_framebuffer_bind(pass->buffer)` reste avant la branche failed, avec ordre différent de pristine. Cette neutralité est **INCONCLUSIVE**, pas garantie par les seize images A/G exactes.

La paire locale est SceneFX 0.5 commit `37ccd723bef49e6891156ffafce8f549f01446cc` et wlroots 0.20.2 commit `d783533489e1f75d6886c2ab5c5960090ef268f8`, bibliothèque SHA `7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`. Les121 headers sont inchangés et chaque nouveau run possède ses propres maps. Aucune SceneFX shared séparée n’y est mappée. Les17 structs/six offsets égaux et85 exports chevauchants sont des checks nécessaires :34 bindings retenus, 31 vers l’exécutable/trois vers wlroots. Ils ne prouvent ni incompatibilité ni safety complète ; toutes autres paires **NOT QUALIFIED**.

## Package privé, notices et maintenance

LAB `parent/package-audit.json` rapporte `bash -n`, sept checksums, `makepkg --printsrcinfo`, `makepkg --verifysource` et `git apply --check` des deux patches PASS sur copies privées locales. Aucun réseau/install ; full `makepkg` build **NOT RUN**. Les stages A/G contiennent exactement cinq fichiers réguliers sans symlink : binaire mode755, quatre notices mode644 sous `/usr/share/licenses/swayfx-mosaic/`. DT_NEEDED ne contient pas SceneFX shared. Le PKGBUILD courant reste inchangé ; aucune distribution n’est validée.

LAB `parent/abi-maintenance.json` vérifie les hashes de notices et inventories conservateurs895/894 entrées A/G, 894/893 chemins uniques (un doublon chacun). `testlog.junit.xml` recensé est un résultat de test, pas du code incorporé. Sept C changent A/G et `opt_probe.h` est retiré ; cette comparaison ne prouve pas l’incorporation exacte par préprocesseur ni les membres réellement extraits des archives. Suffisance des licences : **HUMAN_REVIEW_REQUIRED**.

La responsabilité projet SceneFX embarqué est déjà approuvée pour le candidat privé. Release maintainer et security reviewer restent à nommer, sans noms/SLA inventés. Avant distribution : veille/impact des fixes, pins source+hash, rebuild paire exacte, tests ABI/graphique/lifetime/clip/damage, notices et stage, puis décision distincte de publication. Standard SwayFX reste indépendant et fallback ; aucun système d’update, dépendance ou politique d’installation nouveau n’est adopté. Ces gates prolongent le contrat privé existant sans modifier Packaging/Upstream/Development.
