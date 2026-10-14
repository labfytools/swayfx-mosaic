# STEP20C — validation DMA-BUF AMD/DCC par plan

> EXPERIMENTAL — édition du 2026-10-14, avant audit final et publication. Ticket `SWAYFX_MOSAIC_STEP20C_CORE_RECOVERY_OOM_AND_DCC_QUALIFICATION_BATCH_V1`. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT_YET_SUPPORTED ; PRODUCTION_AUTHORIZED=FALSE. Aucun contrat production, UX ou package adopté.

LAB désigne `/home/fy59/swayfx-mosaic-core-recovery-qmhckba5`, hors Git. Le [dossier V3](STEP20C_CORE_QUALIFICATION_DECISION_V3.md), la [fixture source-only](../../tooling/probes/step20c-core-recovery/README.md), ses [résultats compacts](../../tooling/probes/step20c-core-recovery/evidence/results.json) et sa [provenance](../../tooling/probes/step20c-core-recovery/provenance.json) fixent les identités, budgets et limites. Les chemins LAB sont des références locales ; les binaires, PNG et traces restent privés. Aucun résultat historique n’est réécrit.

## Verdict

La réparation isolée du prédicat par plan et36 tests offline passent. Le **gate complet reste INCONCLUSIVE** : la vraie époque G1 est rejetée sur `effective halfpixel`, read_success reste NOT_PROVEN et GL_ERROR_QUEUE UNOBSERVED. **GPU_DCC_DESIGN_REVIEW=NOT_PROVEN ; GPU_DCC_RUNTIME=NOT_RUN ; GPU_WHOLE_FIELD_CAUSALITY=INCONCLUSIVE.** Aucun G2 ni nouveau build GPU/compositeur n’est lancé. La revue initiale accepte la correction offline limitée ; elle n’accepte pas un préflight runtime complet.

G1 historique SHA256 `1905a20fa72ebcc7ec47d1584a4653654280288096a20005199eb75673ac0383`, Build ID `1505e31c3dc08d2a7799c2ee9e1b2705eb61f5fe`, reste distinct du CORE29baf31. Son runner1, son premier A seul et son résultat INCONCLUSIVE sont immuables. Aucun B ni A-return n’a été acquis.

## Contrat explicite du validateur copié

La [fixture GPU](../../tooling/probes/step20c-core-recovery/gpu-field/README.md) lie parents/hash/delta. L’autorité locale est `/usr/include/libdrm/drm_fourcc.h`, SHA256 `992f33804acda60b0b46f1a272942c3592484ea3217d469239f1cb12249de2eb`. La [source primaire Linux UAPI](https://linux.googlesource.com/linux/kernel/git/torvalds/linux/+/refs/heads/master/include/uapi/drm/drm_fourcc.h) corrobore la signification ; le SHA local fixe les octets effectivement utilisés.

Le modifier exact allowlisté `020000001046bb04` décrit AMD=2/GFX11=4, tile27, DCC1, RETILE0, PIPE_ALIGN1. Pour cette disposition, plane0 est l’image et plane1 l’auxiliaire DCC. Les neuf objets historiques800×600 annoncent `[[3584,0],[1024,2293760]]` pour `[pitch,offset]`. Exiger width×4 sur plane1 confondait auxiliaire et pixels image.

Le nouveau prédicat exige un FOURCC packed32 connu, image stride≥width×4 divisible par4, pitch auxiliaire non nul uint32, offsets/arithmetic bornés et nombre de plans cohérent. Son filtre image-before-auxiliary est une restriction de fixture, pas une règle universelle de layout AMD. Formats/modifiers inconnus et incohérences sont rejetés. Le contrôle linéaire un plan est synthétique ; aucun nouveau contrôle GPU non-DCC n’est qualifié.

Les FD et tailles d’allocation ne sont pas observés. Alignement DCC, taille physique tilée, étendue auxiliaire et bornes d’allocation restent NOT_PROVEN. Aucune formule universelle inventée ne transforme une metadata plausible en décodage physique prouvé.

## Replay réel et second blocage

`LAB/gpu-field/replay-result.json` relit les metadata/arm/payload immuables, neuf reads et8312048 octets bruts. Les offsets/ROI/hash, contextes/attachments/channels et les neuf champs GL/PACK sauvés/restaurés passent. L’enveloppe native vérifie11 writes, deux copies, source/destination, ping-pong, texture unit, samplers, matrices, ordre et domaines de composition. Cette enveloppe est **STRUCTURAL_ONLY** et ne remplace pas validate_epoch.

| Stages | Bits uniform observés | Bits float32 attendus par expression source |
| --- | --- | --- |
| 0–2 | 983818240 / 987398144 | 983815946 / 987395086 |
| 3–5 | 967041024 / 970620928 | 967038730 / 970617870 |

Les shaders déclarent mediump et le hook conserve les bits retournés par glGetUniformfv. Une quantification est une hypothèse, pas une cause établie. Le validateur strict rejette `effective halfpixel` ; aucune tolérance ajustée après observation n’est ajoutée et le modèle idéal float64 ne devient pas un modèle d’arithmétique GPU.

Le hook indique lui-même que son sentinel alpha ne prouve pas le succès du read ni la neutralité de la queue GL. Le test de la restauration déclarée ne peut démontrer l’absence d’erreur GL non observée. Corriger cette acquisition exigerait un nouveau contrat/hook/binaire, hors autorisation zéro build de ce ticket. Réutiliser G1 avec un runner neuf ne ferme donc pas ces gates.

Les36 tests couvrent plans/pitches/offsets/fourcc/modifiers inconnus, samples tronqués/corrompus, hash/read validity/sentinel, GL/PACK/context/attachment, ROI, writes/copies manquants, aliases, samplers/uniforms, régions, ordre blur et continuité ping-pong. Le reçu de réparation whitespace du parent-delta est un changement de fixture prospective, pas une réécriture de G1. Les premiers essais de setup non aboutis restent archivés ; ils ne sont pas des résultats GPU acquis.

## Suite bornée

Les16×16 RGBA U0/cache échantillonnées sont exactes ; cache/presubmit diffèrent. Sans whole-field natif ni B/A-return, cela ne détermine ni cause entière H1, ni précision effective, ni causalité DCC. Les FAIL RGB historiques, dont le CORE33789 pixels/max6/5/1, restent inchangés.

Un futur ticket devrait définir l’observabilité read-success/GL error, établir le contrat de précision effective à partir de spécifications primaires et rendre explicites les limites d’allocation/FD, puis faire revoir les octets et le préflight avant toute réservation. Aucun shader, clear, clamp ou sampler n’est changé. L’analyse offline n’empêche pas les campagnes CORE indépendantes déjà achevées.
