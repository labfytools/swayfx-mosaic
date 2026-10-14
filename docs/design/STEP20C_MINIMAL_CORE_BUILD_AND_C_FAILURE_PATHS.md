# STEP20C — build du noyau privé minimal et chemins d'échec C

> EXPERIMENTAL — édition du 2026-10-14. Ticket `SWAYFX_MOSAIC_STEP20C_MINIMAL_CORE_BUILD_RUNTIME_AND_GPU_FIELD_GATE_V1`. Ce rapport consigne uniquement les preuves déjà acquises des phases provenance, C et build privé. ACCEPTED qualifie les revues bornées ; PASS qualifie les contrôles indiqués. Aucun verdict global de la matrice graphique n'est établi ici. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT YET SUPPORTED.

LAB désigne `/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_/`, laboratoire
privé hors Git. Ses chemins désignent des preuves locales accessibles, pas une
distribution autonome ni des artefacts publiés. Le ticket précédent et ses
laboratoires restent historiques et en lecture seule. Le
[rapport source-only historique](STEP20C_MINIMAL_PRIVATE_INTEGRATION_CORE.md)
conserve son état BUILD/C/UBSan/OOM NOT RUN ; les preuves nouvelles ci-dessous
portent sur un nouveau candidat et sa propre identité.

Les [contrats d'architecture](../ARCHITECTURE.md), [UX](../UX.md),
[packaging](../PACKAGING.md) et le
[registre des décisions statiques privées](STEP20C_STATIC_RUNTIME_AND_PACKAGE_CONTRACT.md)
gardent leur autorité. Row 0 emprunte `workspace->tiling` ; le compositeur natif
reste l'autorité de scène, transactions, géométrie et input. Aucun sous-système,
contrat UX popup ou mécanisme de génération atomique n'est adopté par ce rapport.

## Provenance et rejeu du candidat historique

Le dépôt de départ est `main`, commit
`c4bdfb46aadaa4e30a9a05a3238702f56651eec6`, propre lors du contrôle initial.
`LAB/audit/source-replay.json` enregistre le rejeu réel des deux patches minimaux,
les contrôles forward/reverse et l'équivalence SHA256 de 417 fichiers Mosaic et
85 fichiers SceneFX. `LAB/audit/parent-provenance.json` lie les parents aux
archives et conserve l'inventaire historique sélectionné/exclu et ses hashes.
Ces deltas s'appliquent à leurs parents exacts ; le patch Mosaic minimal n'est
pas présenté comme un delta directement applicable au SwayFX pristine.

| Composant | Parent ou identité épinglée |
| --- | --- |
| SwayFX pristine 0.6 | `fd71a6bdc061bd633b488ae7b83e8a6981d22f86` |
| Parent Mosaic privé | `cd550382b311efdbfe3ed892f4e1d281d852e754` |
| Parent SceneFX 0.5 | `37ccd723bef49e6891156ffafce8f549f01446cc` |
| Source wlroots | `d783533489e1f75d6886c2ab5c5960090ef268f8` |
| Bibliothèque wlroots observée | `/usr/lib/libwlroots-0.20.so`, SHA256 `7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837` |

Le dossier historique distingue huit patches fonctionnels et deux patches de
commentaires. Le rejeu conserve clip/input natif, ownership root/nested popup,
hidden-owner guard, retirement/retour standard et lifetime fonctionnelle ; il
n'ajoute pas les instrumentations PI/C3/OPT ni un compteur de génération.
Les quatre statements de log intrinsèques conservés ne prouvent pas leur
neutralité. Le manifeste de provenance reste la référence pour les composants
sélectionnés ; aucun résultat des anciens binaires A/G/GPU ne se transfère.

| Artefact historique source-only | SHA256 |
| --- | --- |
| `LAB/mosaic-minimal.patch` | `af680be7322a9257769cadc137c487b7f9f880a0b0d66df7701ae26b8baf1fe6` |
| `LAB/scene-minimal.patch` | `750337f75f9dc5ca655d3cd10f49bdd04169cca4dc53459d7f0d9eb8ad4db25a` |
| Transaction avant correction caméra | `e5066df7808a1633c635582c052ba89931c2856a54f6b471ff1009a4b455ef6c` |
| Scene privée | `99992429f9a1d2754042989d89904fb6d705f963d74f4456d737fc9da3e0927d` |

## UB caméra réellement reproduite et correction privée

`LAB/c-tests/` compile les corps C extraits et conserve les commandes, sorties,
bindings source et manifeste initial. La suite définie initiale passe avec
177 assertions, mais six reproducteurs UBSan empêchent la qualification C :
NaN, +Inf, -Inf, borne supérieure int64 et valeur sous la borne inférieure
déclenchent `float-cast-overflow` ; INT64_MIN déclenche un overflow signé dans
la soustraction de `workspace_tiling_scene_x`. La portée d'atteignabilité de
ces valeurs dans le compositeur runtime n'est pas démontrée. Ces échecs bruts
restent conservés, sans réécriture rétrospective du verdict initial BLOCKED.

Une correction privée bornée garde le corps fonctionnel existant et vérifie
`isfinite(scroll)` et `INT_MIN <= scroll <= INT_MAX` avant conversion et
soustraction. Les caméras valides gardent la troncature vers zéro et le clamp
final de position. Pour une caméra invalide, l'origine reste non décalée et
le clip vide de la politique existante d'`arrange_output` masque la scène.
Ce garde correspond à la plage déjà employée ; il n'invente pas une politique
UX des valeurs invalides.

| Nouvelle identité privée | SHA256 |
| --- | --- |
| `LAB/camera-boundary-fix.patch` | `adec2cb5dd11c4347c519e13717b9a0744bac8389f277ce85b39fc13df9c459e` |
| `LAB/mosaic-fixed/sway/desktop/transaction.c` | `0b1d31bb8458dceaff34cc2a2987044b3096e6ebc96e68b522c0ac3540bc8ecd` |
| `LAB/audit/candidate-source-freeze.json` | `f2f5c4f4823c0dd33bc2a9085d5eaa114256a2501add0ffd417f8d796728d787` |

La seule différence fonctionnelle de cette réparation est la transaction
privée. `LAB/c-tests-fixed/` enregistre 184 assertions définies, 14 cas
d'intersection sous trois modes d'alias, 12 translations sous deux modes
d'alias et 13 gardes scroll. Normal, UBSan avec `float-cast-overflow` et ASan
passent, y compris les six anciennes valeurs déclenchantes. La revue
`LAB/reviews/camera-delta-review.json` est ACCEPTED pour ce delta : 26 commandes
enregistrées ont un exit zéro ; le reviewer ne lance aucun build/runtime.
Le manifeste initial `c-tests` demeure intact.

## Lifecycle, popup et OOM : preuve unitaire uniquement

`LAB/c-tests-lifecycle/bindings.json` lie cinq slices exactes aux offsets byte,
lignes, SHA256 du source intégral et SHA256 extrait : sidecar/find/remove/destroy,
setter/getter, translate/intersect/point-inside, iterator de hit et
`probe_clip_popup` avec son intersection. Les corps sont copiés sans réécriture.
Les types autour sont réduits ; coordinates, conversions, logging et scene
update sont des supports explicites, dont la mise à jour de scène est stub.
Les listes/listeners/signaux destroy utilisent Wayland serveur installé et les
intersections utilisent Pixman installé ; ces bibliothèques ne sont pas elles-mêmes
recompilées avec sanitizers.

Normal, UBSan et ASan avec détection des fuites passent pour les slices :

- NULL répété sans allocation/update, clip copié et idempotent, zéro installé
  puis suppression NULL ; une sidecar/listener par arbre, retrait explicite et
  retrait via émission native des signaux destroy ;
- intersection héritée parent/child, refus hors clip et sous masque zéro avant
  callback `point_accepts_input`, translation invalide refusée ;
- véritable corps `probe_clip_popup` : propriétaire tiled Mosaic, viewport local,
  ascendance fullscreen **current**, contradiction pending ignorée, standard,
  workspace inactif, owner caché puis visible, fullscreen workspace, owner
  non-tiled, clip absent et owner absent ; héritage nested de la sidecar root.

L'échec initial de fixture est conservé dans `attempt-1/` : Pixman peut retourner
`not_empty=1` pour un rectangle dégénéré d'aire zéro, avec extents
`(15,25,15,25)` et aucun point contenu. Le diagnostic indépendant le reproduit.
Le prédicat final vérifie l'absence de rectangles dont largeur **et** hauteur
sont positives. Aucun corps extrait n'a changé ; cette assertion initiale ne
démontre pas un défaut du source.

L'injection vise exclusivement le `calloc` de sidecar après une première
allocation réussie. Les trois variantes terminent avec le code brut
`-6 / SIGABRT`, `RLIMIT_CORE=(0,0)`, sans diagnostic sanitizer précédant l'arrêt
volontaire. Cela exerce l'abort existant et ne prouve ni survie du compositeur
ni état graphique sûr après panne. La revue OOM conserve l'option A,
`CORE_OOM_POLICY=OOM_ABORT_EXPERIMENTAL`, risque de disponibilité **P1**.
L'abort ne constitue pas une disponibilité production acceptable ni un
fail-closed survivant. Les alternatives B/C ne sont pas démontrées et aucune
signature publique ou politique de remplacement n'est définie ici.

`LAB/reviews/c-prebuild-review.json` accepte le premier build privé non-OOM
pour 502 sources et les bindings finaux, avec `C_gates=PASS_UNIT_ONLY`.
Construction/destruction intégrale de scène, stockage réellement détruit,
protocole XDG/grabs/serials, cycle natif root/nested, render/damage, transaction,
concurrence, GPU et shutdown restent hors preuve unitaire. L'émission native
d'un signal sur un node de fixture en stack ne qualifie pas ces lifetimes.
**Sanitizers unitaires : PASS ; compositeur sanitizer : NOT RUN dans ces phases.**

## Build privé, lien statique et identité ELF propre

`LAB/build-audit/handoff.json` lie le build à la revue acceptée et au manifeste
des 502 sources. Un build initial SceneFX et un build initial Mosaic sont
enregistrés : respectivement 38/38 et 275/275 tâches, exits zéro. SceneFX utilise
`default_library=static`, prefix `/usr`, sans exemples ; Mosaic utilise le
mode package privé, prefix `/usr`, bindir `bin`, sans swaybar/swaynag/man-pages
ni wallpaper. Le `.pc` effectif est celui de `scene-build/meson-uninstalled/` ;
la commande de lien contient `LAB/scene-build/libscenefx-0.5.a`, SHA256
`191ec14fc08c4aeb83e6b313c0f23cda67e10bebe15e29d47bfd192256286f3a`.

Le contrôle syntaxique C17 du header SceneFX privé avec `WLR_USE_UNSTABLE`
passe. `meson test --no-rebuild --print-errorlogs` donne un test Mosaic passé
sur un ; SceneFX termine zéro avec **zéro test défini**. Les avertissements
`LIBINPUT_CONFIG_SCROLL_CIRCULAR` sont conservés dans les logs ; ils n'ont pas
été supprimés pour présenter une compilation sans avertissement.

| Identité du nouveau noyau | Valeur |
| --- | --- |
| Binaire | `LAB/mosaic-build/sway/swayfx-mosaic` |
| SHA256 | `29baf31aa3eeed259825c87d0799fa5d3dc83710afb967154604eb1c6657f965` |
| Build ID | `1b42e557e38db3440ae8dcf7ac967e4132223365` |
| Format / taille / mode | ELF64 / 6 744 472 octets / 0755 |
| SceneFX dynamique | Aucun `DT_NEEDED` SceneFX |
| Chemin dynamique incorporé | Aucun RPATH/RUNPATH |
| Relocations | `ldd -r` exit zéro, aucun symbole non résolu observé |

Ce SHA est distinct des binaires historiques et du diagnostic GPU séparé.
Il qualifie une construction privée BUILDABLE, sans transfert de preuves
graphiques vers ou depuis ces autres binaires.

L'inventaire `LAB/build-audit/new-build-source-inventory.json` dérive des
`compile_commands` et dépendances Ninja : 885 fichiers uniques hashés,
277 unités de traduction, 32 fichiers générés protocoles/shaders. Son SHA256
est `fa9a4e673b77472c34619fd76f692c18cddd9ff1df95eb4c5e8126961ec1fe84`.

Le helper de collecte de provenance a initialement échoué sur
`str has no attribute decode`, après écriture des stdout. La récupération
s'appuie sur ces sorties et un nouveau contrôle `pkg-config --path` enregistré.
L'exit original de l'introspection Ninja reste **NOT RECORDED** dans le handoff.
Une vérification ultérieure distincte et en lecture seule,
`LAB/build-audit/link-command-raw.json`, enregistre exit zéro et présence de
l'archive, avec stdout SHA256
`268ae3f27b8fcfeda63b8d9ab8c70f3c5f50e4fa38660452377056e6e6fa32ca`.
Cette nouvelle observation ne réécrit pas l'exit perdu de la collecte initiale.

## ABI locale et forme du stage privé

`LAB/audit/core-abi-provider-summary.json` résume une capture existante
non graphique `LD_BIND_NOW --version`, exit zéro : 43 bindings pour
40 symboles scène uniques. Les providers et layouts appartiennent à cette
paire exacte ; la résolution forcée ne démontre pas une compatibilité ABI
runtime. Le helper local mesure `sizeof(wlr_scene_node)=112`,
`sizeof(wlr_scene_tree)=128`, offsets parent=8, enabled=32, visible=88 et
children=112. Ces mesures locales ne constituent pas une promesse ABI future.

Un seul stage `LAB/stage1` est enregistré avec `meson install --no-rebuild
--destdir`, exit zéro. `LAB/build-audit/stage1-manifest.json` vérifie exactement
cinq fichiers réguliers, sans symlink ni chemin inattendu :

| Chemin dans DESTDIR | Mode |
| --- | --- |
| `/usr/bin/swayfx-mosaic` | 0755 |
| `/usr/share/licenses/swayfx-mosaic/SceneFX-LICENSE` | 0644 |
| `/usr/share/licenses/swayfx-mosaic/SwayFX-LICENSE` | 0644 |
| `/usr/share/licenses/swayfx-mosaic/wlroots-LICENSE` | 0644 |
| `/usr/share/licenses/swayfx-mosaic/INCORPORATED-NOTICES` | 0644 |

Le binaire stagé possède le même SHA256 que le build. La forme des chemins et
modes passe ; notices **PARTIAL / LEGAL_NOT_APPROVED**. Aucun package complet
`makepkg`, installation réelle ou validation juridique n'est acquis. Les rôles
nommés de release/security, maintenance et requalification des nouvelles paires
restent des gates du contrat privé accepté.

## Frontière de preuve et suite du dossier

Les rapports/reçus `c-tests`, `c-tests-fixed`, `c-tests-lifecycle`, les revues
OOM/caméra/prébuild et `build-audit` conservent commandes, sorties brutes,
manifests et bindings. Leur contenu est consulté ; aucun ancien build, test,
stage ou runtime n'a été répété pour cette rédaction. Les états historiques
FROZEN et SOURCE_ONLY demeurent inchangés.

Les preuves ci-dessus ferment uniquement les contrôles C unitaires indiqués,
la compilation privée, la résolution locale observée et la forme du stage.
GPU lifetime/release/completion, génération atomique scène/input/present,
damage complet et qualifications graphiques pertinentes sont **NOT PROVEN**
par ces phases. Les résultats de la matrice runtime en cours appartiennent à
leur propre dossier ; ce rapport ne leur attribue aucun verdict terminal ni
recommandation globale.

Sources de production, tests du dépôt, API publique, `AGENTS.md`, UX/Packaging,
`PKGBUILD` et patch cumulatif restent inchangés. Aucun commit, push, installation
ou opération sur la session quotidienne n'est effectué par cette rédaction.
La prochaine étape documentaire justifiée est de relier ce rapport aux preuves
runtime réellement terminées lors de la clôture distincte du nouveau ticket,
sans déduire leur résultat de la réussite du build ou des slices C.
