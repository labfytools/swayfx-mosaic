# STEP20C — récupération des contrôles standard, vertical et fullscreen

> EXPERIMENTAL — édition du 2026-10-14, avant audit final et publication. Ticket `SWAYFX_MOSAIC_STEP20C_CORE_RECOVERY_OOM_AND_DCC_QUALIFICATION_BATCH_V1`. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT_YET_SUPPORTED ; PRODUCTION_AUTHORIZED=FALSE. Aucun contrat production, UX ou package adopté.

LAB désigne `/home/fy59/swayfx-mosaic-core-recovery-qmhckba5`, hors Git. Le [dossier V3](STEP20C_CORE_QUALIFICATION_DECISION_V3.md), la [fixture source-only](../../tooling/probes/step20c-core-recovery/README.md), ses [résultats compacts](../../tooling/probes/step20c-core-recovery/evidence/results.json) et sa [provenance](../../tooling/probes/step20c-core-recovery/provenance.json) fixent les identités, budgets et limites. Les chemins LAB sont des références locales ; les binaires, PNG et traces restent privés. Aucun résultat historique n’est réécrit.

## Périmètre et qualité des fixtures

Le CORE exact SHA256 `29baf31aa3eeed259825c87d0799fa5d3dc83710afb967154604eb1c6657f965` est réutilisé sans build. Le contrôle pristine SHA256 `8ac865481bc0487344210cd0e16d8e6c7655b29db887cd58ddc11b0ca22fe494` reste distinct. Les deux utilisent la paire wlroots contrôlée et un renderer FX GLES réel ; aucun résultat des anciens diagnostics A/G/C3/G1 n’est attribué au CORE.

Le replay `LAB/graphics/historical-replay.json` conserve E0-pristine/E0-core/E2 sans PNG, le défaut d’ascendance de la seconde chaîne E1, l’ancêtre non feuille réel E4 et le dismissal E5 avant retour. E6 avait déjà un timeout réel : son verdict gelé reste INCONCLUSIVE. Les prédicats ne sélectionnent plus un propriétaire à partir d’un index arbitraire ; le workspace et l’ascendance tiled sont vérifiés explicitement.

La première revue a reproduit INITIAL-P1-01 : une fermeture SHM invalide pouvait laisser un statut global/scientifique PASS. Un seul delta R1 rend l’échec bloquant et conserve les reçus de fermeture explicite. La [revue du delta](../../tooling/probes/step20c-core-recovery/evidence/graphics-delta-accepted.json) accepte le manifeste `ed0c2be50d067f273e884c338b607a47d066d3a290432df99a513c620346fbc7`, 565 entrées vérifiées, aucun écart. Vingt tests offline couvrent notamment les chemins réellement appelés main/normal_remaining/cleanup, pas seulement un modèle de fermeture. Cette acceptation autorisait uniquement les neuf cas S prévus.

## Résultats nouveaux

Tous les outputs mesurés font 800×600, scale1, transform normal. S0/S1/S2/S5/S6 utilisent H1 à (-800,0), H2 à (0,0) ; S3/S4 H1 à (0,0), H2 à (0,600). La configuration privée et les snapshots de chaque run constituent l’autorité des coordonnées. Chaque lancement `python -B run.py <id>` se fait dans `LAB/graphics`, avec runtime 0700 et socket explicite. Les relations natives configure→ACK→map et les serials de vrais boutons sont archivés.

| Run | PNG | Résultat ciblé | Verdict scientifique |
| --- | ---: | --- | --- |
| S0-pristine-standard | 12 | Débordement standard A/B, input B puis B-close et input A survivant, H2 finale exacte | PARTIALLY_FEASIBLE |
| S1-core-standard | 12 | Même scénario standard, douze RGB entières homologues exactes avec S0 | PARTIALLY_FEASIBLE |
| S2-core-horizontal | 16 | Deux chaînes, quatre grabs, Mosaic→splith, B-close/A-survie et H2 finale exacte | PARTIALLY_FEASIBLE |
| S3-pristine-vertical | 8 | A/B traversent y=600, pixels/input sur H2 standard | PARTIALLY_FEASIBLE |
| S4-core-vertical | 8 | Même traversée Y, H1 visible, H2 protégée et input interdit échantillonné | PARTIALLY_FEASIBLE |
| S5-pristine-fullscreen | 12 | Ancêtre non feuille fullscreen réel, mais aucun popup traversant | INCONCLUSIVE |
| S6-core-fullscreen | 12 | Ancêtre non feuille fullscreen réel, comparaison non équivalente | INCONCLUSIVE |

Les sept runners sortent0, les compositeurs et clients sortent0, les fermetures explicites/SHM et nettoyages scientifique/mécanique passent. Les sept transports IPC terminaux sortent1 (`Unable to receive IPC response`) et sont conservés séparément. Les reçus bruts `architecture_verdict=INCONCLUSIVE` ne sont pas remplacés par les verdicts ciblés dérivés. La [revue runtime limitée](../../tooling/probes/step20c-core-recovery/evidence/runtime-evidence-accepted.json) accepte la fidélité des mesures, sans qualification production.

## Identités, destination et buffers natifs

Tous les propriétaires ci-dessous sont sur workspace nommé1/id6 et HEADLESS-1. Ils sont tiled (`floating=auto_off`) ; la frontière renderer/input est contrôlée après mutation par peinture et coordonnées pointer fraîches. Le champ rect IPC reste une géométrie candidate pending, pas un epoch natif : scene et origine appliquée peuvent différer sous caméra.

| Run | Owner | Scene appliquée `[x,y,w,h]` | Origine surface appliquée | Destination window_rect `w×h` | Grabs réels A/B |
| --- | ---: | --- | --- | --- | --- |
| S0 |9 |[-400,0,400,600] |(-398,25) |396×573 |29/38 |
| S1 |9 |[-400,0,400,600] |(-398,25) |396×573 |29/38 |
| S2, seconde chaîne au contrôle standard |10 |[-400,0,400,600] |(-398,25) |396×573 |31/40 puis83/92 |
| S3 |9 |[400,0,400,600] |(402,25) |396×573 |27/36 |
| S4 |9 |[160,0,640,600] |(162,25) |636×573 |29/38 |
| S5 fullscreen |9 |[-800,0,800,300] |(-798,25) |796×273 |50/59 |
| S6 fullscreen |9 |[-800,0,800,600] |(-798,25) |796×573 |49/58 |

Le toplevel du client nested garde son **buffer SHM natif420×320**, même lorsque le compositor lui configure une destination différente. L’IPC geometry420×320 ne doit donc pas être pris pour la taille de la cellule. Les popups natifs sont350×170 et300×130 en horizontal/fullscreen,250×170 et170×130 en vertical, avec leurs propres configure/ACK/buffers. Les bordures restent `normal`, current_border_width2, avec décoration25px : un état root border none n’annule pas ces décorations propriétaires. Les snapshots, wire logs et captures natifs distincts sont conservés par run.

## Standard et retour horizontal

S0/S1 ont A `[-298,105,350,170]` et B `[-198,165,300,130]`, notation `[x,y,width,height]`, avec grabs29/38. Les douze images RGB entières homologues (480000 pixels chacune) sont EXACT, y compris le débordement standard, la survie A après fermeture B et le retour final. Ce contrôle qualifie les états échantillonnés du code statique en standard ; il n’établit pas une neutralité universelle.

S2 exerce les grabs31/40 puis83/92, chacun issu du bouton réel correspondant. Le workspace1/H1 et son layout sont sélectionnés et vérifiés avant le spawn de la seconde chaîne, puis son propriétaire est validé par PID et ascendance après map : le défaut E1 n’est pas répété. A/B traversent x=0, respectivement `[-218,105,350,170]` et `[-118,165,300,130]`. H2 entière reste identique en Mosaic pour les deux chaînes. Après retour splith avec popups encore vivants, H2 change de16380 pixels, puis8840 après B-close, puis0 après fermeture finale. Input standard B puis A survivant est observé. La clôture préserve l’identité du propriétaire et les relations XDG ; aucun click-through universel n’en découle.

## Traversée verticale réelle et limite du champ brut

A couvre y505..675 ; B y585..715, de part et d’autre de y600. Le contrôle pristine mesure sur H2 A6000 pixels et B19550 pixels, avec input réel. Le CORE mesure0 pixel A/B sur H2 et conserve H2 entière EXACT, avec input visible sur H1 et absence de bouton dans la zone exclue échantillonnée.

Le fichier brut `geometry.crossing` dit `NOT EXERCISED` : son helper générique utilise X et la frontière0 par défaut. Ce champ n’a pas été corrigé après le run. Le runner a exécuté le prédicat Y/600 et les bornes numériques configurées ci-dessus démontrent séparément la traversée verticale. Il faut lire ces deux sources ensemble ; une assertion X ne suffit pas à qualifier Y. Pristine et Mosaic ont des origines X propriétaires différentes, ce qui explique des images H1 différentes ; on ne prétend pas une égalité entière H1 entre layouts.

## Fullscreen : contrôle présent, comparaison non close

S5/S6 observent tous deux l’ancêtre current con10, non feuille, fullscreen_mode1. Les popups restent entièrement dans H1 : A x[-698,-348], B x[-598,-298]. Aucun débordement vers H2 n’exerce donc le bypass de clipping visé : traversée fullscreen **NOT_EXERCISED**.

De plus, l’ancêtre pristine possède deux enfants et un owner haut de275 ; le CORE un enfant et un owner haut de575. Les RGB différentes ne sont pas un défaut Mosaic attribuable sous un contrôle non équivalent. Le retour standard et les fermetures passent, mais **CORE_FULLSCREEN_COMPARISON=INCONCLUSIVE**. Aucune politique offscreen/fullscreen n’est décidée et aucun retry n’est autorisé par ce rapport.

## Frontière

CORE_STANDARD_CONTROL, CORE_HORIZONTAL_RETURN et CORE_VERTICAL_CROSSING restent PARTIALLY_FEASIBLE. Les régions et événements non échantillonnés sont NOT TESTED/NOT_OBSERVABLE ; native buffer identity, atomic generation et complete damage restent NOT PROVEN. Le plus petit futur travail fullscreen serait de définir hors ligne un contrôle réellement équivalent et traversant, puis de demander un scope runtime distinct. STEP20C reste NEXT.
