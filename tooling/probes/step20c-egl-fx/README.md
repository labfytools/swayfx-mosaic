# STEP20C — fixture source-only EGL/FX

**Mise à jour du 17/10/2026 : essai unique consommé, BLOCKED_BEFORE_HELPER.**
Bubblewrap a échoué à créer le namespace ; EGL_NOT_RUN /
ALLOCATOR_NOT_ATTEMPTED. Les instructions ci-dessous décrivent la préparation
historique et ne constituent plus une procédure de relance admissible.
Ne relancer aucun ancien LAB. Le [nouveau protocole de limite de tâches](../../../docs/design/STEP20C_EGL_FX_TASK_LIMIT_PROTOCOL.md)
est DESIGN_ONLY / EGL_FX_RETRY_PREP_BLOCKED : admission cgroup à implémenter,
tester hors ligne et qualifier séparément avant toute nouvelle autorisation EGL.
Le code historique reste inchangé ; ses tests ne valident pas ce nouveau protocole.

**EXPERIMENTAL / runtime NOT_RUN.** Cette fixture prépare une unique mesure
future. Elle n'ajoute aucune dépendance de production, ne démarre aucun
compositeur et ne démontre ni allocation ni rendu. Le document de référence est
[la proposition de sonde](../../../docs/design/STEP20C_HEADLESS_EGL_FX_PROBE.md).
Les anciens LAB restent en lecture seule.

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

Les tests Python ne lancent que des processus Python inertes pour exercer les
pipes, le timeout et la collecte. Aucun test n'invoque bwrap ou le helper :

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tooling/probes/step20c-egl-fx -p test_probe.py -v
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

Le budget est exactement un lancement, 8 s de payload et 2 s de réserve de
nettoyage dans un délai nominal supervisé de 10 s au total, 1 MiB par canal brut, AS 1 GiB, CPU 5 s,
NOFILE 64, FSIZE 1 MiB, CORE 0, NPROC 256. AS/CPU sont par processus et NPROC
s'applique à l'UID global ; ce n'est pas une limite agrégée cgroup. Le
superviseur crée sa session, ferme les FDs, lit les deux pipes concurremment,
utilise pidfd si disponible, tue seulement son groupe non récolté et récolte
son enfant. La fin du namespace PID bwrap termine ses descendants. Une
collecte non prouvée est un échec explicite ; aucun PID déjà récolté n'est tué.
Ce contrat ne prétend pas durcir le système contre un pair hostile du même UID,
ni retirer les capacités de diagnostic `/proc` déjà imposées au protocole.
Les canaux bruts et reçus bornés restent privés, avec écritures atomiques et
fsync ; aucun scope systemd n'est créé.
