# SWAYFX_MOSAIC_STEP20C_REBUILD_FROM_GIT_COREC_OOM_GPU_NIGHT_SHIFT_V1

2026-10-15. Dossier expérimental de décision, distinct du
[ticket historique bloqué](STEP20C_COREC_PREALLOCATION_NATIVE_AND_GPU_PRECISION.md)
et du [plan de provenance V2](STEP20C_COREC_V2_PROVENANCE_AND_PLAN.md).
Les contrats canoniques gardent leur autorité. Aucun résultat de ce dossier
n'adopte une politique de production.

Disposition : **PRIVATE_COREC_V2_NEEDS_TARGETED_EVIDENCE**.
Recommandation OOM : **C_FURTHER_NATIVE_REVIEW**.
Availability production : **UNDECIDED**.
Résultat global : **PARTIALLY_ADVANCED**.

```text
STEP20A = DONE
STEP20B = EXPERIMENTAL
STEP20C = NEXT
STEP20D–G = PLANNED
PRODUCTION_MULTI_OUTPUT = NOT_YET_SUPPORTED
PRODUCTION_AUTHORIZED = FALSE
```

## 1. Provenance nouvelle et persistance Git

Le début du ticket était `339dda45bc81b953e2f0afadf28765149e3a1ba1`,
sur `main` propre. Le nouveau candidat s'appelle **COREC_V2_REDERIVED**.
Il reconstruit des sources natives complètes depuis les objets Git survivants
et les sources publiques épinglées. Les anciens arbres privés, binaires CORE/
CORE-C/G1, hooks et captures supprimés restent **MISSING_NOT_RECOVERABLE** ;
aucune égalité avec leurs anciens SHA n'est affirmée. Leurs résultats restent
**HISTORICAL_REPORTED_ONLY**. Les échecs et budgets du ticket précédent restent
inchangés.

| Élément | Identité exacte | Rôle |
| --- | --- | --- |
| Mosaic parent | `cd550382b311efdbfe3ed892f4e1d281d852e754` | Parent Git de reconstruction |
| Arbre parent Mosaic | `6be2d6cada19bd84673c30dfc4fb900a48b87e86` | Vérification des modes et octets |
| SceneFX | `37ccd723bef49e6891156ffafce8f549f01446cc` | Source publique épinglée |
| Arbre parent SceneFX | `685a78b94f9e44ee683e5fea93874557a9fed457` | Vérification des modes et octets |
| SwayFX pristine | `fd71a6bdc061bd633b488ae7b83e8a6981d22f86` | Contrôle indépendant, pas le checkout modifié |
| wlroots source | `d783533489e1f75d6886c2ab5c5960090ef268f8` | Audit source, non modifié |
| wlroots partagé SHA256 | `7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837` | Fournisseur exact qualifié localement |
| Patch CORE SceneFX SHA256 | `6039799046d052bb4cf2b15fbeb132983d6e3c1a45ad63752a6a63e83b585627` | Delta cumulatif privé |
| Patch CORE Mosaic SHA256 | `9eb6afac0be5c747fbf1a1ee5a33a633c193c4ebae0a36b17636abde7a64c879` | Delta cumulatif privé |

Le [kit source-only](../../tooling/probes/step20c-corec-v2/README.md) conserve
patches, assemblage, vérification, clients, tests, schémas, budgets et recettes.
Il ne contient ni copie complète d'upstream, ni bibliothèque, ni binaire,
capture, arbre de build ou socket. Ses suppléments OOM/GPU sont séparés du CORE
fonctionnel et portent leurs propres manifests de parents et résultats.

Les commits source-only suivants étaient publiés normalement sur `origin`
(Forgejo) puis `github`, avant les runs qui en dépendaient :

- `1053ab2a47f8ff0ab5d52fb0cba92c5dba4ad531` : kit CORE reconstructible ;
- `c0a822a0799ef024727b4a51a7442b8626223a69` : fixtures headless revues ;
- `bf00b0b0ed3e20bfb7c68d2fbbe6553594f3167a` : diagnostics OOM/G2 revus.

Le kit publié à bf00b0b0 compte 105 fichiers, environ 1,18 Mo ; les reçus
de clôture et le correctif du test offline sont conservés ensuite séparément. La reproduction depuis
une archive Git vierge (`results/git-next-kit-reproduction.json`) vérifie les
octets et modes des arbres CORE SceneFX/Mosaic 85/417 fichiers, OOM 86/417,
GPU SceneFX 87 ; une reconstruction CORE indépendante avec fetch public avait
déjà été acceptée. Cela prouve **EXACT_FOR_NEW_TREE**, sans garantir un binaire
reproductible bit à bit. La [recette de build](../../tooling/probes/step20c-corec-v2/BUILD_RECIPE.md)
décrit les prérequis et les limites.

La publication documentaire a été vérifiée directement sur origin puis github
au commit `9d4e7942f5a45b4be37ba75682cd146a58295659`. Son extraction Git
vierge reproduit aussi CORE/OOM/GPU exactement et passe 48 tests offline.
Le closeout externe scelle l'inventaire final et la présente mise à jour
administrative, sans référence circulaire à son propre futur SHA. Le contrôle système pré-final confirme
les huit hashes protégés, le PID Sway quotidien 2325, son exécutable
`/usr/bin/sway` et son startticks 2833 inchangés par lecture seule. Tous les
PIDs privés vérifiés sont absents ; aucun `/tmp/smx-*` ne reste. Les huit
premières entrées du ledger sont structurellement identiques aux reçus initiaux.
Les observations de publication sont conservées dans
evidence/documentary-publication.json ; elles portent sur ce commit réellement
interrogé, pas sur un SHA futur.

## 2. Contrat technique V2 et audit C

SwayFX garde l'autorité sur arbre, focus, caméra, transactions, scène, input et
IPC ; Row 0 emprunte `workspace->tiling`. Le nouveau delta privé garde les
popups root dans leur couche native globale, dérive leur clip de l'owner tiled
CURRENT et laisse les descendants nested hériter. Le leaf réellement caché
reçoit un clip vide ; les ancêtres CURRENT fullscreen sont parcourus ; les
retours standard/floating/fullscreen retirent le clip supplémentaire. Aucune
UX hide/dismiss/reposition ni promesse de click-through universel n'en découle.

Option C : la factory réserve le sidecar avant `scene_tree_init` et avant toute
publication. L'échec libère l'arbre non publié et retourne NULL. Le setter
n'alloue pas ; NULL désactive en conservant la réservation ; une boîte vide
reste active et masque rendu/input. Les réservations inactives sont ignorées
par get/render/hit ; destroy retire et libère une seule fois. Un root embedded
non réservé est explicitement rejeté par abort, même avec NDEBUG. Ce rejet de
précondition n'est pas le traitement OOM de la factory.

L'audit inspecte 294 références / 16 symboles, avec ownership, premiers usages,
NULL, rollback et listeners. Les callers du compositor et les helpers wlroots
épinglés sont couverts ; tinywl/examples non liés restent hors qualification.
Les réparations expérimentales sont bornées à l'admission/back-pointer IME,
refocus/rollback, premier usage nullable de dim-rect, admission image-capture
XDG et destruction partielle output/workspace/view/seat. Aucun layout public
de struct ni signature publique ne change. Les translations/intersections
utilisent des bornes larges avant narrowing ; la conversion caméra vérifie
finite/range avant conversion.

Mesures natives : arbre 128 octets, sidecar 64 octets pour **chaque arbre de
factory**, y compris inactif et non Mosaic. Lookup linéaire ; overhead de
l'allocateur et coût global/performance **NOT MEASURED**. Trois traces passives
restent déclarées (`SPIKE_CLIP`, `PROBE_POPUP_CLIP`,
`PROBE_POPUP_HIDDEN_OWNER`) ; leur neutralité temporelle est **NOT_PROVEN**.
NULL et zéro actif peuvent produire la même ligne de log. `SPIKE_DAMAGE` et
les hooks PI/OPT sont absents du CORE fonctionnel.

Les corps C exacts sont liés aux SHA complets et offsets de slices ; types
natifs, signaux Wayland et régions Pixman sont réels. Les adapters de damage/
visibility/effects restent explicitement des adapters : ils ne prouvent pas
le moteur natif. Normal C17, UBSan (dont float-cast/signed overflow/bounds),
ASan+UBSan ont réussi dans le périmètre borné. Les dix mutants compilent tous
et sont tous tués par un oracle exécuté. Les échecs de setup et la correction
du harness root-return restent archivés ; aucun échec de compilation ne compte
comme mutant tué. Le corpus OOM supplémentaire couvre 27 cas dans trois modes,
six mutants causaux et neuf négatifs supplémentaires ; il étend le même
harnais H1, sans campagne sanitizer H2 full-compositor.

Dix cores systemd précoces (2 261 704 octets sous gestion système hors LAB) et
huit événements journal-only ont précédé le correctif de dumpability. Ils n'ont
été ni supprimés ni manipulés avec sudo. RLIMIT_CORE seul était insuffisant
avec le handler pipé. Le harnais final vérifie PR_SET_DUMPABLE=0 et
PR_GET_DUMPABLE ; l'audit final des corpus n'observe pas de nouvelle entrée.
Il serait faux d'affirmer zéro écriture hors LAB pour les premières exécutions.

## 3. Trois couples privés et staging

| Couple | SHA256 du compositor | Build ID |
| --- | --- | --- |
| CORE | `91f48aae2675331e0a2c60ec2fedf983745c521c75232c704a6516a4140801fb` | `d5d304533f2c8db9d738365e9bd7f2c96779ef8d` |
| OOM | `6067946bd79ad6fd8da7669ab9b0b3bacfd2638f5d3d8382002b9118db20d835` | `9bc3dc9055106b343c80a51ded111a382e98442d` |
| GPU | `b2ba890908e385b0a8884e786b279bfb2e582eed38c7fcd0587b418326eca5bc` | `b6a52111beabe3c2122e0142a802415d3c84f9a5` |

Chaque couple a sa revue ELF/build et son DESTDIR privé de cinq fichiers :
binaire distinct et quatre notices sous `/usr/share/licenses/swayfx-mosaic/`.
SceneFX est statique ; wlroots partagé est le fournisseur exact ci-dessus.
Les revues vérifient symboles privés, layouts, archives, relocations, absence
de SceneFX DT_NEEDED et absence de RPATH/RUNPATH. Les traces loader sont
distinctes des mappings `/proc` observés au runtime. L'acceptation vaut pour
ces octets, pas pour une future paire simplement proche en version.

Le premier build CORE rencontre un nouvel enum libinput sous Werror ; la
recette privée utilise `-Wno-error=switch`, garde le warning et ne modifie pas
le C. Le premier build GPU échoue sur la déclaration de realpath ; la
configuration privée `-Dc_args=-D_XOPEN_SOURCE=700` définit la macro
`_XOPEN_SOURCE=700` et résout ce problème, sans edit C.
Ces tentatives restent dans leurs réservations de couples ; elles ne sont
pas cachées par le succès ultérieur. Trois couples / trois stages consommés ;
aucun package installé, aucune modification du vrai PKGBUILD ou du patch
production. Notices : **LEGAL_NOT_APPROVED** ; makepkg/distribution ne sont
pas qualifiés par ces stages.

## 4. Matrice native des 14 cellules prévues

P0/P1 utilisent le contrôle pristine qualifié séparément (SHA256
`b7fa32116e3c42706b9b02da7df12f27e76d82dd253deb8bdec81519eed145f6`).
C1–C8 utilisent uniquement CORE ; O1/O2 uniquement OOM ; G2 uniquement GPU.
Une réservation reste consommée après refus ou échec ; aucun retry.

| Run | Binaire | Objet | Statut scientifique | Captures / cap réservé |
| --- | --- | --- | --- | --- |
| P0 | pristine | Contrôle standard horizontal | PARTIALLY_FEASIBLE | 10 / 10 |
| C1 | CORE | Horizontal, nested grabs, retours standard | PARTIALLY_FEASIBLE | 16 / 18 |
| C2 | CORE | Vertical | PARTIALLY_FEASIBLE | 8 / 12 |
| C3 | CORE | Scale fractionnaire | PARTIALLY_FEASIBLE | 9 / 12 |
| C4 | CORE | R90 | PARTIALLY_FEASIBLE | 9 / 12 |
| C5 | CORE | Owner caché, même chaîne, retour | PARTIALLY_FEASIBLE | 12 / 12 |
| C6 | CORE | Configure retenu, timeout naturel, retour live | PARTIALLY_FEASIBLE | 10 / 12 |
| C7 | CORE | Resize/migration dynamique | INCONCLUSIVE | 10 / 14 |
| P1 | pristine | Non-leaf fullscreen et débordement réel | PARTIALLY_FEASIBLE | 10 / 10 |
| C8 | CORE | Comparaison non-leaf fullscreen | INCONCLUSIVE | 0 / 12 |
| O1 | OOM | Première réservation root-popup ciblée | INCONCLUSIVE | 6 / 8 |
| G2 | GPU | Première acquisition A, arrêt strict | INCONCLUSIVE | 2 / 16 |
| O2 | OOM | Deuxième réservation ciblée | NOT_RUN — dépendance O1 fermée | 0 / non réservé |
| R1 | aucun | Discriminant conditionnel | NOT_RUN — non admis | 0 / non réservé |

Total réconcilié : **12 runs lancés une seule fois / 14 maximum ; 102 captures
output / 180 ; somme des caps réservés 148 / 180**. Les deux PNG source-marker
générés pour C3/C4 ne sont pas des captures output. Le snapshot intermédiaire
`phase-status.json` est désormais réconcilié à 12 runs / 102 captures. Son
ancien état 8 runs / 84 captures est préservé dans
`results/resume-audit/phase-status.json.before` et
`results/phase-status-before-closeout.json`, sans modifier les anciens reçus.
Maximum
par run : 18 captures et 150 secondes ; build `-j8` maximum. Une seule campagne
sanitizer H1 sur deux autorisées ; pas de H2 full-compositor. L'espace restant
dans un budget ne constitue pas une admission à rejouer une cellule consommée.

## 5. Mesures graphiques et refus conservés

P0 fournit le contrôle standard, avec serial/grab réels, popup root/nested et
débordement standard. Les tests du nouveau CORE ont leurs propres chaînes
wire, points visibles/interdits, captures et retours. La première revue native
vérifie 28 paires wire/input et 30 fermetures pour P0/C1–C7. Les retours H2
finaux sont exacts dans les échantillons acceptés ; un H2 standard contenant
encore des popups débordants ne doit pas être comparé à un baseline vide.
Les contrôles pristine propres à scale et rotation sont **NOT TESTED**.

C2 conserve son ancien champ brut X0 `NOT_EXERCISED` ; l'annotation séparée
confirme que l'oracle exécuté utilise l'axe Y à 600, avec A 505..675 et
B 585..715. Aucun raw historique n'est réécrit. C3/C4 couvrent les cellules
scale/R90 échantillonnées, sans qualification universelle de transformations.
C5 garde les mêmes identités et grabs : origin owner -1456 entièrement cachée,
puis retour -318 sans outside click ni dismissal provoqué.

C6 retient configure39 après ACK30, mesure la cible 636×513, observe le
timeout natif 5000 ms avec une transaction waiting1, puis ACK39 tardif, retour
live et fermeture normale. L'identité du buffer saved natif est **NOT_PROVEN** ;
ces événements ne prouvent ni génération atomique ni lifetime GPU.

C7 reste INCONCLUSIVE : la fixture calcule un clamp attendu 800 après
migration, mais le focus natif de la cellule 10 (bornes logiques 1280..1920,
viewport 800) impose 1120. Le déplacement appelle réellement le refocus ;
l'oracle l'omet. Les étapes resize antérieures sont mesurées ; pixels/input
post-migration et retour arrière ne sont pas atteints. Aucun défaut CORE n'est
établi par cette divergence. Préserver le raw et corriger prospectivement la
fixture ne permettrait pas de requalifier ce run consommé.

P1 forme réellement un groupe non-leaf avec deux enfants de largeur 400,
groupe fullscreen 800×600, A `[-448,105,900,170]` et
B `[-348,165,900,130]`. Les captures whole-H2 mapped, A-only et baseline final
sont vérifiées exactement. C8 laisse le peer sibling du workspace, hors du
groupe qui ne contient que l'owner ; le guard refuse avant capture. La
comparaison P1/C8 fullscreen est donc **NOT_EXERCISED**, même si P1 seul est
informatif. Pas de promesse d'exemption fullscreen native qualifiée.

## 6. OOM : faits natifs et limite de l'oracle

O1 injecte le premier échec sidecar sur le root-popup ciblé par PID/nonce et
rôle natif, sans épuiser la mémoire réelle. Les compteurs natifs mesurent
`matched=1 failures=1 successes=0 initialized=0 listeners=0 published=0
children=0`, puis retour NULL. Le même compositor survit : snapshots et IPC
ultérieurs, captures pré/post, boutons du voisin serial42/43. Whole-H2 pré/post
est exact ; le chemin ne publie pas de scène partielle dans cet échantillon.
Le disconnect `no_memory` n'est **pas observé**.

L'owner ferme A puis TOPLEVEL, sans B créé. L'oracle commun attend soit
B/A/TOPLEVEL, soit TOPLEVEL seul et rejette cette séquence root-only. Les
processus sortent pourtant tous à 0, sans rescue ; CLOSE_RECEIVED, EXIT error0
et SHM1/1 sont présents. Les deux captures finales prévues sont absentes.
**Scientific cleanup=false**, runner 1, budget et statut **INCONCLUSIVE**
restent immuables ; la fermeture mécanique correcte ne répare pas le verdict.
Le terminal IPC rc1 pendant teardown, avec compositor rc0, décrit la fermeture
de l'endpoint et ne prouve pas un bug de shutdown.

La fonction availability vérifie par code PID/exécutable/mappings après
injection avant le snapshot ; son retour n'est pas archivé car la sauvegarde
finale a été sautée. Les `proc-maps` conservés sont ceux du startup : ne pas
les présenter comme archive post-injection complète. Survie native bornée
observée ; disponibilité générale, damage complet et absence universelle de
stale listeners **NOT_PROVEN**. O2 reste **NOT_RUN**, sa gate dépendant d'un
O1 complet ; les injections unitaires de deuxième réservation ne remplacent
pas O2 natif.

| Choix | Availability / fail-closed | Coût et callers | Preuve / décision |
| --- | --- | --- | --- |
| A abort | Arrêt du process ; fail-closed par sa mort | Allocation au setter ; callers inchangés | Historique source ; recovery non prouvé |
| B bool + masque | Recovery à décider ; masque fail-closed à qualifier | Réservation par arbre clippé ; 11 setters/admission à traiter | Harnais historique, pas nouvelle qualification native |
| C préallocation | NULL avant publication ; survie O1 bornée observée | Sidecar pour chaque factory, lookup linéaire ; audit create/rollback | V2 natif partiel ; **C_FURTHER_NATIVE_REVIEW** |

Cette recommandation technique ne choisit pas la politique production :
**COREC_V2_AVAILABILITY_POLICY=UNDECIDED**.

## 7. G2 : observabilité partielle et arrêt conforme

Les nouveaux hooks et sources G2 sont revus séparément ; aucun hook G1 perdu
n'est revendiqué. Le shader de calcul est inchangé à la revue source. La
première acquisition A atteint point0, puis refuse strictement avec
`GLES_STATE_NOT_SUPPORTED` : EGL `client_version=2`, tandis que GL_VERSION
annonce `OpenGL ES 3.2 Mesa 26.2.4-arch1.1`. Le contrat figé exige les deux
prédicats. Il n'est pas assoupli après observation. B et A-return ne sont pas
armés, aucun retry, zéro fichier / zéro octet raw GPU ; seuls deux baselines
H2 exacts sont capturés. Les processus sortent tous à 0 sans rescue ; cleanup
scientifique et mécanique est observé.

Les métadonnées natives observées décrivent un DMA-BUF 800×600, format
`875713112`, modifier `020000001046bb04`. Plane0 stride3584 offset0 ; plane1
stride1024 offset2293760. Les FDs sont borrowed ; fstat réussit sur le même
inode. Cela ne prouve pas la longueur d'allocation ; un plan auxiliaire DCC
ne reçoit pas un prédicat de stride d'image inventé. FBO/RBO/texture et objets
natifs sont identifiés, sans preuve du contenu présenté.

`g2_drain` préliminaire, `glGetString(GL_VERSION)` et drain de query ont été
exécutés ; `pre_errors` et `query_errors` sont vides. En revanche le refus
précède sauvegarde/bind/read/restauration : `read_errors` / `restore_errors`
vides et champs before/after à zéro sont des valeurs initialisées, **pas**
des observations de lecture ou restauration. Aucun `READ_SUCCESS`, bits
d'uniformes ou halfpixel effectif natif n'est observé. L'attribution des
erreurs de readback et la neutralité GL ne sont pas prouvées. Les drains sont
intrusifs : ils consomment les erreurs et ne restaurent pas la queue.

GL observability reste **PARTIAL**. Les tests offline de modifier, framing,
uniform/precision et négatifs valident les outils dans leur périmètre ; ils
ne fournissent pas les valeurs natives manquantes. Pas d'epsilon ajusté, pas
de fit CPU pour transformer le refus en succès. Whole-H1 A/A-return nouveau
**NOT_PROVEN** ; le FAIL whole-H1 historique reste historique, non rejoué et
non effacé par une ROI centrale. Causalité whole-field GPU **NOT_PROVEN**.

## 8. Input, damage, commit/present et lifetime

| Propriété | Preuve V2 | Limite |
| --- | --- | --- |
| Applied/input | Géométries CURRENT, points wire et pixels stabilisés échantillonnés | PARTIALLY_FEASIBLE ; pas d'atomicité générale |
| Damage échantillonné | H2 et retours exacts aux états capturés | PARTIALLY_FEASIBLE ; toutes les frames non couvertes |
| Damage complet / stale pixels | Pas de couverture exhaustive | NOT_PROVEN |
| Commit/present natif | Pas de clé native commune instrumentée dans CORE | NOT_PROVEN |
| Identité exacte du buffer physique présenté | Pas de lien V2 readback/commit/present | NOT_PROVEN |
| Buffer saved natif | Configure/timeout/ACK observés, identité absente | NOT_PROVEN |
| GPU completion / fences / lifetime | Aucun signal effectif mesuré | NOT_PROVEN |
| Génération atomique transaction/scène/input | Aucun compteur adopté ou prouvé | NOT_PROVEN |

Les compteurs historiques 57/55/2, 821/789/32 et 414/400/14 sont **REPORTED**,
sans replay depuis les LAB supprimés. Aucun appariement entre runs par
proximité temporelle ni aucun héritage d'une instrumentation ancienne.
Décorations, ombres, blur/cache et saved buffers complets restent des gates
indépendantes, malgré les pixels stabilisés favorables.

## 9. Revues, sévérité et décisions restantes

Les revues indépendantes source/C, CORE build, fixtures/admission, OOM source/
build, GPU source/build/portable et les deltas fullscreen/FIFO sont liées à
leurs manifests et hashes. Le kit conserve les reçus compacts sous
`reviews/` ; le LAB garde les preuves détaillées. Les tests négatifs directs
rejettent notamment mauvais SHA, mauvais fournisseur wlroots, archive
dynamique, source stale, ancienne destination LAB et bindings incorrects.
Les révisions source invalident l'avis précédent pour les octets modifiés ;
une acceptation source/offline ne vaut pas admission native.

La première revue runtime (`review-oom-runtime/runtime-receipt.json`) garde
P0/C1–C6 partiels et C7 inconclusif. La revue
`review-remaining-runtime/early-receipt.json` garde P1 partiel, C8/O1
inconclusifs et O2 fermé. La décision G2 dépendante autorise seulement le
diagnostic indépendant après examen de l'absence de défaut commun critique
démontré ; elle n'upgrade pas O1. La
[revue finale runtime](../../tooling/probes/step20c-corec-v2/reviews/remaining-runtime-final-review.json)
accepte la vérification bornée du protocole d'arrêt G2 et de la comptabilité
(SHA256 `3372e0ba9f7b33da4fbc041dc4eea97ccc000fb1a9cf809b189c29c90b510569`).
Elle maintient G2 INCONCLUSIVE et toutes les limites de phase I. La revue
globale indépendante est désormais ACCEPTED, sans finding BLOCKING ; elle
confirme la disposition NEEDS_TARGETED_EVIDENCE et la recommandation C, sans
production. Son reçu est conservé dans le kit sous reviews/final-global-review.json.

| Priorité | Constat | Correction ou preuve de clôture | Responsable |
| --- | --- | --- | --- |
| P0 | Aucun nouveau défaut critique commun démontré dans les revues bornées | Ne signifie pas sûreté globale | Non assigné |
| P1 | Availability OOM production, damage complet, lifetime/présentation, GPU whole-field ouverts | Décision de politique et preuves natives ciblées | Non assigné |
| P2 | C7 omet refocus migration ; C8 ne forme pas le groupe comparable ; O1 oracle root-only incompatible | Correctifs prospectifs source-only et tests directs ; nouveau budget séparé pour run futur | Non assigné |
| P3 | Coût mémoire/performance, overhead allocator, neutralité des traces et portabilité future | Mesures/requalification dédiées | Non assigné |

Il n'y a pas d'autorisation de nouveaux runs dans cette clôture. Le plus petit
pas ultérieur justifié est une revue native C ciblée et des corrections
offline des trois fixtures P2, suivies seulement si autorisées d'une nouvelle
tranche de preuves ; pas STEP20D ni intégration production.

## 10. ABI, licences, maintenance et rollback

Les règles de [maintenance upstream](../UPSTREAM.md) et de
[packaging](../PACKAGING.md) restent applicables. Toute nouvelle révision
SceneFX/wlroots, shaders, dépendances, layout/symboles, clip/damage ou lifetime
exige impact review, rebuild, relocation/stage et nouvelles qualifications
pertinentes. Aucun autre couple n'est qualifié par proximité de version.
Le projet doit assurer veille de sécurité et rebuild du SceneFX embarqué si
une future décision l'adopte ; les responsables maintenance, sécurité et
release sont **non assignés**, sans SLA inventé.

Le stage de notices n'est pas une validation juridique : **LEGAL_NOT_APPROVED**.
Les licences/notices exactes et la décision de distribution restent à revoir
humainement. Le paquet actuel garde uniquement son binaire distinct ; aucun
`provides`, `conflicts` ou `replaces` avec Sway/SwayFX. SwayFX ordinaire doit
rester indépendamment actualisable et utilisable comme fallback. Le rollback
préparé consiste à revenir au binaire/paquet Mosaic antérieurement qualifié ou
au SwayFX standard, en conservant les manifests ; aucun rollback live n'est
exécuté. Il ne faut ni remplacer `/usr/bin/sway`, ni bibliothèque système,
session, dotfiles ou configuration QuickShell.

## 11. Stockage, conservation et purge sélective non exécutée

LAB conservé : `/var/tmp/swayfx-mosaic-corec-v2-i516p6po`, hors HOME. Le diagnostic
initial distingue EDQUOT dans `/tmp` et écriture possible sous `/var/tmp` ;
TMPDIR/TMP/TEMP et caches sont redirigés par `run-env`. Le cap généré est
18 Gio, alerte 12 Gio. Le relevé pré-final mesure LAB 677 228 967 octets
(environ 646 Mio), SSD libre 279 665 819 648 octets (environ 260 Gio),
`/tmp` libre 1 610 719 232 octets (environ 1,50 Gio). Il ne prétend pas être
un maximum historique mesuré. Aucun LAB sous HOME ; le header source
transitoire a été régénéré à l'identique, préservé puis retiré. Les sockets
privés utilisent de petits `/tmp/smx-*` retirés
après les runs. Les premières commandes de build utilisaient le wrapper TMP
mais l'absence de variables de session héritées n'est pas prouvée pour toutes
ces commandes ; aucun consommateur IPC quotidien n'a été observé.

Une suppression future du LAB ne doit plus supprimer le code reconstructible.
Procédure préparée, **non exécutée** : vérifier les trois commits publiés,
reconstruire/vérifier dans un second répertoire vierge, garder manifests,
reviews, ledger et closeout à préserver ; identifier les seuls répertoires
générés dispensables appartenant à l'UID et vérifier leurs realpaths sous ce
LAB ; supprimer sélectivement uniquement après demande explicite, puis
relever espace et inventaire restant. Ne pas lancer de suppression globale,
suivre de symlinks, supprimer les cores système ou toucher aux sources Git.
Les anciennes preuves perdues ne sont pas récupérées par cette procédure.

## 12. Marqueurs du ticket

Les PASS suivants désignent les gates bornées réellement validées, jamais
STEP20C production. L'audit HOME/protections pré-final et la revue globale indépendante sont
acceptés. La publication documentaire est liée aux observations directes des
deux remotes au commit 9d4e7942 ; les reçus de clôture conservent le SHA final.

```text
COREC_V2_STORAGE_GATE=PASS
COREC_V2_GIT_GATE=PASS
COREC_V2_RECONSTRUCTION_FROM_SURVIVING_SOURCES=PASS
COREC_V2_SOURCE_EQUIVALENCE=EXACT_FOR_NEW_TREE
COREC_V2_PLAN_AND_PROVENANCE_REVIEW=ACCEPTED
COREC_V2_FULL_SOURCE_REBUILD=PASS
COREC_V2_OPTION_C_CALLSITE_AUDIT=PASS
COREC_V2_SOURCE_FORWARD_APPLY=PASS
COREC_V2_NATIVE_C_SANITIZERS=PASS
COREC_V2_PRIVATE_BUILD=PASS
COREC_V2_PRIVATE_ELF_ABI=PASS
COREC_V2_PRIVATE_STAGE=PASS
COREC_V2_BUILD_REVIEW=ACCEPTED
COREC_V2_GRAPHICS_OFFLINE_PREFLIGHT=PASS
COREC_V2_STANDARD_COMPARISON=PARTIALLY_FEASIBLE
COREC_V2_HORIZONTAL_RETURN=PARTIALLY_FEASIBLE
COREC_V2_VERTICAL=PARTIALLY_FEASIBLE
COREC_V2_FRACTIONAL=PARTIALLY_FEASIBLE
COREC_V2_R90=PARTIALLY_FEASIBLE
COREC_V2_HIDDEN_SAME_CHAIN=PARTIALLY_FEASIBLE
COREC_V2_SAVED_NATURAL_TIMEOUT=PARTIALLY_FEASIBLE
COREC_V2_DYNAMIC=INCONCLUSIVE
COREC_V2_FULLSCREEN_COMPARISON=NOT_EXERCISED
COREC_V2_NATIVE_OOM_PREFLIGHT=ACCEPTED
COREC_V2_OOM_FIRST_ALLOCATION=INCONCLUSIVE
COREC_V2_OOM_SECOND_ALLOCATION=NOT_RUN
COREC_V2_AVAILABILITY_POLICY=UNDECIDED
COREC_V2_GPU_SOURCE_REVIEW=ACCEPTED
COREC_V2_GPU_METADATA_OFFLINE=PASS
COREC_V2_GPU_GL_OBSERVABILITY=PARTIAL
COREC_V2_GPU_RUNTIME=INCONCLUSIVE
COREC_V2_GPU_WHOLE_FIELD_CAUSALITY=NOT_PROVEN
COREC_V2_APPLIED_INPUT_COHERENCE=PARTIALLY_FEASIBLE
COREC_V2_NATIVE_COMMIT_PRESENT=NOT_PROVEN
COREC_V2_SAMPLED_DAMAGE=PARTIALLY_FEASIBLE
COREC_V2_COMPLETE_DAMAGE=NOT_PROVEN
COREC_V2_NATIVE_BUFFER_IDENTITY=NOT_PROVEN
COREC_V2_GPU_COMPLETION=NOT_PROVEN
COREC_V2_ATOMIC_GENERATION=NOT_PROVEN
COREC_V2_REPRODUCIBLE_KIT=PASS
COREC_V2_INDEPENDENT_REVIEW=ACCEPTED
COREC_V2_DOCUMENTARY_PUBLICATION=PASS
COREC_V2_HOME_CLEAN=PASS
SWAYFX_MOSAIC_STEP20C_REBUILD_FROM_GIT_COREC_OOM_GPU_NIGHT_SHIFT_V1=PARTIALLY_ADVANCED
```

`COREC_V2_HOME_CLEAN=PASS` désigne l'absence de LAB/caches lourds sous HOME
et le contrôle pré-final ; il n'efface pas les cores système précoces déclarés.
La revue globale indépendante est ACCEPTED, sans finding BLOCKING. Le reçu
reviews/final-global-review.json est matérialisé explicitement par le parent
depuis le retour structuré du reviewer en lecture seule.

## 13. Réponses aux seize questions imposées

**Q1. Reconstruction sans ancien LAB ?** Oui, pour cette nouvelle dérivation :
Git et sources publiques épinglées suffisent ; vérification exacte des octets
et modes. Les anciens octets perdus ne sont pas restaurés.

**Q2. Véritables create NULL traités ?** Audit source/C accepté pour les callers
du compositor et helpers épinglés concernés, avec rollback et premiers usages.
Les exemples non liés restent hors périmètre ; cela ne garantit pas tout OOM
du compositor.

**Q3. Zéro scène/listener/exposition avant publication ?** Oui dans les tests
exacts et le failpoint root O1 observé (`initialized/listeners/published=0`).
Pas de généralisation à tous sites possibles.

**Q4. Survie privée à l'injection ?** Oui observée pour O1 : même PID, IPC,
voisin serial42/43 et sorties 0. Le run reste INCONCLUSIVE pour l'oracle de
fermeture ; O2 natif non exécuté.

**Q5. Régression damage/rendu/hit ?** Pas de régression démontrée dans les
échantillons qualifiés ; damage complet, effets et disponibilité générale
restent NOT_PROVEN. Une absence de défaut échantillonné n'est pas une garantie.

**Q6. Qualification propre au nouveau SHA ?** Oui, C1–C6 fournissent les
échantillons horizontal/vertical/scale/R90/hidden/saved et retours ; statuts
PARTIALLY_FEASIBLE, contrôles scale/rotation dédiés NOT TESTED.

**Q7. Fullscreen vraiment comparable ?** P1 pristine oui pour le non-leaf
mesuré ; C8 échoue à construire le même groupe avant capture. Comparaison
CORE/pristine NOT_EXERCISED.

**Q8. Même chaîne hidden ?** Oui, C5 conserve IDs et grabs sans outside click
entre dissimulation et retour ; portée bornée à cette chaîne.

**Q9. Saved configure/timeout/live/close ?** C6 observe hold39, timeout naturel,
ACK tardif, live et close. Identité native saved buffer NOT_PROVEN.

**Q10. GPU nouveau et revu ?** Oui, sources/hooks G2 nouveaux, revues propres,
binaire GPU distinct ; premier A refusé, aucune usurpation de G1.

**Q11. DCC/halfpixel sans prédicat inventé ?** Métadonnées réelles par plan,
pas de fausse borne allocation ; halfpixel natif non observé à cause du refus.
Pas de tolérance apprise après coup.

**Q12. Attribution GL et interférence ?** Drains pré/version exécutés et vides ;
lecture/restauration non atteintes, donc pas de preuve read-success/error queue
pour ces étapes. Les drains consomment la queue, interférence explicitée.

**Q13. Whole-H1 A/A-return égal ?** Non mesuré en V2 : B/A-return non armés.
Causalité whole-field NOT_PROVEN ; FAIL historique conservé sans replay.

**Q14. Cohérence effectivement mesurée ?** Input/applied et damage stabilisé
partiels ; commit/present natif, buffer physique, GPU completion/lifetime et
génération atomique NOT_PROVEN.

**Q15. Code survivant à la suppression de /var/tmp ?** Oui pour les patches,
scripts et fixtures publiés et reproduits depuis Git. Les captures et logs
volumineux privés ne sont pas garantis survivants sans conservation séparée ;
le LAB n'est pas supprimé.

**Q16. Décisions humaines restantes ?** Availability OOM production ; UX popup
offscreen hide/dismiss/reposition ; acceptation juridique des notices ;
responsables maintenance/sécurité/release et décision de distribution ;
admission d'une future tranche native et intégration éventuelle. Toutes restent
ouvertes ; aucun statut production n'est adopté par ce dossier.
## 14. Validation documentaire et état de clôture

Cette édition documentaire ajoute seulement le présent dossier et de courts
renvois dans README documentaire, Architecture, Known Limitations, Roadmap,
Development, Upstream et Changelog. UX, Packaging, AGENTS, production,
PKGBUILD et patch cumulatif ne sont pas modifiés par cette rédaction.
`git diff --check` réussit ; 348 liens locaux des huit documents sont résolus,
les 43 marqueurs et les seize réponses imposées sont présents. La première
assertion de comptage documentaire omettait R90 dans sa regex sans chiffres ;
le contrôle corrigé compte les 43 noms exacts, sans changement de résultat.
Cette rédaction n'a exécuté aucun build, test runtime, commit ou push.

La validation de clôture du parent trouve initialement 1 échec sur 48 tests
offline : le test d'environnement utilisait le chemin O1 réel désormais muni
d'un token consommé. Il ne s'agit pas d'un run O1 supplémentaire. Une
correction bornée du test vers son propre répertoire OFFLINE_TEST_ONLY donne
48/48 tests réussis ; sa revue de delta indépendante est acceptée. Le vrai
jeton O1 et le ledger sont inchangés, le jeton factice existant est refusé.
L'échec initial reste conservé. Les reçus reviews/offline-post-run-delta-review.json
et reviews/final-global-review.json sont matérialisés explicitement par le
parent depuis les retours structurés des reviewers en lecture seule. La revue
globale est ACCEPTED sans blocage ; la publication documentaire est vérifiée
au commit 9d4e7942. Le scellement externe conserve ensuite l'inventaire final.

Les autres validations finales transmises à cette édition réussissent : AST
des 43 Python, C17 fullscreen/G2, cinq bindings, manifests historiques
54/105, budget immuable et diff-check. Les nouveaux fichiers de preuves et
la correction offline du parent sont visibles séparément dans le worktree ;
ils ne sont pas des changements effectués par cette rédaction documentaire.
