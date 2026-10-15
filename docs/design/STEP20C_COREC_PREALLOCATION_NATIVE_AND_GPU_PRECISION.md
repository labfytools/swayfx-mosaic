# SWAYFX_MOSAIC_STEP20C_OOM_PREALLOC_NATIVE_CORE_AND_GPU_PRECISION_BATCH_V1

> EXPERIMENTAL — édition du 2026-10-15, avant revue finale et publication. Résultat global **BLOCKED**, recommandation **UNDECIDED**. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; PRODUCTION_MULTI_OUTPUT=NOT_YET_SUPPORTED ; PRODUCTION_AUTHORIZED=FALSE.

## Résultat et autorité des preuves

Le gate obligatoire de provenance bloque le candidat CORE-C avant toute modification native. Les laboratoires historiques requis ont été délibérément supprimés, selon confirmation de l’utilisateur. Les résumés publiés restent historiques ; ils ne remplacent ni le scellement, ni les sources exactes, ni les payloads et le hook GPU disparus. Aucun candidat CORE-C, redesign natif, correctif GPU, succès OOM ou contrat opérationnel nouveau n’est démontré. La politique OOM et la recommandation restent **UNDECIDED**.

Les [reçus compacts](../../tooling/probes/step20c-corec-prealloc-gate/README.md) sont des preuves de ce blocage et des seules commandes hors ligne exécutées. Le [résultat structuré](../../tooling/probes/step20c-corec-prealloc-gate/evidence/results.json) est un snapshot avant revue/publication : CORE_C_FINAL_INDEPENDENT_REVIEW et DOCUMENTARY_PUBLICATION sont représentés par les marqueurs exacts `COREC_FINAL_INDEPENDENT_REVIEW=NOT_PROVEN` et `COREC_DOCUMENTARY_PUBLICATION=BLOCKED`. Les éventuels reçus ultérieurs doivent enregistrer la revue et la publication réellement accomplies sans réécrire cette édition ni anticiper PASS.

Le petit LAB de reçus a été déplacé de `/home/fy59/swayfx-mosaic-corec-prealloc-hm3xzpzi` vers `/tmp/swayfx-mosaic-corec-prealloc-hm3xzpzi`, suivant la préférence de stockage exprimée par l’utilisateur. Aucun nouveau LAB ne reste dans home. Les chemins originaux des argv restent intacts dans les reçus ; le [reçu de déplacement](../../tooling/probes/step20c-corec-prealloc-gate/evidence/relocation.json) explique leur résolution actuelle. Les logs bruts se trouvent dans `LAB/tests/`, les quatre XML Khronos dans `LAB/inputs/`. Ce LAB temporaire n’est ni un kit reconstructible ni une conservation durable garantie.

## Gate A : état Git et inputs absents

Le [reçu Git initial](../../tooling/probes/step20c-corec-prealloc-gate/evidence/git-initial.json) consigne la branche `main`, un arbre initial propre (`## main...origin/main`) et le HEAD exact `c9a35ce13726b592072aae52352b74403784551d`, message `test(mosaic): qualify CORE recovery and document OOM and DCC gates`. Les vérifications directes `git ls-remote` d’origin et github donnent ce même SHA pour `refs/heads/main`. Ce constat initial précède les nouveaux reçus et documents ; il ne signifie pas que l’arbre final est propre ou publié.

Le [reçu du gate A](../../tooling/probes/step20c-corec-prealloc-gate/evidence/gate-a.json) constate ENOENT pour les trois fichiers sous `/home/fy59/swayfx-mosaic-core-recovery-qmhckba5/` :

| Reçu requis absent | SHA256 attendu, non revérifié |
| --- | --- |
| `closeout-manifest.json` | `5bd327e106c48ae92d3b00d77041a11b78aec1fbf0e405d27e0ae52e256c7cd4` |
| `closeout.json` | `4281fa76a6e9e8077378c4b772ddd92a5e23dbee225f57b221ae996f93c6e71e` |
| `publication-receipt.json` | `300ac4f7a7a0abdcf6406c41e4a86daac56be2df64da7fe017b252987f518d7d` |

**0/979 entrées et 0/916 fichiers revérifiés.** Les neuf runs/102 captures antérieurs sont REPORTED, sans nouvelle validation. Le CORE privé exact de `/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_/`, les inputs OOM du LAB clos et le hook/payload G1 requis ne sont pas disponibles. Recréer des fichiers à leurs anciens chemins ou reconstruire des preuves depuis la prose ne satisferait pas ce gate. Aucun changement implicite de politique de provenance n’est adopté.

Les identités historiques suivantes, hors wlroots installé, sont **REPORTED**, issues du [dossier V3](STEP20C_CORE_QUALIFICATION_DECISION_V3.md) et du ticket, **pas revérifiées sur leurs artefacts dans ce lot**. Le wlroots installé a été rehashé ici au SHA256 attendu, comme le consigne le reçu de sûreté ; aucune bibliothèque CORE-C n’a été chargée :

| Objet historique | Identité rapportée |
| --- | --- |
| CORE existant | SHA256 `29baf31aa3eeed259825c87d0799fa5d3dc83710afb967154604eb1c6657f965` ; Build ID `1b42e557e38db3440ae8dcf7ac967e4132223365` |
| Pristine | SHA256 `8ac865481bc0487344210cd0e16d8e6c7655b29db887cd58ddc11b0ca22fe494` |
| G1, diagnostic distinct | SHA256 `1905a20fa72ebcc7ec47d1584a4653654280288096a20005199eb75673ac0383` ; premier A rejeté, aucun B/A-return accepté |
| wlroots installé, rehashé ici | `/usr/lib/libwlroots-0.20.so` ; SHA256 `7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`, conforme à l’identité historique attendue |
| Base SwayFX 0.6 | `fd71a6bdc061bd633b488ae7b83e8a6981d22f86` |
| Base SceneFX 0.5 | `37ccd723bef49e6891156ffafce8f549f01446cc` |

Aucun SHA256 CORE-C/O1/G2 ni Build ID CORE-C nouveau n’existe dans ce lot. Les succès des anciens CORE/A/G/C3/G1 ne se transfèrent pas à un candidat absent.

## OOM : comparaison historique et gate natif fermé

Les [options OOM A/B/C](STEP20C_MANDATORY_CLIP_OOM_POLICY_OPTIONS.md) conservent leur portée d’étude C privée :

| Option historique | Allocation et admission rapportées | Coût de structure rapporté | Limite pour ce lot |
| --- | --- | --- | --- |
| A | Allocation au clip ; abort ciblé si échec | 56 octets par arbre clippé | Disponibilité session non approuvée, blocage P1 historique |
| B | Setter bool et masquage synchrone ; owner décide admission | 56 octets par arbre clippé | Admission native, recovery et damage complet non prouvés |
| C | Réservation avant publication de chaque arbre créé ; create peut retourner NULL ; setter sans allocation | 64 octets par arbre créé, réservations inactives retenues jusqu’au destroy, plus overhead allocateur non mesuré | Sources exactes absentes ; propagation NULL et survie native non validées |

Le ticket proposait de tester C sans adopter `PRODUCTION_OOM_POLICY=C`. Cette intention ne démontre pas sa réalisation. Les corps C exacts compilés, arbres factory/roots embarqués/externes, callers create, rollback, listeners, reparent, destroy et anciennes/nouvelles régions damage ne peuvent être qualifiés à partir du seul rapport. Aucun appel setter sur root non préalloué n’est autorisé par cette discussion.

**Tous les nouveaux tests C exact-body, natifs, normal/ASan/UBSan/float-cast et OOM sont NOT_RUN.** Les anciens harnais ne prouvent pas le moteur complet SceneFX, la gestion NULL de SwayFX, les popups réels, saved, animation, dommage ou shutdown. Aucun redesign candidat viable ni coût réel d’allocateur n’a été mesuré. `COREC_PREALLOCATION_SOURCE_AND_C_TESTS=BLOCKED` ; recommandation et politique production **UNDECIDED**.

## Commandes hors ligne réellement exécutées

Les [argv, codes bruts et hashes stdout/stderr](../../tooling/probes/step20c-corec-prealloc-gate/evidence/offline-commands.json) fixent les cinq commandes `python -B` exécutées ; leurs logs privés restent dans `LAB/tests/`. Elles n’ont lancé ni compositeur, ni IPC, ni build, ni staging. Les suites historiques n’ont pas été corrigées ou relancées pour ce dossier.

| Commande / famille | Résultat exact | Cause observée et portée |
| --- | --- | --- |
| unittest discover graphics, `test_*.py` | rc1 ; 20 tests, 15 réussites, 5 erreurs | Fichiers historiques owner/events/saved absents dans le LAB minimal-core |
| unittest discover gpu-field, `test_fixture.py` | rc1 ; 4 méthodes réussies, 1 erreur setUpClass | `RuntimeValidator` échoue à écrire les RGBA avec EDQUOT, errno122 ; les méthodes runtime ne sont pas exécutées |
| unittest discover gpu-field, `test_replay.py` | rc1 ; 0 test, 1 erreur setUpClass | Payload/metadata historiques G1 absents |
| unittest discover saved-input-gpu-batch, `test_native.py` | rc1 ; 5 tests, 3 réussites, 1 FAIL, 1 erreur | Log overnight absent ; agrégation targeted vide `(0,0,0)` au lieu de `(821,789,32)` |
| `step20c-core-recovery/audit.py --output …/tests/legacy-audit-result.json` | rc1 ; traceback ; aucun fichier résultat créé | `minimal-core-2l7riqt_/closeout.json` absent |

Ces échecs actuels ne réécrivent pas les succès publiés des campagnes historiques. Les trois tests synthétiques natifs réussis n’observent aucun nouvel événement CORE-C ; les quatre tests GPU de modèle réussis ne prouvent aucune acquisition GPU. Les rejets d’admission, verrou exclusif, réservation atomique/fsync, tokens/SHA/wlroots/reviewer/socket/budgets et tests négatifs nouveaux restent **NOT_RUN**. Un budget disponible n’est pas une admission validée.

## Matrice neuve : zéro réservation, zéro acquisition

| ID | Question prévue | Binaire prévu | État réel |
| --- | --- | --- | --- |
| C1 | Horizontal, deux chaînes nested, retour splith complet | CORE-C | NOT_RUN |
| C2 | Vertical y=600 et input visible/interdit | CORE-C | NOT_RUN |
| C3 | Hidden-owner, même chaîne au retour sans outside click | CORE-C | NOT_RUN |
| C4 | Saved tenu, timeout naturel, live et fermeture normale | CORE-C | NOT_RUN |
| C5 | Resize/migration et input sur owner appliqué | CORE-C | NOT_RUN |
| C6 | Contrôle fullscreen non feuille réellement traversant | Pristine | NOT_RUN |
| C7 | Fullscreen comparable avec ascendance/géométrie équivalentes | CORE-C | NOT_RUN |
| C8 | Fractional scale ou R90 discriminant après gate source | CORE-C | NOT_RUN |
| O1 | Injection sidecar ciblée à l’admission, diagnostic distinct revu | OOM distinct | NOT_RUN |
| G2 | Readback A/B/A et précision/état GL attestés | GPU distinct | NOT_RUN |
| G3 | Contrôle GPU pristine optionnel si attribution requise | Pristine GPU | NOT_RUN |

Chaque ligne a **0 réservation et 0 capture**. C1–O1 sont arrêtés au gate source/provenance ; G2/G3 manquent aussi de hook/payload et de contrat d’observation complet. Fullscreen traversant, vrais grabs et équivalence des arbres ne sont pas certifiés ; aucune démonstration triviale n’est comptée. Toutes les cases de cette nouvelle matrice sont **NOT TESTED**, sans héritage des résultats S historiques.

Plafonds du ticket : **11 runs, 176 captures output, 18 captures maximum/run, 150 s/run, 3 builds SceneFX + 3 builds Mosaic, 3 stages DESTDIR**. Consommation : **0 run, 0 capture output, 0 PNG source marqueur, 0 build SceneFX, 0 build Mosaic, 0 stage**. Aucun retry, ancien token réutilisé, dépassement, remboursement ou nouvelle autorisation runtime ne découle de ces zéros. Les quotas locaux n’ont pas été réservés. La revue du présent dossier ne vaut pas revue d’un launcher inexistant.

## GPU : analyse prospective, préflight NOT_PROVEN

Le [rapport DCC antérieur](STEP20C_GPU_DCC_MODIFIER_AWARE_VALIDATION.md) rapporte le modifier AMD `020000001046bb04` : vendor2, tile version GFX11=4, tile27, DCC1, RETILE0, PIPE_ALIGN1. Pour ses neuf objets 800×600, plane0 image `[pitch,offset]=[3584,0]`, plane1 auxiliaire DCC `[1024,2293760]`. Ces valeurs sont **REPORTED, pas relues sur les payloads**. Exiger width×4 du plan auxiliaire était un prédicat inadapté ; le réparer ne prouve pas alignements, FD, taille physique/étendue auxiliaire, succès readback, GPU completion ou causalité DCC. `GPU_DCC_METADATA=NOT_PROVEN` pour ce lot.

Le rapprochement effectif du hook G1, du programme lié, des shaders compilés et de leur version de langage est **NOT_PROVEN**. Les neuf positions du tableau GL/PACK historique ne sont pas associées ici à des GLenum vérifiés : leur mapping reste inconnu sans le hook. Aucun contrat complet de Phase F ni préflight G2 corrigé n’est déclaré accepté.

Les références primaires orientent une future spécification ; elles ne certifient pas le programme absent :

- [glGetUniform](https://raw.githubusercontent.com/KhronosGroup/OpenGL-Refpages/main/es3.0/glGetUniform.xml) décrit la consultation d’une valeur uniforme courante du programme. Les bits consultés ne prouvent pas l’arithmétique effective des instructions shader.
- [glGetShaderPrecisionFormat](https://raw.githubusercontent.com/KhronosGroup/OpenGL-Refpages/main/es3.0/glGetShaderPrecisionFormat.xml) renseigne les plages et précisions supportées par le compilateur pour le type/stage demandé. Cette capacité ne mesure pas chaque opération exécutée du programme.
- La [spécification GLSL ES 3.20, section 4.7](https://registry.khronos.org/OpenGL/specs/es/3.2/GLSL_ES_Specification_3.20.html) définit des exigences de précision ; `mediump` ne justifie pas une égalité bit à bit avec l’expression CPU float32. L’applicabilité dépend du langage/contexte réellement établi. On ne déduit ni epsilon des différences G1, ni modèle GPU float64, ni causalité d’une quantification supposée.
- [glReadPixels](https://raw.githubusercontent.com/KhronosGroup/OpenGL-Refpages/main/es3.0/glReadPixels.xml) impose ses conditions de lecture et d’état. Sentinel alpha, FBO complet ou hash du fichier ne suffisent pas à établir `read_success` : ils peuvent être compatibles avec des octets antérieurs ou une erreur non attribuée.
- [glGetError](https://raw.githubusercontent.com/KhronosGroup/OpenGL-Refpages/main/es3.0/glGetError.xml) consomme les indicateurs d’erreur retournés ; cette observation ne permet pas de restaurer la queue d’erreurs antérieure. Une neutralité fondée sur sa seule restauration est donc injustifiée.

Les quatre XML ont été récupérés dans `LAB/inputs/` ; leurs tailles et SHA256 sont conservés dans le [reçu des sources Khronos](../../tooling/probes/step20c-corec-prealloc-gate/evidence/khronos-primary-sources.json). Les liens GitHub `main` sont mobiles ; ces hashes fixent les octets effectivement récupérés, sans prétendre pinner leur contenu futur. La page GLSL est une référence de spécification, sans lien démontré à la version shader G1.

Avant toute future réservation G2, il faudrait un hook isolé dans un diagnostic distinct et identifiable, l’attribution des erreurs préexistantes/produites par la lecture, la restauration des états modifiés observables, et des tests négatifs bornés sur les vrais corps : mauvais contexte/programme/FBO/attachment, erreur antérieure, échec lecture, payload inchangé/tronqué et restauration défectueuse. Le programme lié, uniformes, précision supportée, état PACK, provenance des octets et limites d’attribution doivent être revus sur les inputs exacts. Ces exigences sont prospectives ; **aucun nouveau hook/test négatif n’a été exécuté ou accepté**. G2 runtime **NOT_RUN**, effective halfpixel/read_success/whole-field/output-buffer identity **NOT_PROVEN**. Aucun shader, clear, clamp, sampler ou tolérance ajustée n’est adopté.

## Cohérence, damage, lifetime et maintenance

Sans CORE-C exécuté, aucun tuple natif `(run,output,commit_seq)` nouveau, commit/present, identité buffer, état applied/input ou completion GPU n’existe à auditer. Les comptes historiques 57/55/2, 821/789/32 et 414/400/14 restent REPORTED et non rejoués ; une absence de present n’a pas de cause déduite. L’agrégation vide d’une suite échouée n’est pas une mesure runtime zéro.

Atomic generation, buffer identity, completion GPU, lifetime/retrait saved et cohérence native input sont **NOT_PROVEN**. Le contrat canonique qui exige rendu/input sur le même état appliqué demeure ; aucun compteur ou mécanisme n’est choisi. Sampled damage CORE-C est **NOT_PROVEN** ; couverture de toutes les frames, stale pixels, ancien/new damage, décorations, ombres, blur/cache et saved sont **NOT TESTED** dans ce lot. Les anciens échantillons positifs ne ferment pas ces gates.

ELF/Build ID/SHA/DT_NEEDED/relocations/symboles/layouts/liaison archive, modèle, stage et qualification de la paire exacte sont **NOT_RUN** pour CORE-C. Aucune ABI future n’est garantie. Les obligations de maintenance SceneFX/wlroots, full package, notices PARTIAL/LEGAL_NOT_APPROVED, revue juridique et responsabilités release/security demeurent ouvertes. Aucun package, pin, dépendance système ou autorité compositor n’est changé.

## Priorités et plus petite suite justifiée

| Niveau | Blocage ou limite | Suite admissible |
| --- | --- | --- |
| P0 de ce ticket | Provenance obligatoire, sources exactes et payload/hook absents ; aucun CORE-C admissible | Restaurer des inputs autoritatifs exacts si une sauvegarde existe, ou définir séparément une instruction changeant/redéfinissant le gate de provenance |
| P1 historique | Disponibilité OOM A non approuvée ; C natif/NULL/rollback non testé ; read-success et attribution GL non prouvés | Étude future seulement après résolution du gate et revue des inputs exacts |
| P2 de qualification | Fullscreen comparable, précision/whole-field GPU, coherence/lifetime/damage complet, ABI/package/maintenance/legal | Conserver les gates ouverts ; ne pas transférer les succès historiques |

Cette classification décrit l’ordre de travail du ticket ; elle ne transforme pas chaque limite en bug produit établi. La plus petite étape actuelle est **une instruction séparément cadrée sur le gate de provenance, ou la restauration d’inputs exacts autoritatifs si une sauvegarde existe**. La suppression volontaire ne permet pas de promettre une récupération ; aucune recherche/reconstruction des données supprimées ni réécriture historique n’est prescrite. Aucun run supplémentaire ne doit précéder un gate admissible.

Le [reçu de sûreté](../../tooling/probes/step20c-corec-prealloc-gate/evidence/safety.json) compare 314 fichiers de production sans delta et les hashes protégés PKGBUILD/patch/AGENTS/UX/Packaging, `/usr/bin/sway`, wlroots et SceneFX inchangés. Il relève zéro socket privé, zéro processus graphique lancé par ce ticket et zéro appel IPC live. Sans snapshot initial de processus, aucune continuité PID mesurée n’est revendiquée. Lors du contrôle de sûreté, le LAB hors home contenait 179747 octets de fichiers réguliers ; cette taille est celle du snapshot avant revue, pas celle du LAB final après ajout de reçus ultérieurs.

Aucune source de production, test existant, fixture historique, UX, packaging, PKGBUILD, patch cumulatif, pin, bibliothèque système, dotfile, QuickShell ou session quotidienne n’a été modifié par cette clôture documentaire. Aucun build, installation, lancement headless, socket IPC ou déploiement nouveau ; aucune commande stage/commit/push dans cette intervention documentaire.

## Marqueurs de l’édition avant revue/publication

```text
COREC_CONTRACTS_AND_HISTORICAL_EVIDENCE=BLOCKED
COREC_PREALLOCATION_SOURCE_AND_C_TESTS=BLOCKED
COREC_BUILD_ELF_AND_STAGE=NOT_RUN
COREC_HORIZONTAL=NOT_RUN
COREC_VERTICAL=NOT_RUN
COREC_HIDDEN_SAME_CHAIN=NOT_RUN
COREC_SAVED_NATURAL_TIMEOUT=NOT_RUN
COREC_DYNAMIC=NOT_RUN
COREC_FULLSCREEN_CONTROL=NOT_RUN
COREC_FULLSCREEN_COMPARISON=NOT_RUN
COREC_FRACTIONAL_OR_R90=NOT_RUN
COREC_NATIVE_OOM_INJECTION=NOT_RUN
COREC_OOM_POLICY_RECOMMENDATION=UNDECIDED
COREC_PRODUCTION_OOM_POLICY=UNDECIDED
GPU_G2_PREFLIGHT=NOT_PROVEN
GPU_G2_RUNTIME=NOT_RUN
GPU_EFFECTIVE_HALFP_PIXEL=NOT_PROVEN
GPU_READ_SUCCESS=NOT_PROVEN
GPU_DCC_METADATA=NOT_PROVEN
GPU_WHOLE_FIELD_CAUSALITY=NOT_PROVEN
GPU_OUTPUT_BUFFER_IDENTITY=NOT_PROVEN
COREC_SAMPLED_DAMAGE=NOT_PROVEN
COREC_NATIVE_LIFETIME=NOT_PROVEN
COREC_INPUT_COHERENCE=NOT_PROVEN
COREC_ATOMIC_GENERATION=NOT_PROVEN
COREC_FINAL_INDEPENDENT_REVIEW=NOT_PROVEN
COREC_DOCUMENTARY_PUBLICATION=BLOCKED
SWAYFX_MOSAIC_STEP20C_OOM_PREALLOC_NATIVE_CORE_AND_GPU_PRECISION_BATCH_V1=BLOCKED
STEP20A=DONE
STEP20B=EXPERIMENTAL
STEP20C=NEXT
STEP20D_G=PLANNED
PRODUCTION_MULTI_OUTPUT=NOT_YET_SUPPORTED
PRODUCTION_AUTHORIZED=FALSE
```
