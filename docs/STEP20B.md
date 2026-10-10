# STEP20B — première ligne Mosaic scrollable

> **Historical implementation report (first scrollable row).** This report preserves the original French validation record and reflects the state at that step. For current behavior and decisions, use the [documentation index](README.md), [architecture](ARCHITECTURE.md), [UX contract](UX.md), and [known limitations](KNOWN_LIMITATIONS.md). Canonical documentation takes precedence if a historical statement is stale.

## Contrat et base

Base source : SwayFX tag `0.6`, commit `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`. La correspondance byte pour byte au paquet local `swayfx 0.6-1` reste invérifiable faute de source de sa révision de paquet ; voir [STEP20A](STEP20A.md). Le fork est toujours compilé contre `wlroots-0.20` et `scenefx-0.5`. SwayFX standard conserve `/usr/bin/sway` et son cycle de mise à jour. Aucun paquet système n'a été installé.

Le dépôt de travail conserve une branche contenant la source complète. Le fichier `patches/0001-mosaic-layout-viewport.patch` rassemble le delta de production à appliquer uniquement sur le commit indiqué. `PKGBUILD` contrôle le commit avant application et ne fournit que `/usr/bin/swayfx-mosaic`. Il ne déclare aucun `provides`, `conflicts` ni `replaces` pour SwayFX. Une nouvelle version upstream exige une adaptation manuelle du patch et une nouvelle validation ; ne jamais réutiliser automatiquement le patch 0.6 sur 0.7.

## Fonctionnement natif

- `layout mosaic` active le layout du workspace courant. Le mode reste inactif par défaut.
- `layout toggle mosaic` bascule entre Mosaic et le dernier layout standard propre à ce workspace. Les commandes standards `layout ...` restent reconnues. Les raccourcis historiques `$mod+s`, `$mod+Shift+w` et `$mod+e` restent en place.
- `layout mosaic scroll <signed pixels>` déplace la caméra logique de Row0 ; la valeur est bornée entre zéro et le dernier pixel du canvas. Le focus directionnel ramène une cellule focalisée dans le viewport. Aucune combinaison clavier supplémentaire de scroll n'a été inventée.
- Row0 emprunte directement `workspace->tiling` : les noeuds restent de vrais conteneurs tiled dans l'arbre Sway. `pending`/`current` portent la géométrie logique au delà de l'écran ; la scène du tiling est translatée de `-scroll_x`. Le hit testing suit les coordonnées de la scène. `get_tree` conserve les champs Sway et ajoute `mosaic: {active_row, rows:[{children, scroll_x, focused}]}` seulement en mode Mosaic.
- La largeur minimale temporaire d'une cellule est 640 px, isolée dans le modèle (`minimum_cell_width`, zéro signifie 640). L'espace disponible est réparti si cela donne des cellules plus larges. Cette valeur n'est pas une politique UX finale ni une commande publique.
- Quand `layout tabbed` ou `layout stacking` a créé un seul conteneur racine autour des fenêtres d'un workspace occupé, l'entrée dans Mosaic promeut ses enfants dans Row0. La sortie restaure le layout standard au niveau du workspace. Les sous-arbres plus profonds restent des conteneurs groupés et sont une unité de Row0.

Exemple :

```text
Workspace 1 (layout=mosaic, previous_standard_layout=tabbed)
└── Row0, active_row=0
    ├── A  [0,640)
    ├── B  [640,1280)
    ├── C  [1280,1920)
    └── D  [1920,2560)
    scroll_x=400, focused=B
```

Les coordonnées ci-dessus sont illustratives, sans gaps Sway. La sortie physique ne rend que sa surface ; sur la machine mono-écran `eDP-1`, cela fournit une ligne effectivement scrollable. Le test headless capture deux images PPM avant/après `scroll 400` et observe un changement substantiel de pixels sans changement d'ordre ou des rectangles logiques IPC.

## Clavier et compatibilité standard

Dans les dotfiles partagés, `$mod+Alt+m` lance `applications-quickshell` et `$mod+Alt+l` appelle `~/.local/bin/labfy-layout-toggle`. Le helper n'a aucun état : il envoie `layout toggle mosaic` au socket du compositor courant. Sous SwayFX standard, la commande non reconnue n'altère pas le workspace et le helper retourne proprement. Le test headless séparé sur `/usr/bin/sway` vérifie le maintien de `splith`. La session actuelle n'a pas été rechargée ; le nouveau bind ne sera pris en compte qu'au prochain chargement normal de configuration.

QuickShell n'a pas été modifié. `session_v2` a encore un ensemble fermé de layouts standards ; STEP20E devra enregistrer l'ordre des conteneurs, les lignes, `active_row`, chaque `scroll_x`, le focus de chaque ligne et une identité durable pour restituer les fenêtres. L'IPC garde les événements Sway et `get_workspaces` habituels ; les lecteurs stricts de `get_tree.layout` devront reconnaître `mosaic`.

Floating, fullscreen et scratchpad suivent les chemins Sway existants et ne sont pas déplacés par la caméra du tiling. Le test couvre le tiling, la suppression, l'insertion, `move`, le focus, les transitions standard/Mosaic, ainsi qu'un aller-retour `floating`, `fullscreen` et `move scratchpad`/`scratchpad show`. Les interactions prolongées avec plusieurs outputs demandent encore une campagne dédiée avant publication générale.

## Limites et risques à traiter avant publication

- SceneFX 0.5 n'expose pas de clip générique pour un `wlr_scene_tree`. La sortie physique crope le canvas sur cette configuration mono-écran, mais une ligne traversant la frontière d'un output adjacent pourrait y apparaître. Le support multi-écran nécessite un clip de scène par viewport ou une stratégie de rendu équivalente, avec hit testing cohérent. Ce point bloque une publication générale multi-écran.
- Le déplacement de caméra est immédiat. L'animation courte et continue demandée pour le produit reste à implémenter sans diverger des transactions `pending/current` ni des animations de workspace.
- Le changement de taille et le déplacement de workspace vers un autre output recalculent la limite de scroll via le nouveau viewport ; le modèle garde la coordonnée tant qu'elle reste valide. Une validation de ces chemins et des transitions fullscreen est encore nécessaire.
- Les groupes imbriqués restent des cellules entières. La politique finale d'aplatissement, de largeur et de reflow multi-ligne est à fixer après la preuve d'une seule ligne.
- `minimum_cell_width` et `scroll_x` restent bornés par les coordonnées `int` de la scène. La capacité pratique au delà d'environ 2 milliards de pixels logiques n'est pas prise en charge par cette tranche.

## Validation locale

```sh
meson compile -C build-mosaic -j 8
meson test -C build-mosaic --print-errorlogs
MOSAIC_HELPER=/home/fy59/.local/bin/labfy-layout-toggle python tests/headless-ipc.py
meson install -C build-mosaic --destdir /tmp/step20b-stage
git diff --check
```

Le build de référence amont et ses résultats sont conservés dans STEP20A. Aucune relance ou reload de la session quotidienne n'a été effectué.

## STEP20C proposé

Introduire un clip de viewport correct par workspace, y compris lorsque deux outputs sont adjacents, puis valider rendu, hit testing et drag aux frontières. Ajouter l'animation de caméra et des tests headless couvrant resize d'output, bascule fullscreen, floating, scratchpad et changement de workspace. Définir ensuite la politique UX de largeur sans transformer la valeur temporaire de STEP20B en API durable.
