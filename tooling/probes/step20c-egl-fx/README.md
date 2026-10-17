# STEP20C — fixture source-only EGL/FX

**EXPERIMENTAL — admission cgroup implémentée pour validation hors ligne ;
qualification du nouveau runner NOT_RUN.** L'ancien essai reste consommé,
BLOCKED_BEFORE_HELPER, EGL_NOT_RUN / ALLOCATOR_NOT_ATTEMPTED. Aucun ancien LAB
ne doit être modifié ou relancé. Cette fixture ne change ni C, ni compositeur,
ni ABI, ni packaging. STEP20C reste NEXT et le clipping multi-output de
production NOT_YET_SUPPORTED.

Le [contrat d'admission](../../../docs/design/STEP20C_EGL_FX_TASK_LIMIT_PROTOCOL.md)
et [l'incident EGL](../../../docs/design/STEP20C_HEADLESS_EGL_FX_PROBE.md)
distinguent les preuves historiques de cette implémentation. Les tests mockés
ne prouvent aucun lancement sur le manager réel et ne valident pas le budget
Mesa. L'exécution bénigne et une éventuelle exécution EGL demandent chacune une
nouvelle autorisation conversationnelle avec leur propre LAB et manifeste.

Le premier essai bénin nominal du 17 octobre 2026 a refusé avant ATTEMPT,
création de scope ou payload : `UID process divergent` dans le diagnostic
`ProcFS.uid_threads()`. Les deux LABs bénins historiques restent non consommés
et ne doivent pas être réutilisés. Le diagnostic historique corrigé inclut les threads de
tous les processus dont l'UID réel correspond, même avec des UID effectif,
sauvé ou filesystem différents. Il reste disponible hors chemin d'admission.
L'admission lit désormais la borne système `runnable/total` de `/proc/loadavg`
après qualification conservative du procfs hôte Linux et de ses namespaces
initiaux ; les contextes ambigus refusent. Le minimum soft/hard NPROC fini doit
être strictement supérieur au total plus256, avant ATTEMPT et avant release.
Les valeurs peuvent fluctuer sans égalité entre snapshots si chaque marge reste
suffisante. Aucun comptage ne réserve atomiquement de capacité. `ProcFS.identity()` conserve ses contrôles
stricts pour le superviseur, le manager et le bootstrap. Les régressions restent
hors ligne ; cette correction n'établit aucun PASS cgroup natif.

`probe.c` crée seulement un event loop, un backend headless non démarré et EGL
via le constructeur interne pinned `wlr_egl_create_with_drm_fd(-1)`. Il interroge
**le device associé à ce display**, exige `EGL_MESA_device_software` et refuse
les extensions DRM avant `fx_renderer_create_egl`. Le constructeur FX initialise
ses ressources internes ; la sonde n'appelle ni allocateur, ni création de
buffer/framebuffer, ni commande de dessin. Les formats de texture DMABUF,
DATA_PTR et SHM sont distincts des formats cibles. Les sets et FDs sont
empruntés ; EGL est détruit par le renderer seulement après transfert réussi.

Les chaînes sont limitées à 16384 octets, chaque set à 256 formats, chaque
format à 64 modifiers et leur total à 4096. Les identités absentes ou un
dépassement refusent la mesure ; aucune troncature n'est qualifiée de succès.
Sorties JSONL, étape EGL flushée avant FX, statut 0 pour une mesure terminée,
20 pour un refus ou une mesure incomplète. `target_allocation=NOT_ATTEMPTED`
reste vrai ; l'éligibilité conditionnelle des allocateurs pinned est une
interprétation de capacités, pas une allocation mesurée.

Préparation passive, sans exécuter le helper, dans un **nouveau** LAB privé :

```sh
python3 tooling/probes/step20c-egl-fx/prepare.py \
  --lab /var/tmp/NOUVEAU_LAB_PRIVE \
  --source-store /var/tmp/swayfx-mosaic-corec-v2-i516p6po/sources
```

Le script lit les objets git pinned SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc` et wlroots
`d783533489e1f75d6886c2ab5c5960090ef268f8`, extrait leurs archives dans le
nouveau LAB et vérifie chaque blob. Il copie les seuls headers générés de
l'installation et compare les headers publics compilés aux sources pinned.
Le contrôle syntaxique utilise C17 avant le link, SceneFX avant wlroots.
Le manifeste contient les commandes exactes, les dépendances `cc -M`, les
SHA256 des sources/headers/scripts/helper/outils, les identités ELF et la
fermeture `readelf` DT_NEEDED. Aucun `ldd`, loader ou helper n'est exécuté.
Les bibliothèques installées sont scellées par leurs bytes et Build IDs ; elles
ne sont **pas reproduites depuis les sources**, et la correspondance des
headers/exportations ne prouve pas leur provenance source. Les licences restent
dans les archives privées ; aucun binaire, log ou manifeste privé n'entre dans Git.

Les 23 tests historiques lancent seulement des enfants Python inertes pour
les pipes. `test_cgroup_admission.py` exerce les adaptateurs et l'orchestrateur
réels avec faux manager/proc/cgroup/processus, sockets locaux et threads inertes.
Une sentinelle interdit toute création native dans cette nouvelle suite.
Aucun test n'invoque systemd-run, bwrap ou le helper :

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tooling/probes/step20c-egl-fx -p 'test_*.py' -v
```

Le harnais C substitue **tous** les appels EGL/Wayland/wlroots et inclut le
corps réel de `probe.c`. Ses huit scénarios discriminent le device sélectionné,
les extensions DRM, le transfert EGL, l'ordre de destruction et les formats.
Il lie uniquement libc, sans bibliothèque EGL/FX ; son exécution reste un test
inerte, distinct de l'exécution interdite du helper réel. Après préparation :

```sh
LAB=/var/tmp/NOUVEAU_LAB_PRIVE
cc -std=c17 -Wall -Wextra -Werror -DWLR_USE_UNSTABLE \
  -I"$LAB/generated" -I"$LAB/sources/scenefx/include" \
  -I"$LAB/sources/wlroots/include" \
  $(pkg-config --cflags scenefx-0.5 wlroots-0.20 wayland-server egl glesv2 pixman-1 libdrm) \
  tooling/probes/step20c-egl-fx/test_probe_mocks.c -o "$LAB/bin/inert-c-tests"
readelf -dW "$LAB/bin/inert-c-tests"
"$LAB/bin/inert-c-tests"
```

Le préparateur imprime le digest du manifeste et la commande exacte du **plan
passif**. Recopier ce digest depuis la préparation revue, sans le recalculer
au moment d'exécuter. Le plan ne crée aucun fichier et n'exécute aucun ELF. Un LAB dont `ATTEMPT`
existe refuse aussi le plan, car son budget est déjà consommé.
Après une **nouvelle autorisation conversationnelle**, la même commande avec
`--approve-native-probe` consomme durablement `ATTEMPT` avant spawn ; toute
erreur, tout timeout et même un échec de spawn interdisent un retry :

```sh
/usr/bin/env -i PATH=/usr/bin LC_ALL=C /usr/bin/python3 -I \
  /var/tmp/NOUVEAU_LAB_PRIVE/fixture/run.py \
  --lab /var/tmp/NOUVEAU_LAB_PRIVE --manifest-sha256 DIGEST_REVU \
  --approve-native-probe
```

Le lanceur refuse tout argument de mount/env libre et tout drift des identités.
Le protocole bwrap exact est construit dans `run.command` et scellé. `/usr` est
RO ; seul le helper neuf est lié RO à `/probe`. `/proc`, `/dev`, `/dev/shm`,
`/tmp` et `/run` sont privés ; pas de HOME, `/etc`, `/sys`, réseau hôte,
socket/bus/session, `/dev/dri`, `/dev/input`, `/dev/udmabuf` ou FD hérité.
`PWD=/tmp` est explicite. L'ICD est restreint à Mesa par son JSON sous `/usr` ;
ce choix ne prouve pas l'identité logicielle, vérifiée séparément par EGL.
Mesa EGL, swrast, GBM dri et gallium plus leurs DT_NEEDED sont scellés ; des
chargements conditionnels runtime restent non observés jusqu'à l'unique essai.

La préparation bénigne inspecte passivement les outils Python/systemd/env/readelf
avec readelf : Build ID, ELF64 x86-64, interpréteur fermé et fermeture DT_NEEDED
sont enregistrés ; tous les octets de cette fermeture sont scellés. Elle ne
compile ni ne charge EGL et ne demande pas de source-store.

Le manifeste schema2 scelle `scope_argv` (seuls PID/startticks du superviseur
restent des emplacements remplis par préflight), `kind` (`benign` ou `egl`), `qualification_mode`,
la commande fermée, les environnements et `scope` : nonce aléatoire 128 bits,
nom et Description associés, Delegate=yes, TasksMax=256, RuntimeMaxSec=12s,
TimeoutStopSec=2s et KillMode=control-group. Le timeout manager indépendant
borne les descendants en cas de disparition du superviseur ; cette propriété
reste à qualifier sur le vrai manager. La limite cible `pids.max=256` compte
tous les threads du sous-arbre, sans garantie de suffisance Mesa.

`run.py` sans drapeau d'approbation vérifie seulement les identités et imprime
le plan : aucun processus, fichier ATTEMPT, socket ni appel manager. Le helper
Python est chargé par chemin absolu, après vérification de son hash, même avec
`python3 -I`. Avec approbation, le préflight refuse un vrai launcher en session
scope, un manager non délégué, app.slice inactif, un montage non cgroup2/domain,
un ancêtre non writable, pids absent, un headroom insuffisant, une source
loadavg non fiable ou NPROC hérité <= total système +256. Aucun snapshot /proc ne
constitue une réservation. Aucun processus n'est migré par le superviseur.

Après ATTEMPT durable O_EXCL, systemd-run crée un seul scope et lance le
bootstrap fixe. Celui-ci ouvre un socket AF_UNIX SOCK_SEQPACKET privé mode0600
dans le LAB0700, sans hypothèse de transmission stdin/FD par systemd-run.
Les deux côtés vérifient SO_PEERCRED ; le bootstrap vérifie le startticks et
le pidfd du superviseur. Avant RELEASE unique, le superviseur contrôle la
Description nonce, Id/InvocationID/ControlGroup, propriétés manager, inode et
propriétaire cgroup, pids.max effectif256, pids.current1, unique PID, absence
de sous-cgroup, UID/startticks/pidfd et membership. EOF, nonce faux, timeout,
PID mort ou divergence interdisent l'exec. Aucun prlimit/bwrap/EGL ne précède
RELEASE. Les FD supérieurs à2 sont fermés à la frontière exec ; le bus manager
ne rejoint pas la charge et l'environnement devient exactement HOST_ENV.

Le payload conserve AS1GiB, CPU5s, NOFILE64, FSIZE1MiB et CORE0. Seul
l'override NPROC256 historique est supprimé ; les limites soft/hard NPROC sont
héritées, jamais augmentées. AS/CPU/NOFILE sont des limites par processus,
FSIZE est par fichier ; aucun quota agrégé mémoire/CPU/disque n'est promis.
Le délai du runner est 10s depuis préflight (collecte jusqu'à8s, cleanup
jusqu'à10s), avec 1MiB par pipe. Le filet manager12s+stop2s est séparé.

Un observateur inerte commence avant RELEASE et échantillonne l'inode et
`cgroup.events populated=0`, `cgroup.procs`, `cgroup.threads`, `pids.current`
récursivement. Il reste actif pendant collecte/stop. Le cleanup vérifie la
même invocation/inode avant tout stop. Un scope déjà disparu n'est accepté
qu'avec une preuve vide antérieure et la disparition unité+cgroup. Une course
qui cache l'état vide reste CLEANUP_UNPROVEN, sans convertir ENOENT/ENODEV en
preuve. Ce protocole est strict : la qualification réelle doit mesurer si
l'échantillonnage observe effectivement la transition. Aucun stop par nom seul,
aucun PID découvert n'est tué, aucun repli vers pkill/cgroup.kill.

Les phases privées JSON sont PRECHECK, SCOPE_CREATED (requête de création),
ADMITTED (ownership), RELEASED (intention exec), COLLECTED et CLEANED.
PAYLOAD_STARTED requiert le marqueur stdout fixe du seul enfant bénin ; une
intention exec n'est pas une preuve d'exécution EGL. Les sorties EGL restent
brutes et `EGL_RESULT_UNINTERPRETED`. Les préfixes de sortie sont conservés
sur overflow/timeout. Toute collecte/cleanup/journalisation non prouvée refuse
le succès. Le risque d'interférence hostile du même UID n'est pas éliminé.

Préparer deux LABs **neufs distincts**, sans compilation ni exécution native :

```sh
python3 tooling/probes/step20c-egl-fx/prepare.py \
  --lab /var/tmp/NOUVEAU_LAB_BENIN_NOMINAL --benign --qualification-mode nominal
python3 tooling/probes/step20c-egl-fx/prepare.py \
  --lab /var/tmp/NOUVEAU_LAB_BENIN_PARENT --benign --qualification-mode parent-death
```

Le cas nominal affiche un marqueur et dort0.2s. Le cas parent-death affiche
le même marqueur et dort30s ; après RELEASE et reçu durable PARENT_DEATH_TEST,
le superviseur termine volontairement avec code71. Le manager doit alors
arrêter le scope à12s, avec stop2s. Le résultat de ce cas doit être établi par
un observateur extérieur ; le superviseur disparu ne peut écrire son succès.
L'observateur doit vérifier la même Description/InvocationID/inode, la fin des
tâches, l'état vide et la disparition, sans jamais stopper une unité étrangère.
Les commandes exactes avec paths/digests/noms éphémères et l'observation bornée
appartiennent aux documents d'autorisation privés du nouveau LAB.

Après accord distinct seulement, depuis le launcher app.slice prévu, utiliser
la commande passive imprimée avec `--approve-benign-gate`. Ce drapeau est
incompatible avec un manifeste EGL ; `--approve-native-probe` est incompatible
avec un manifeste bénin. Aucun scope réel, charge bénigne, bwrap ou EGL n'a été
exécuté par l'implémentation et les tests hors ligne.
