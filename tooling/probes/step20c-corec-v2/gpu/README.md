# G2 — nouveau diagnostic privé, sources seulement

EXPERIMENTAL / SOURCE-ONLY / revue indépendante requise. Aucun résultat G1
perdu n’est récupéré ni requalifié. Les nouvelles sources dérivent de
SceneFX 37ccd723bef49e6891156ffafce8f549f01446cc + CORE accepté. Les copies
`scene-core` et `mosaic-core`, les shaders, les calculs blur/sampler/clear/cache,
les kits graphics et les binaires CORE restent inchangés.

## Contenu et contrat

- `g2-native.patch` : nouveau delta contre `sources/scene-core`, trois fichiers
  privés, aucun changement Meson, shader ou ABI publique.
- `g2_gl.h` : corps exact de lecture testé par FakeGL. Contexte EGL courant,
  API et version réels ; ES3 confirmé par EGL ET GL avant tout enum ES3.
  GLES2 et attachments texture sans dimensions sûres sont explicitement refusés.
  RBO : objet attaché, dimensions/format/canaux/alpha/samples, completeness,
  read buffer, viewport/scissor, bindings et pack/PBO sont observés.
- `g2_native.h` et `fx_pass.c` : source, down0/1/2, up2/1/0, cache optimisé,
  copie sans blur, composition avant submit. Identités époque, nonce,
  séquence locale de pass et clé offscreen de l’output. H1 est sélectionné
  par le vrai `output->name == HEADLESS-1`, scale1 et transform normal lors de
  `fx_render_pass_init_offscreen_buffers` ; jamais par les dimensions seules.
  Les slots de passes sont retirés au submit ; réutilisation d’adresse remplacée,
  plus de huit passes simultanées = refus explicite.
- `clients-g2.c` : adaptation nouvelle du client edge versionné. Background
  uniquement sur commandes exactes `G2-A`, `G2-B`, `G2-A-return`, trois commits
  maximum. Le premier payload A est retenu et recopié verbatim à A-return.
  Configuration ACK sans dessin background. Motifs fixes RGB connus avant
  acquisition ; l’alpha XRGB du payload n’est pas un sentinel de lecture.
  SHM privé sous LAB/scratch, buffers immuables jusqu’au release, comptes
  release/closure explicites ; RLIMIT_CORE=0 et PR_SET_DUMPABLE=0.
- `protocol.py` : framing/verificateur offline et armement exclusif, aucune
  création de processus. `scenario.py` : scénario exécutable `run(session,
  binding)` pour une Session du moteur commun liée séparément au nouveau G2.
  Aucun lancement automatique à l’import. Le moteur commun n’est pas modifié.
- `validate_source.py` : adaptation bornée des contrôles gpu-field versionnés :
  image plane0 FOURCC connu/stride approprié ; auxiliaire AMD/DCC distinct,
  aucun image-stride appliqué au plan1, aucune taille DCC ou propriété FD
  inventée. Header DRM SHA vérifié. Les exemples anciens restent
  HISTORICAL_REPORTED_ONLY ; les fixtures contrôlées ne sont pas des allocations.

## Intrusion GL et limites

`glGetError` consomme une queue non restaurable. Chaque groupe de requêtes
et la lecture est suivi d’un drainage limité à16 codes ; erreurs préexistantes,
queue saturée, erreurs de requête/lecture/restauration refusent READ_SUCCESS.
Le hook restaure puis vérifie chaque binding/paramètre pack qu’il change,
ainsi que le contexte et l’état fonctionnel observé. Aucun glFinish, changement
shader/sampler/clear ou correction numérique. `glReadPixels` retourne void :
les CRC des fichiers et l’alpha ne constituent jamais une preuve de succès.
La lecture peut synchroniser et modifier le timing : diagnostic INTRUSIF.

Programme réellement lié et courant, location/type halfpixel, bits float bruts,
uniformes radius/proj/tex_proj, sampler et capacité mediump sont interrogés.
Les qualifiers et SHA des shaders portent explicitement la base
FROZEN_LINK_INPUT_SOURCE. La capacité n’est pas une mesure de chaque opération.
L’idéal CPU float32 est calculé séparément offline sans égalité, epsilon ajusté
ou fit sur mediump. Dimensions texture GL-level : NOT_PROVEN sur ce port ;
dimensions natives wlr sont conservées séparément. Attachments textures : refus.

Buffer physique présenté, lien au commit/present natif, lifetime et completion
GPU, génération atomique et causalité de tout le champ restent NOT_PROVEN.
Aucun de ces statuts n’est promu par compilation ou contrôles synthétiques.

## Protocole prospectif exact et bornes

Répertoire réel fixe :
`/var/tmp/swayfx-mosaic-corec-v2-i516p6po/gpu-work/acquisition`, UID courant,
mode0700, aucun lien symbolique. Variables : MOSAIC_G2_DIR (ce chemin exact),
MOSAIC_G2_NONCE (64 chiffres hexadécimaux minuscules).

`epoch-N.arm` doit être un fichier régulier mode0600, UID courant, lien unique,
contenant exactement `<nonce> <N>\n`. Le hook le consomme avant toute observation
par lien exclusif `.consumed`, vérifie l’inode, supprime `.arm` puis fsync.
Aucune réutilisation si `.consumed` existe, même après crash. Les fichiers raw
et JSONL sont exclusifs et fsync. Un rejet de premier A conserve les fichiers
existants et arrête B/A-return ; aucune boucle retry. Les dix readbacks sont
plein cadre physique800×600 RGBA8, soit19,200,000 octets par époque et57,600,000
au total planifié, avec multiplication contrôlée et plafond total256MiB.
Les régions Pixman fraîches sont conservées comme unions de rectangles natifs,
256 rectangles maximum ; hors-domaine frais conservé dans les raw plein cadre.

L’armement peut précéder le commit client ; un passage ancien est refusé par
un contrôle RGB natif exact du motif prospectif complet de l’époque, sans retry.
Le scénario règle le setup puis vérifie deux captures H2 stables avant A,
ensuite trois paires H1/H2, huit captures au total (cap G2 existant16).
Chaque époque est validée avant la commande suivante. Une anomalie H2 refuse
l’époque. Whole H1 A/A-return et H2 ne masquent aucun pixel et utilisent une
tolérance RGB nulle. L’égalité raw source A/A-return est rapportée séparément.

## Interface du parent, avant construction/acquisition G2

La revue R-GPU doit porter sur le gel exact et les logs offline. Le kit ne
crée pas de receipt d’acceptation et n’ouvre pas le ledger G2. La paire3,
le binaire distinct et les sources exactes doivent être liés par le parent
après revue, observabilité suffisante et décision explicite.

Le parent crée ensuite le répertoire fixe et un gate externe mode0600 avec
`source_review=ACCEPTED`, `gl_observability=PASS`, `runtime_authorized=true`,
`pair=3`, `binary_sha256=<nouveau SHA exact>`. `protocol.arm` le contrôle,
mais ne le produit jamais. Cette interface n’auto-autorise aucune acquisition.

`scenario.run(session, binding)` exige une Session G2 avec les outputs
horizontaux H1[-800,0,800,600] et H2[0,0,800,600], limites de capture/action
liées au nouveau diagnostic, identité binaire/librairies vérifiée par le moteur
commun, cleanup/watchdog du parent. `binding` contient : G2_ledger_reserved=True,
gate_file, binary, client, client_sha256, nonce, source_manifest_sha256.
L’autorisation/ledger du parent doit être scellée avant `session.start` ; elle
reste fermée avec les sources seules. Le scénario débite la mutation avant
jeton/commande, et le moteur débite spawns/captures/configuration. Les commandes
IPC utilisent exclusivement le socket explicite privé de Session.

## Reproduction portable offline

`reproduce.py` et `test-targeted.py` sont des CLI source-only portables. Ils
n’infèrent aucun LAB, build, arbre CORE ni répertoire de sortie. Fournir à chaque
appel les chemins explicites :

```sh
KIT=/chemin/vers/gpu-publication-kit
CORE=/chemin/vers/scene-core-reconstruit
CC=/chemin/vers/build-core/compile_commands.json
DEST=/chemin/vers/nouvelle-destination-scene-gpu
WORK=/chemin/vers/repertoire-de-travail-existant
python "$KIT/reproduce.py" --core "$CORE" --destination "$DEST" --work "$WORK"
python "$KIT/test-targeted.py" --core "$CORE" --compile-commands "$CC" --work "$WORK"
```

`CORE` doit être l’arbre SceneFX CORE reconstruit attendu, incluant le commit
SceneFX décrit ci-dessus et le CORE accepté. `DEST` doit être absent et
indépendant de CORE. `WORK` doit exister et rester un espace jetable pour les
logs, exécutables de test et reçus. `reproduce.py` copie CORE vers DEST, applique
`g2-native.patch` puis compare l’ensemble des fichiers modifiés au manifeste
d’empreintes embarqué dans le script. La vérification n’utilise aucun ancien
LAB, reçu ou arbre cible. `test-targeted.py` exige le `compile_commands.json`
associé au CORE fourni pour obtenir les includes nécessaires aux vérifications
de syntaxe; il ne reconstruit aucun compositor.

Les chemins `G2_ROOT` et les chemins d’acquisition déclarés dans le diagnostic
natif restent l’identité exacte de l’ancien LAB, par choix explicite du
diagnostic accepté. Cette recette portable ne rend donc pas ce binaire/configuration
transférable à un autre emplacement. Pour tout autre `G2_ROOT`, il faut une
nouvelle identité de diagnostic, un nouvel examen des sources et des reçus; ne
réutilisez pas silencieusement les sources natives ou leur autorisation.

Les tests utilisent C17, `-Werror`, limite core 0 et processus non dumpable. Le
test native lie uniquement les helpers utilisés avec dead-section removal;
FakeGL exécute le même corps `g2_read` que le hook natif. Ces vérifications ne
sont ni un build natif ni une exécution Wayland/GL/GPU. Statut de la revue
indépendante : PENDING. Runtime G2, vrai readback GL et vraie allocation DRM :
NOT RUN. Aucun sanitizer campaign, build pair, compositor, client Wayland ou
acquisition GPU n’est lancé par cette recette.
