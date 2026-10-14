# G1 — diagnostic factuel du rejet DMA-BUF

Statut : **INCONCLUSIVE — lecture seule**, limité au rejet du seul epoch 1.
Ce document n'accepte ni les pixels bruts ni le résultat GPU. Aucun run,
rebuild, revalidation du ticket, test, analyse numérique ou reconstruction de
contenu masqué n'a été effectué pour cet audit.

## Constat

`gpu-field/validate.py::validate_object` exige `p[0] >= 800*4` pour **tous**
les plans DMA-BUF (`validate.py`, ligne 46), puis rejette sous le message
`dmabuf fields`. Le writer `gpu-field/scene/render/fx_renderer/gpu_field_private.h::gf_object`
(lignes 198–213) sérialise chaque plan comme `[stride, offset]` à partir de
`wlr_dmabuf_attributes.stride[]` et `offset[]`; `dmabuf_available` provient de
`wlr_buffer_get_dmabuf`.

Dans chaque échantillon 0–8 de `gpu-field/runtime/epoch-1.meta`,
`dmabuf_available=true`, la taille est `[800,600]`, deux plans sont présents,
et le modifier comporte 16 caractères. Les plans sont toujours
`[[3584,0],[1024,2293760]]`. Le premier plan passe le contrôle stride
(3584 ≥ 3200); le second le fait échouer (1024 < 3200). C'est le premier
prédicat de `dmabuf fields` et la cause immédiate démontrable du rejet.

| Point | Échantillon | DRM format décimal / rôle | Plans [stride, offset] | Champ fautif |
|---:|---|---|---|---|
| 0 | main-before-blur | 875713112 / main | [[3584,0],[1024,2293760]] | stride plan 1 = 1024 < 3200 |
| 1 | down-0 | 875708993 / effets | [[3584,0],[1024,2293760]] | idem |
| 2 | down-1 | 875708993 / effets | [[3584,0],[1024,2293760]] | idem |
| 3 | down-2 | 875708993 / effets | [[3584,0],[1024,2293760]] | idem |
| 4 | up-2 | 875708993 / effets | [[3584,0],[1024,2293760]] | idem |
| 5 | up-1 | 875708993 / effets | [[3584,0],[1024,2293760]] | idem |
| 6 | up-0 | 875708993 / effets | [[3584,0],[1024,2293760]] | idem |
| 7 | cache-after-copy | 875709016 / cache | [[3584,0],[1024,2293760]] | idem |
| 8 | output-presubmit | 875713112 / main | [[3584,0],[1024,2293760]] | idem |

Les formats correspondent aux constantes du validateur : 875713112 = XR24
(XRGB, accepté pour main), 875708993 = AB24 (ABGR, accepté pour effets), et
875709016 = XB24 (XBGR, accepté pour cache). Le rejet n'est donc pas une
absence de DMA-BUF ni un format de rôle inadéquat. L'audit n'attribue pas de
cause plus générale à l'instrumentation ou au pilote.

## Portée des preuves

Résumé `gpu-execution/G1-summary.md` et JSON : 49 artefacts; les 49 chemins et
SHA-256 publiés dans `gpu-execution/G1-summary.json` correspondent aux fichiers
présents. Le manifeste d'arbre porte le SHA-256
`ccd45c0a56c1ee72ff7bcd84711090745012911a7ecc3e0d890aa52ccb715329`.

Pour les artefacts centraux :

- `epoch-1.meta`: 19 686 octets, SHA-256
  `c8ca51bca694db9e21471356a4260064ed81ab7013a88d4edb4b8572044a825c`.
- `epoch-1.rgba`: 8 312 048 octets, SHA-256
  `a6dc7fd873e1ab7e52e04625bacb3251ba8e1aad2e766811efebde7ae7932a99`.
- Métadonnées : 1 begin, 9 sample, 11 write, 2 copy, 1 end; fin native
  `epoch=1 points=9 complete=1`. Ceci établit la publication des métadonnées
  et des octets rapportés, pas leur validité comme lecture GPU.
- `read_success=NOT_PROVEN`; `GL_ERROR_QUEUE=UNOBSERVED`; précision effective
  `UNCERTAIN`. Restauration GL/EGL n'est attestée qu'au moyen des champs
  échantillonnés (`before/after`, contextes, readbuffer); une preuve complète
  indépendante de la restauration n'est **NOT PROVEN**.
- Aucun reçu d'epoch accepté ni analyse n'a été produit. Aucun epoch 2/3 n'a
  été lancé. La valeur byte-count et les SHA prouvent l'intégrité des fichiers
  par rapport au résumé, pas le succès de `glReadPixels`.
- Deux `EGL_BAD_ALLOC` sont enregistrés pendant `eglQueryDevicesEXT`, puis
  l'initialisation Mesa/radeonsi et l'observation DMA-BUF se poursuivent.
  Aucune preuve ne relie ces messages au rejet de métadonnées; aucun lien causal
  n'est affirmé.

## Texte de publication fidèle

« G1 a publié un seul epoch brut, ensuite rejeté par le validateur : son
contrôle exige une stride d'au moins 3200 octets sur chaque plan DMA-BUF, alors
que le second plan rapporté pour les neuf échantillons a une stride de 1024.
Les données restent non acceptées; `read_success` n'est pas prouvé et la queue
GL n'a pas été observée. G1 est INCONCLUSIVE. »

## Empreintes des sources d'interprétation

- `gpu-field/validate.py`: `158a820a2f170cabce37f7b8965ce23c3887cfbced32fecaea4914ea6f423ef7`.
- `gpu-field/scene/render/fx_renderer/gpu_field_private.h`:
  `16f5287c5eb5fb463aef526525631c55e299f5ae860976b46cc0fb901cf1e611`.
- `gpu-execution/G1-summary.json`:
  `fe48671c95a06210768c3addf08b61dbf67efa80953d49b389e3b851687c3d47`.
- `gpu-field/README.md`:
  `df1d6782e5bead9f01d6dbf998c1c47d09ec01bc3e2db0da90975fea14d5c32c`.

## Actions et limites

Lecture/parsing ciblés, `stat`, SHA-256 et comparaison avec les prédicats
source uniquement. Aucun script historique du labo n'a été importé ou lancé.
Pas de modification des sources, des reçus ou des artefacts G1. La seule
écriture est cette note sous `audit/gpu-rejection/`.
