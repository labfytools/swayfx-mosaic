# STEP20C — alternatives OOM privées sur corps C réels

**EXPERIMENTAL, source-only. CORE_PRODUCTION_OOM_POLICY=UNDECIDED.**
Aucune modification production, aucun nouveau build compositeur/SceneFX, aucune
réservation runtime, aucune adoption de politique. Le CORE historique exact
`29baf31aa3eeed259825c87d0799fa5d3dc83710afb967154604eb1c6657f965`
reste inchangé. A reste **OOM_ABORT_EXPERIMENTAL** ; la disponibilité production
est **PRODUCTION_AVAILABILITY_NOT_APPROVED**.

## Reproduction et provenance

Depuis la racine du dépôt, choisir un **nouveau** dossier privé hors Git :

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tooling/probes/step20c-core-recovery/oom/run.py /chemin/prive/nouveau-oom
PYTHONDONTWRITEBYTECODE=1 python3 tooling/probes/step20c-core-recovery/oom/negative.py /chemin/prive/nouveau-oom
```

Le parent historique en lecture seule est
`/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_/`. `prepare.py` exige les hashes
connus des sources complètes, construit trois **copies complètes privées**
`{A,B,C}/scene.c`, `transaction.c`, `scene.h`, puis extrait leurs intervalles
exacts. Les noms complets ne sont jamais ceux du harnais (`harness-scene.c`).
Les sources complètes, slices, binaires et logs restent hors Git. Les petits
patches sans contexte préservés ici sont les deltas exacts des copies privées ; ce ne sont pas
le patch cumulatif production. `sources.json` lie chaque parent, prototype et
patch ; `bindings.json` lie les slices aux sources complètes, offsets et SHA.
Le header B change seulement la déclaration privée void→bool ; aucun header
installé n'est modifié. C conserve le header byte-identique.

Parent scène : `99992429f9a1d2754042989d89904fb6d705f963d74f4456d737fc9da3e0927d`.
Parent transaction : `0b1d31bb8458dceaff34cc2a2987044b3096e6ebc96e68b522c0ac3540bc8ecd`.
Parent header : `bc102f289c905995d142786412e6085c60b8d44d37184d67fa35fdb301c33e2d`.
Les parents viennent du noyau privé minimal figé au ticket précédent, pas des
sources productives du dépôt ni d'un modèle d'allocation réinventé.

## A — arrêt contrôlé

Corps setter, sidecar, destroy, clips, hit et popup **byte-identiques** au parent.
Les injections ciblent uniquement son calloc : première sidecar, ou deuxième
après réussite d'une première sur un autre arbre. Résultat attendu et obtenu :
**-6 / SIGABRT** dans les trois modes normal/UBSan/ASan, `RLIMIT_CORE=(0,0)`.
L'arrêt refuse le fail-open mais tue le processus. Récupération de session,
retour au SwayFX quotidien, réouverture des applications : **NOT TESTED**.
Le test mutant retire abort et exige que cette mutation soit détectée via
sortie99, plutôt qu'un abort artificiel dans le harnais.

## B — bool, masquage synchrone et admission du propriétaire

Le setter exact modifié retourne true pour succès/NULL/idempotence. En OOM,
il appelle le vrai corps `wlr_scene_node_set_enabled(false)` extrait puis
retourne false. Il n'existe donc pas de retour false laissant cet arbre enabled.
Le setter ne réactive jamais l'arbre : le propriétaire conserve l'autorité de
visibilité. Un popup qui a subi OOM reste désactivé même après réussite ou
retour standard ; la récupération de cette disponibilité nécessitera un futur
contrat explicite. Ce compromis privé est intentionnel et n'est pas une UX
popup adoptée.

L'audit trouve **11 appels** setter dans transaction.c : deux pour tiling
(Mosaic/standard) et neuf pour popup (standard/no owner, ancêtre fullscreen
current, non-tiled/workspace fullscreen, inactive/missing clip/coords,
translation/intersection invalides, propriétaire caché, viewport final).
Chaque appel privé vérifie le résultat et retourne sur échec. Le retour
arrange_output n'empêche pas arrange_root d'arranger ensuite les popups ; un
clip tiling absent mène au masque popup. Cette chaîne complète est auditée dans
les sources mais n'est pas exécutée par un compositeur dans ce ticket.

L'audit des enable tiling révèle le risque de réactivation par fading-out
(parent ligne1024) sans nouveau setter. Le helper privé
`probe_clip_enable_tiling(ws, desired)` exige un clip appliqué si Mosaic est
courant. Les demandes active, fading-out et inactive passent par ce helper ;
une installation réussie est suivie d'une admission active explicite.
`desired=false` reste false. NULL standard peut être admis par la demande
upstream suivante ; un clip vide reste un clip valide et masque les hits.
La régression compile le **corps exact du helper** et la **statement exacte de
la branche fading-out**, avec état workspace réduit. Le corps arrange_output
complet n'est pas compilé et la cohérence transaction/animation reste à tester.

Les autres enable de transaction.c concernent des descendants de conteneurs,
fullscreen/floating ou les couches root/output : ils ne réactivent pas le
workspace tiling désactivé. `disable_workspace` désactive seulement. L'audit
`set_enabled` du Sway privé ne trouve pas de réactivation directe du wrapper
popup XDG dans xdg_shell.c ; son arbre interne de surface et les popups IME
sont des arbres distincts. Les animations de workspace passent par
arrange_root/arrange_output. Reparent ne remplace pas l'identité du wrapper ni
son enabled. Ce constat de source n'est pas une preuve universelle de tous les
consommateurs SceneFX possibles ; aucun API général fail-closed n'est annoncé.

Le vrai enabled extrait collecte l'ancienne visibilité avant disabled puis
appelle scene_node_update avec cette région. Le harnais vérifie la transmission
d'une région antérieure non vide au callback réduit. Les changements de clip
réussis gardent scene_node_update du parent. La visibilité/damage réelle,
effects, ancien/nouveau viewport et pixels périmés sont **NOT PROVEN** :
scene_node_visibility et scene_node_update sont des supports, pas le moteur.

## C — réservation sidecar avant publication

Le vrai corps create est modifié dans une copie privée : première allocation
arbre, deuxième allocation réservation ; échec de la seconde libère l'arbre
**avant scene_tree_init**, sans listener ni publication au parent. Après les
deux succès seulement, init publie et le listener de destroy est attaché.
Le setter réutilise cette réservation et ne contient plus d'allocation. NULL
la rend inactive, un zéro reste actif, destroy la libère. Les walkers/get ne
voient que les entrées actives ; une ancienne box inactive ne peut pas devenir
un clip effectif. Un clip nouveau écrase la box avant la mise à jour.

Ce contrat exige des arbres créés par ce create privé. Le root embarqué du
scene n'y passe pas et ne peut pas être donné au setter C ; aucun appel actuel
Mosaic ne clippe ce root. Les chemins de création externes/embarqués et tous
les consommateurs de create doivent être qualifiés avant adoption. Un appelant
qui ne traite déjà pas NULL peut échouer ailleurs : la survie d'une session
complète n'est **pas** acquise par le retour NULL de ce create.

Aucun champ tree/node public n'est ajouté. `bool active` appartient à la
sidecar privée. `memory.c` compile sa déclaration **exacte** avec le vrai
`wlr_box` des headers wlroots0.20 et le vrai `wl_listener` Wayland :
A/B **56 octets par arbre effectivement clippé** ; C **64 octets pour chaque
arbre créé**, même jamais clippé, plus allocations/metadata allocateur non
mesurées. Pointeurs8, box offset16, listener offset32 (A) /40 (C).
La taille tree historique128 n'est pas remesurée ici, et les types réduits de
harnais ne servent jamais de preuve ABI. C ajoute une allocation à chaque
create et retient la mémoire jusqu'au destroy ; coût total proportionnel au
nombre de tous les arbres, non seulement aux fenêtres Mosaic.

## Tests obtenus et frontière de preuve

LAB exécuté : `/home/fy59/swayfx-mosaic-core-recovery-qmhckba5/oom/`.
`commands.json` contient **40 commandes aux codes attendus** : neuf builds
normal/UBSan/ASan, 27 exécutions (defined + injections1/2), deux builds et deux
exécutions de taille sidecar. Tous B/C retournent0. ASan leak detection activée,
UBSan halt-on-error ; aucun diagnostic sanitaire hors arrêts volontaires.
Listes, listeners et signaux destroy sont Wayland natif, régions Pixman natives.
Ce ne sont pas des builds sanitaires du compositeur ni de ces bibliothèques.

A/B réutilisent les tests lifecycle : copie/idempotence, NULL/zéro/retrait,
parent-child, entrée après exclusion clip, destructions parent/child. B ajoute
OOM sans hit descendant et transmission ancienne région, aucune réactivation
implicite, activation/fading/standard admis seulement selon desired/clip.
C teste le vrai create extrait sur chaque allocation, aucune publication ni
listener à l'échec, NULL→clip→zéro→retrait→réinstallation sans allocation,
parent-child, hit et changement de pointeur parent, destroy parent avant child.
Le reparent fixture n'est **pas** le vrai corps reparent/damage.

A/B/C exécutent le vrai probe_clip_popup : current fullscreen ancêtre et
pending contradictoire, standard, workspace inactif, propriétaire complètement
caché puis revenu, fullscreen workspace, propriétaire non tiled, clip tiling
absent et owner absent ; nested hérite le clip root. Les arbres stack de ce
test C reçoivent une réservation par `reserve_fixture`, support explicite et
non preuve du create réel ; celui-ci est vérifié séparément avec allocations.
Aucun XDG/grab/serial réel ni saved-buffer natif n'est exercé. Les saved buffers
héritent le clip tiling par leur arbre selon l'audit historique, pas par une
nouvelle mesure runtime OOM dans ce lot.

`negative.py` compile six mutants puis exige leur rejet : admission ignorée,
abort retiré, false sans masque, réactivation après setter, publication avant
réservation, et clip actif supprimé. Résultats bruts respectifs :
`-6,99,-6,-6,-6,-6`. Ces SIGABRT sont des assertions de régression intentionnelles,
distinctes du crash A. Le premier essai de l'ajout fading extrayait trop de
texte et échouait à compiler ; les commandes/stderr sont préservés dans
`LAB/oom/attempt-4/`. La correction resserre le marqueur à la statement exacte.
Aucun échec de compilation n'est reclassé comme résultat produit.

**CORE_OOM_C_TESTS=PARTIALLY_FEASIBLE** pour ces chemins C.
**CORE_OOM_ALTERNATIVES_REVIEW=NOT_PROVEN**, revue indépendante à acquérir.
**CORE_PRODUCTION_OOM_POLICY=UNDECIDED**.

## Recommandation technique, décision humaine restante

C évite l'allocation au moment de l'exposition et préserve la signature, au prix
de mémoire sur tous les arbres et d'une nouvelle obligation des create callers.
B réduit ce coût aux arbres effectivement clippés et rend l'échec explicite,
avec une signature privée différente, un audit d'admission obligatoire et une
perte de disponibilité locale possible des popups. A est le plus simple mais
transforme une allocation locale en perte du compositeur entier. Préférer
l'étude future de C pour un chemin d'exposition sans allocation, comparer son
coût réel, et garder B comme alternative si l'admission/recovery des owners peut
être qualifiée. Ce conseil ne tranche pas le choix disponibilité/fail-closed.

Prochain plus petit pas : revue indépendante de ces octets puis, sous un futur
ticket explicite, qualification d'un seul choix sur compositeur privé complet :
injections réelles premières/deuxièmes allocations, hide/return et fullscreen,
popups nested avec grabs, saved timeout, reparent/destroy, animations et retour
standard, ancien/nouveau damage à chaque échec, input/applied transaction/present,
pixels périmés/FX, shutdown et récupération session. Aucun de ces tests natifs
n'est autorisé ou annoncé PASS par cette fixture.

STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ;
PRODUCTION_MULTI_OUTPUT NOT_YET_SUPPORTED ; PRODUCTION_AUTHORIZED FALSE.
