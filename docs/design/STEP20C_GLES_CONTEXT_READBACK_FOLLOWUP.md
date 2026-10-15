# STEP20C — suivi contexte GLES et readback G3

2026-10-15. Rapport expérimental du ticket
`SWAYFX_MOSAIC_STEP20C_COREC_V2_FULLSCREEN_OOM_GLES_NATIVE_CLOSURE_BATCH_V1`.
Le run GPU-G3 est **INCONCLUSIVE** ; son objectif diagnostic natif est
**NOT_EXERCISED**. La cause identifiée est un chemin de fixture non portable,
avant toute acquisition ; aucun défaut GPU/compositeur n'en est déduit.

```text
GPU_GLES_CAPABILITY_AND_READBACK_PREFLIGHT=ACCEPTED
GPU_GLES_ADMISSION=NOT_EXERCISED
GPU_G3_NATIVE_READBACK=NOT_EXERCISED
GPU_WHOLE_FIELD_CAUSALITY=NOT_PROVEN
```

La portée du preflight accepté est **OFFLINE_ONLY** ; elle ne qualifie pas
l'admission ou le readback natifs non exercés.

## Octets exécutés et préparation revue

Le [kit de suivi](../../tooling/probes/step20c-corec-v2-followup/README.md)
exécuté est celui du commit source publié
`c55373eab3c53132bf1157acc9cfc9edd451156e`, gel global V2 SHA256
`2e9fe75a48466fa1a9e3081137146d5cfffb35145c1749160e2c4f350bc6e5b7`,
digest `f21ea193aedfada620c251f0cf6a22375fb993483905129208864e22e535b140`.
La [publication](evidence/step20c-native-closure/source-publication.json)
et le [clone](evidence/step20c-native-closure/clone-validation.json)
précèdent les réservations : 49/49 fichiers et modes, 66 tests, six clients
compilés. Trois findings initiaux ont été corrigés avant acceptation source.
Ces faits ne qualifient pas le premier dessin client sous le nouveau LAB.

Le nouveau diagnostic G3 a sa propre identité : SHA256
`9da90b178f20ea79bc9fb2a105c227f9d5d66a9de7eac77ff4ec3ea102908658`,
Build ID `afdde13d52f3a5fe07c096c1221fcf0c8ae223fc`, PID `3510983`.
Le client réellement lancé, PID `3511049`, porte le SHA256
`4e791780ac62152245891459864283750681b136a246c3c39ccf36b4f33972b4` ;
sa source `clients-g2.c` porte le SHA256
`66658e99704c32d90b073f7664dd4aa9ff1cbf3530c81f7f7ac40e2fa49d9ca7`.
Le gel GPU séparé est
`03b3cdb4b665aeca860cf3e1363d4fbe5c2cbcb0372f3b4fe582e88488ccb5d2`.
Une correction offline ultérieure n'est pas la source de ce run.

La première préparation Meson échoue : les arguments C sont fusionnés et
`EGL_EGLEXT_VERSION` n'est pas obtenu. Le reçu FAIL reste archivé ; la
continuation explicitement autorisée corrige les arguments de la **même paire**,
sans changement source. Le [build réparé](evidence/step20c-native-closure/g3-build-repair.json)
et la [revue indépendante de build](evidence/step20c-native-closure/gpu-build-review.json)
portent sur cette identité, une paire et un DESTDIR de cinq fichiers.
Les 417 fichiers Mosaic restent ceux du CORE source compilé inchangé ; le
diagnostic SceneFX est distinct. Le stage privé comprend uniquement
`/usr/bin/swayfx-mosaic` et les quatre notices documentées sous
`/usr/share/licenses/swayfx-mosaic/`. Aucune installation ; licences
**LEGAL_NOT_APPROVED**. Le [contrôle final de build](evidence/step20c-native-closure/g3-build-validation.json)
est distinct d'une exécution du hook.

## Contrat B4 accepté et limite de sa couverture

La [revue sémantique B4](evidence/step20c-native-closure/gpu-b4-semantic.json)
accepte le vrai corps `g2_read` dans un périmètre offline : 29 cas FakeGL,
quatre mutants rejetés, 12 commandes de corpus source, plus 66 tests
d'admission/adapters. La revue n'a pas rejoué ces commandes une seconde fois :
elle a vérifié leur liaison aux sources effectivement compilées.

Le diagnostic préserve la divergence EGL/GL au lieu de l'effacer par une
supposition sur la version demandée à la création. Les queries de version et
capacités, leur fenêtre d'erreur propre et les queries supportées doivent
être qualifiées sur le contexte réel. L'ancien G2 observait
`EGL_CONTEXT_CLIENT_VERSION=2` face à `GL_VERSION=OpenGL ES 3.2` ; cette
divergence reste non résolue par G3. La préparation B4 acceptée ne constitue
pas une preuve universelle de conformité EGL.

Le plan garde les bits d'uniformes et la précision `mediump`, le DCC
modifier-aware et les modèles/résidus avant toute comparaison A/B/A. Un plan
auxiliaire DCC ne reçoit pas un stride d'image inventé `width*4`.
Les drains consomment la queue d'erreurs GL, qui n'est pas restaurable ; la
restauration des bindings ne restaure pas cette queue. Le readback synchrone
serait intrusif temporellement. Aucune tolérance, shader ou règle de fit n'est
changée sur la base du résultat non exercé.

La revue de préparation client était trop large : compilation, parsers,
armement et FakeGL n'exerçaient pas `draw()` avec le nouveau `TMPDIR`.
Cette lacune est reconnue dans la
[revue du résultat](evidence/step20c-native-closure/gpu-results-review.json),
sans invalider les observations offline effectivement couvertes ni convertir
une correction future en succès runtime rétroactif.

## Arrêt avant SHM et avant armement

Le client reçoit un configure XDG et envoie son ACK, puis sort à **2** avant
`create_pool`, `create_buffer`, `attach` et toute confirmation SHM. Dans les
octets c553 exécutés, `gpu/clients-g2.c:92`, fonction `draw`, compare
`TMPDIR` littéralement au scratch de l'ancien LAB
`/var/tmp/swayfx-mosaic-corec-v2-i516p6po/scratch`. La session fournit le scratch
du LAB neuf `/var/tmp/swayfx-mosaic-step20c-native-closure-qseaqp39/scratch`.
Cette branche source déterministe, l'environnement construit, le wire et
le code 2 attribuent l'arrêt à la fixture. Aucun errno ou message explicite
client n'a été journalisé ; aucun diagnostic de ce type n'est inventé.
Le runner attend une vue IPC qui ne se mappe jamais et atteint son attente
bornée. La réservation GPU-G3 reste consommée, sans retry ni remplacement
par GPU-CTRL.

| Niveau observé | Fait exact |
| --- | --- |
| Startup EGL | EGL 1.5 ; log de création de contexte OpenGL ES 2.0 |
| Startup GL | OpenGL ES 3.2 Mesa 26.2.4-arch1.1, vendor AMD |
| Renderer | AMD Radeon 780M, radeonsi/phoenix/ACO |
| Hook G3 | Zéro armement, zéro epoch, zéro raw ; acquisition vide |
| Budget output | 0/12 captures ; zéro hook et zéro mutation |
| `eglQueryContext` / major-minor du hook | NON OBSERVÉS |
| `READ_SUCCESS`, uniformes, DCC, erreurs/restauration du hook | NON OBSERVÉS |
| A/B/A, H1/H2, modèles/résidus nouveaux | NOT_EXERCISED |

Les logs startup ne sont pas une nouvelle mesure
`EGL_CONTEXT_CLIENT_VERSION=2` du hook. Zéro armement diagnostic ne signifie
pas absence d'appels GL ordinaires du renderer. Les valeurs de readback ou
de restauration absentes ne sont pas des zéros mesurés.

## Codes, conservation et revue

Le ledger mesure 7,623459039 s, outcome 7,614715491014067 s, enveloppe commande
8,184041837 s. Runner 1 ; compositeur PID 3510983 et pointeur PID 3511036
sortis à 0 ; référence PID 3511049 sortie à 2. IPC terminal 1 avec fin de
réponse/EOF, distinct du compositeur 0. Le cleanup scientifique est **false /
INCONCLUSIVE** : le client n'a ni `CLOSE_RECEIVED` ni `SHM_CLOSURE`.
Nettoyage mécanique PASS, processus récoltés, runtime privé supprimé, aucun
rescue ni watchdog. Le succès mécanique ne qualifie pas la fermeture client.

Les bruts restent sous le LAB neuf : `graphics-runs/GPU-G3/run/`, dont
`outcome.json`, `partial-failure.json`, `events.jsonl`, `g2-reference.log`,
`compositor.log`, identité et maps ; `execution/GPU-G3-command.json` conserve
l'enveloppe. La revue indépendante `reviews/gpu-results/receipt.json` porte
le SHA256 `78ce6fe03955d62d1b079b9a8e81161dcb5bfceef71bd2b71d13892bcf7e4d78`
et accepte l'interprétation **INCONCLUSIVE / objectif NOT_EXERCISED**.
Elle identifie le finding P2 `GPU-RUNTIME-FIXTURE-TMPDIR` et la limite de
l'admission antérieure. Le [résumé runtime](evidence/step20c-native-closure/runtime-summary.json)
et le [ledger](evidence/step20c-native-closure/ledger.json) préservent les codes.

## Suite limitée

La correction de portabilité et le diagnostic explicite FS-P sont un delta
**OFFLINE_ONLY** séparé, sans reconstruction de compositeur ni qualification
native. Le [reçu de réparation](evidence/step20c-native-closure/postcampaign-repair.json)
et la [validation indépendante](evidence/step20c-native-closure/postcampaign-offline-validation.json)
conservent 73 tests réussis : 66 existants, trois d'identité et quatre du vrai
helper C validation/template, sans dessin Wayland. Le reçu indépendant porte
le SHA256 `5905e2002041148d7a104e195132f56c8b4152952547be4ed0985da4eacc3852`.

Le [manifeste post-campagne final](evidence/step20c-native-closure/postcampaign-source-manifest-final.json)
de 50 fichiers mode0644 porte le SHA256
`1db849c1152bb29d512bf62e3db53cba18d0179c0008ca116887eb572d76a080`,
digest `14e24501658f1c4c29e7d8c06db71ed07a77b8e80e283453420bbc5b3e2f03c8` ;
le [gel GPU final](evidence/step20c-native-closure/postcampaign-gpu-manifest-final.json)
porte le SHA256 `a89926241a871bdc492348f922df1232962e622c4703720984ef681b5e6d98cb`.
Les gels intermédiaires f13da722…/230f131a… restent archivés ; seul
`gpu/README.md` change ensuite pour donner la commande explicite SMX_LAB et
les quatre tests TMPDIR. La
[revue initiale du delta](evidence/step20c-native-closure/postcampaign-delta-initial-review.json)
conserve CORRECTION_REQUIRED. La
[revue documentaire finale du delta](evidence/step20c-native-closure/postcampaign-delta-review.json),
SHA256 `4d459c0963c6535a404bfaa68d11dff0cf738e2d21167c148c12315e954ffe86`,
accepte cette correction : code/tests identiques à ceux des 73 tests
indépendants, non réexécutés dans cette revue documentaire.

Le client corrigé compilé SHA256
`bfc7d47596d5f69b68cd7000e257c7819949081ee7c6d66635eb9accf9ad7f36`
n'a **jamais été exécuté** en campagne native. Ces gels finaux ne remplacent
ni le gel V2 ni le client c553 réellement exécutés ; ils ne requalifient
aucun run consommé. La [revue finale approfondie](evidence/step20c-native-closure/final-review.json)
du dossier est **PASS**, SHA256
`3b15b5093730d6c43897e0adad4a1b2987fbc1097694a03645e928023ba23814`,
zéro constat bloquant. Son unique remarque documentaire non bloquante
NB-ENUM-1 est corrigée ici : valeur `ACCEPTED`, portée OFFLINE_ONLY séparée ;
le reçu historique de revue reste inchangé. L'audit rejoue 69+4 tests réussis,
rejette six contre-exemples bruts et vérifie 86 hashes d'artefacts et les
316 hashes protégés. Les contrôles finaux après audit sont consignés dans le
[reçu de validation](evidence/step20c-native-closure/final-validation.json).
La publication effective est attestée séparément par
`LAB/final-publication.json` et le rapport final après vérification distante.

La [décision V4](STEP20C_COREC_V2_INTEGRATION_DECISION_V4.md) garde
**PRIVATE_COREC_V2_NEEDS_TARGETED_EVIDENCE**, GPU whole-field, buffer identity,
atomic generation, complete damage et GPU completion **NOT_PROVEN**.
G2 historique reste inchangé. Toute campagne future exige une instruction et
un budget distincts. STEP20C NEXT ; production multi-output
**NOT_YET_SUPPORTED**, `PRODUCTION_AUTHORIZED=FALSE`.
