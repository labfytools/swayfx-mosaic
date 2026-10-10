# STEP20A — fondation Spatial Canvas native

> **Historical implementation report (native compositor foundation).** This report preserves the original French validation record and reflects the state at that step. For current behavior and decisions, use the [documentation index](README.md), [architecture](ARCHITECTURE.md), [UX contract](UX.md), and [known limitations](KNOWN_LIMITATIONS.md). Canonical documentation takes precedence if a historical statement is stale.

## Base et provenance

- Installation protégée : paquet Arch `swayfx 0.6-1`, binaire `/usr/bin/sway`, `swayfx version 0.6 (based on sway 1.12.0)`. `pacman -Qkk swayfx` : 58 fichiers, aucun altéré.
- Source amont : `https://github.com/WillPower3309/swayfx`, tag `0.6`, commit `fd71a6bdc061bd633b488ae7b83e8a6981d22f86` ; la branche `master` courante n'a pas été utilisée.
- Bibliothèques installées : `wlroots0.20 0.20.2-1` (`pkg-config wlroots-0.20` : `0.20.2`), `scenefx 0.5-1` (`pkg-config scenefx-0.5` : `0.5.0`). Le tag demande `wlroots-0.20 >=0.20,<0.21` et `scenefx-0.5`.
- Le cache AUR local contient un `PKGBUILD` **0.5.3-4**. Le dépôt AUR distant, commit `55c2e27f83e54eadd9d811bc123b868e6ba56866`, contient **0.6-0**, alors que le paquet local est **0.6-1** ; celui-ci a donc une recette ou révision locale qui n'est plus disponible ici. Les métadonnées du paquet ne contiennent pas son archive source ni son commit. La correspondance binaire exacte au commit du tag n'est donc pas démontrable. Le tag `0.6` est la base vérifiable qui reproduit la version annoncée et se compile avec les dépendances installées.
- Options Arch pertinentes reprises : `-Dwerror=false -Dsd-bus-provider=libsystemd`, avec les bibliothèques système ci-dessus. `-Dwerror=true` échoue aussi sur une incompatibilité amont avec `libinput 1.32.0` : le `switch` de `sway/ipc-json.c` ne traite pas `LIBINPUT_CONFIG_SCROLL_CIRCULAR`.

## Baseline avant modification

```sh
meson setup build-baseline -Dwerror=false -Dsd-bus-provider=libsystemd
meson compile -C build-baseline -j 8
meson test -C build-baseline --print-errorlogs
build-baseline/sway/sway --version
```

Résultat : build PASS, binaire répond `swayfx version 0.6-fd71a6b ... (based on sway 1.12.0)`. Meson indique `No tests defined.` pour l'amont. Aucune installation système.
La baseline binaire reste dans `build-baseline/sway/sway`, SHA-256 `5c377fdd5b6f72d343699dd1949956dfa73fe08b7c5dd305c45a5bb020bd8ccb` ; elle a été construite avant la première modification fonctionnelle et n'a pas été reconstruite depuis.

## Validation du fork

```sh
meson setup build-mosaic -Dwerror=false -Dsd-bus-provider=libsystemd \
  -Dprefix=/usr -Dbindir=bin -Dswaybar=false -Dswaynag=false \
  -Dman-pages=disabled -Ddefault-wallpaper=false
meson compile -C build-mosaic -j 8
meson test -C build-mosaic --print-errorlogs
python tests/headless-ipc.py
meson install -C build-mosaic --destdir /tmp/step20a-stage
git diff --check
```

Résultat : build PASS ; modèle `1/1 PASS` ; headless IPC et six fenêtres Kitty PASS ; installation de staging limitée au binaire ; `git diff --check` PASS. La validation de la configuration quotidienne par `/usr/bin/sway -C -c /home/fy59/.config/sway/config` retourne 0 ; wlroots y écrit deux diagnostics EGL `EGL_BAD_ALLOC`, sans démarrer de session ni invalider la configuration.

## Carte des points d'insertion

| Couche | Fichier/fonction | Rôle et point d'insertion |
| --- | --- | --- |
| Arbre | `include/sway/tree/container.h`, `workspace.h` | Enum de layout, workspace et listes `tiling`/`floating` ; état Mosaic attaché au workspace. |
| Insertion/suppression | `sway/tree/workspace.c:workspace_add_tiling`, `sway/tree/view.c:view_map`, `sway/tree/container.c:container_detach` | L'ordre de `workspace->tiling` fait autorité pour Row0. Insertion après le dernier actif, nettoyage de la référence de focus à la sortie. |
| Géométrie logique | `sway/tree/arrange.c:arrange_workspace`, `apply_horiz_layout` | Calcule `pending` et les tailles des enfants. En STEP20A, Mosaic emprunte le calcul horizontal standard. |
| Transaction/scène | `sway/desktop/transaction.c:arrange_children`, `arrange_workspace_tiling` | Applique l'état `current`, reparent les scènes et positionne les containers. Le nouvel enum doit passer ici également. |
| Output/rendu | `sway/desktop/output.c` (`wlr_scene_output_build_state`) | Composition de la scène dans le buffer d'output. |
| Clipping | `sway/tree/view.c:view_center_and_clip_surface`, `sway/desktop/transaction.c:arrange_container` | Clip de contenu au rectangle d'une vue, pas un clip général du viewport Mosaic. |
| Hit testing | `sway/input/cursor.c:node_at_coords` | Interroge `wlr_scene_node_at` ; toute translation de caméra devra conserver la correspondance avec la scène interactive. |
| Focus/move | `sway/commands/focus.c`, `move.c`, `sway/input/seat.c:seat_set_workspace_focus` | Navigation directionnelle, réorganisation et dernier focus par ligne ; aucune nouvelle touche n'est câblée ici. |
| IPC | `sway/ipc-json.c:ipc_json_describe_workspace`, `ipc_json_layout_description`, `sway/ipc-server.c` | `get_tree` publie `layout: "mosaic"` ; `get_workspaces` et les événements continuent par les chemins Sway existants. |
| Parser | `sway/commands/layout.c:cmd_layout` | `layout mosaic` active explicitement le mode sur le workspace ; les layouts classiques restent disponibles. |

## État réalisé

```text
Workspace 1 (layout=mosaic, opt-in)
└── Row0 (children emprunte workspace->tiling)
    ├── A
    ├── B
    └── C
    scroll_x = 1200 (coordonnée logique, non rendue en STEP20A)
    focused = B
active_row = 0
```

`mosaic_workspace_state` possède les objets `mosaic_row`, jamais les containers Sway. Row0 emprunte `workspace->tiling`, sans copie de l'ordre. Les autres lignes ont leur propre liste dans le modèle et sont vérifiées par test unitaire ; leur branchement à l'arbre, aux transactions et à l'IPC attend une tranche ultérieure. Un `scroll_x` négatif ou non fini est refusé. Changer le focus ou `scroll_x` ne réordonne pas les enfants. L'état est libéré avec le workspace et reste dormant si l'on repasse à un layout classique.

La première ligne reste tiled et non flottante. Le test headless a observé `A B C`, puis `A X B C` après focus de A et création de X, puis `A X B` après fermeture de C. Un `move right` suivi de `move left` garde Mosaic actif et permet ensuite d'insérer Y immédiatement après X. Après retour à `splith`, Mosaic peut être réactivé sur un workspace occupé et la nouvelle fenêtre s'insère encore après A. Le test vérifie aussi des rectangles sans chevauchement et `floating_nodes=[]`. Ce n'est **pas** encore une ligne plus large que le viewport ni un POC graphique scrollable : aucun ratio de largeur de cellule n'a été fixé.

## Exécution et coexistence

Le fork produit `build-mosaic/sway/swayfx-mosaic`. L'option Meson `mosaic-package=true` installe seulement ce binaire. La vérification `meson install -C build-mosaic --destdir /tmp/step20a-stage` n'a produit que `/tmp/step20a-stage/usr/bin/swayfx-mosaic`. Le paquet Arch futur pourra dépendre des bibliothèques communes et déclarer ce seul chemin ; il ne doit déclarer ni `provides=sway`, ni `conflicts=swayfx`, ni installer les fichiers `/etc/sway`, `swaymsg`, `swaybar`, les complétions ou la session `sway.desktop` déjà possédés par SwayFX. Une session dédiée, sous un autre nom, sera une étape ultérieure. Aucun fichier de `/usr` n'a été modifié ici.

Activation dans le seul processus du fork : `swaymsg -s <socket-du-fork> 'layout mosaic'`. Le socket explicite est essentiel en test : une commande envoyée à la session quotidienne n'active rien dans le fork. La session actuelle n'a pas été relancée ou rechargée.

## Compatibilité et limites

- IPC : `get_tree` annonce `mosaic` sur le workspace, en conservant les noeuds Sway et leurs identités. `get_workspaces` et les événements utilisent les chemins existants. Les clients qui traitent les layouts comme un enum fermé doivent ajouter `mosaic` avant de restaurer ce workspace.
- QuickShell : les vues générales IPC peuvent lire l'arbre ; `session_v2/schema.py` limite explicitement `LAYOUTS` à `splith`, `splitv`, `tabbed`, `stacked`, et `session_v2/snapshot.py` a aussi une condition sur les layouts à un enfant. STEP20E devra représenter les lignes, l'ordre, `active_row`, `scroll_x` et le focus de chaque ligne, avec des identités stables de fenêtres et un ordre de restauration défini. Aucun fichier QuickShell n'a été modifié dans STEP20A.
- Scratchpad, floating et fullscreen : les chemins Sway existants sont conservés. Le test vérifie le tiling normal, mais ne constitue pas encore une validation exhaustive des transitions scratchpad, floating et fullscreen sous Mosaic.
- Clavier : `$mod+Alt+m` ouvre Applications. `$mod+Alt+l` est libre et réservé au futur sélecteur de layout, sans commande factice. Son ancien usage Applications a été retiré. Le bind `limusic-app` qui occupait `$mod+Alt+m` a été supprimé ; son autostart reste en place. `$mod+s`, `$mod+Shift+w`, `$mod+e` restent inchangés. Aucun reload de la session actuelle n'a été déclenché.

## Risques et STEP20B

La scène wlroots peut positionner les noeuds indépendamment de leur ordre logique. Le moteur d'output compose déjà la partie visible dans le buffer physique, mais un vrai viewport Mosaic doit définir une translation de caméra et un clip **par workspace/ligne** pour éviter qu'une portion hors viewport apparaisse sur un autre output. Le clip existant des surfaces ne fournit pas cette frontière. Le hit testing utilise la scène ; l'offset visuel et les rectangles des commandes `focus`/`move` doivent rester cohérents. La transaction distingue `pending` et `current` et possède des animations : le déplacement de caméra doit être appliqué au bon instant, sans saut ni divergence IPC. Les changements d'output, de taille et de workspace doivent recalculer le viewport sans perdre `scroll_x`.

STEP20B doit livrer une première ligne réellement plus large que son viewport, scrollable par une commande native explicite, avec largeur temporaire isolée et configurable sans imposer de politique UX finale. Il doit relier géométrie logique, translation de scène, clip, input et focus directionnel ; couvrir les transactions et les changements de workspace/output par tests headless. Le modèle des lignes supplémentaires sera raccordé après la preuve d'une ligne utilisable.
