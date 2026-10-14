# Tests unitaires C17 privés — lifecycle et popup

Statut : **EXPERIMENTAL**, preuve unitaire bornée, aucune qualification runtime
compositeur. Les anciens `c-tests`/`c-tests-fixed` restent inchangés.

Reproduction : `python3 run.py` depuis ce dossier. Le runner extrait les slices,
compile normal/UBSan/ASan puis exécute chaque variante sans injection et avec
`--allocation-unavailable`, avec `RLIMIT_CORE=(0,0)`. `commands.json` conserve
argv, codes bruts et overrides sanitaires ; chaque commande possède stdout et
stderr bruts. Le runner échoue si un code diffère de 0, sauf l'injection où il
attend précisément -6 (SIGABRT). Les premières sorties erronées de fixture sont
conservées dans `attempt-1/`.

## Provenance et frontière de fixture

`extract.py` copie des intervalles exacts de bytes, sans réécriture du corps :

- `sidecar.inc` : struct/global/find/remove/destroy et conversion tree-from-node ;
- `setter.inc` : set/get clip ;
- `clip.inc` : translate/intersect/point_inside ;
- `hit.inc` : struct node_at_data et scene_node_at_iterator ;
- `popup.inc` : probe_clip_box_intersection et probe_clip_popup.

`bindings.json` lie chaque intervalle aux SHA-256 du source intégral et de la
slice, offsets byte et lignes source. Les corps compilés sont ces fichiers.
`scene.c` définit uniquement autour de `setter.inc` une macro `calloc` ciblant
`sidecar_calloc`. La première allocation réussit ; l'injection ensuite active
retourne NULL au prochain sidecar. Aucun autre calloc n'est interposé. Aucun
source fonctionnel n'a été modifié, aucune ABI publique n'a été reproduite.

`support.h` expose des structs minimaux ; coordinates/box predicates/list_find,
conversions buffer/rect, scene update et logging sont des supports explicites,
avec commentaires WHY/CONTRACT/INVARIANT. Les coordonnées fixture sont petites,
sans overflow dans le support ; les arithmetic checks étudiés sont les corps
réels extraits. Les listes/listeners et destroy signals sont Wayland serveur
installé, les intersections sont Pixman installé. Ces bibliothèques sont liées
normalement et ne sont pas reconstruites avec sanitizers. Les logs produit sont
no-op ; on mesure les mises à jour, pas le damage/rendu. Les types réduits ne
prouvent ni taille/offset des vrais structs ni compatibilité ABI.

## Couverture réellement exercée

**PASS unitaire** normal, UBSan, ASan (ASan leak detection activée) :

- aucun clip : get false, NULL répété sans mise à jour ni allocation ;
- premier clip puis update : une allocation, une sidecar et un listener,
  box copiée, copie identique idempotente ;
- plusieurs arbres, suppression explicite head, destroy tail puis head,
  toutes sidecars/listeners retirés par les signaux Wayland natifs ;
- clip zéro installé, get true, zéro pixel d'aire positive ; NULL l'enlève ;
- coordonnées parent/child, région intersectée sur X par parent et Y par child ;
- hit permis dans l'intersection, refus hors parent et sous masque zéro avant
  point_accepts_input ; compteur callback vérifié ;
- translation simple, négative dimension et origine/endpoint non représentable
  refusés ; render region sans pixels et input refusé après rejet ;
- vrai probe_clip_popup : owner tiled Mosaic éligible, popup-local viewport,
  ascendance current fullscreen exemptée, pending fullscreen contradictoire
  ignoré, standard sans clip, workspace inactif masqué, owner entièrement
  caché masqué puis retour visible, fullscreen workspace, non-tiled owner,
  clip tiling absent et owner absent ;
- nested node hérite réellement de la sidecar root via point_inside_clip.

Les intersections popup réelles sont exercées par ces branches (dst alias
viewport à l'intersection output, dst séparé à l'intersection owner). La suite
numérique complète/scroll reste dans `c-tests-fixed`, non refaite ici.

## Injection OOM et limite de disponibilité

**CORE_OOM_POLICY=OOM_ABORT_EXPERIMENTAL** : les trois variantes montrent
allocation sidecar réussie puis panne ciblée de la seconde, avec terminaison
brute **-6 / SIGABRT**, core dump interdit. Aucun diagnostic sanitaire précède
l'arrêt volontaire. Ceci vérifie le chemin abort existant, pas la survie du
compositeur, pas un contrat de disponibilité production, pas un état graphique
observable après OOM. La politique production reste ouverte.

## Échec initial et correction de fixture

L'assertion initiale imposait `pixman_region32_not_empty(region)==false` pour un
rectangle nul. Le contrôle indépendant `pixman-diagnostic.c` montre qu'avec le
Pixman installé l'intersection (15,25,0,0) conserve un rectangle dégénéré :
return=1, not_empty=1, extents=(15,25,15,25), contains_point false. Le test final
vérifie qu'aucun rectangle n'a largeur ET hauteur positives. Aucun corps extrait
n'a changé. Cet échec initial de fixture n'est pas une panne produit.

## NOT TESTED / NOT EXERCISED

Aucune création réelle de scènes via l'API intégrale, aucun parcours complet
scene_node_at/scene_nodes_in_box, aucune transaction generation, surface XDG,
grab/serial/protocole popup, cycle natif root/nested popup, rendu/GPU, damage,
décoration/FX/saved buffer, taille/offset ABI, mutation concurrente ou shutdown
compositeur. Le listener est émis réellement mais node storage est stack fixture,
non destruction de l'arbre intégral. Rien ici ne ferme une cellule runtime.

STEP20A=DONE ; STEP20B=EXPERIMENTAL ; STEP20C=NEXT ;
STEP20D–G=PLANNED ; PRODUCTION_MULTI_OUTPUT=NOT_YET_SUPPORTED.
Aucun commit/push, aucune modification dépôt/système/session.
