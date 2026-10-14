# STEP20C — retour du propriétaire caché et lifecycle saved

> EXPERIMENTAL — édition du 2026-10-14, avant audit final et publication. Ticket `SWAYFX_MOSAIC_STEP20C_CORE_RECOVERY_OOM_AND_DCC_QUALIFICATION_BATCH_V1`. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT_YET_SUPPORTED ; PRODUCTION_AUTHORIZED=FALSE. Aucun contrat production, UX ou package adopté.

LAB désigne `/home/fy59/swayfx-mosaic-core-recovery-qmhckba5`, hors Git. Le [dossier V3](STEP20C_CORE_QUALIFICATION_DECISION_V3.md), la [fixture source-only](../../tooling/probes/step20c-core-recovery/README.md), ses [résultats compacts](../../tooling/probes/step20c-core-recovery/evidence/results.json) et sa [provenance](../../tooling/probes/step20c-core-recovery/provenance.json) fixent les identités, budgets et limites. Les chemins LAB sont des références locales ; les binaires, PNG et traces restent privés. Aucun résultat historique n’est réécrit.

## S7 : même chaîne cachée puis revenue

S7-core-hidden-return consomme12 PNG, sans retry. H1/H2 font800×600, scale1, transform normal, origines(-800,0)/(0,0). Le CORE exact29baf31 conserve une chaîne XDG TOPLEVEL→A→B avec vrais grabs59/68. Le mouvement pendant la phase entièrement cachée n’envoie aucun outside click de dismissal ; aucun popup_done n’est observé. Au retour, les mêmes IDs et serials restent présents, H1 RGB entière retrouve exactement sa capture mappée d’origine et H2 reste EXACT. Le bouton visible atteint B, puis les fermetures normales/SHM se terminent sans erreur Wayland.

Cette séparation répond à la lacune historique E5 : un dismissal avait déjà détruit sa chaîne avant le retour. E5 reste NOT_EXERCISED pour ce retour et son dismissal reste une preuve historique, pas un nouveau run. La seconde chaîne destructive facultative est omise dans S7 ; elle n’est pas annoncée testée. Ce cas move-only n’adopte aucune politique de hide/dismiss/reposition ni click-through sous grab.

**CORE_HIDDEN_RETURN=PARTIALLY_FEASIBLE**, borné à cette chaîne, ces captures et ces callbacks. Les IDs complets et hashes de captures sont liés dans les [résultats](../../tooling/probes/step20c-core-recovery/evidence/results.json) et `LAB/graphics/runs/S7-core-hidden-return/run/`.

Les deux S7/S8 utilisent owner10, workspace nommé1/id6 sur H1. S7 observe scene appliquée[-320,0,640,600], origine surface(-318,25), destination636×573 ; le buffer SHM natif du toplevel nested reste420×320. Les buffers natifs A350×170/B300×130 portent les IDs de protocole A[12,11,14], B[15,13,17] et TOPLEVEL[3,9,10]. A est[-218,105,350,170] et B[-118,165,300,130] à l’ouverture/restitution. Le rect logique propriétaire[480,25,640,575] ne doit pas être confondu avec la scene translatée par la caméra. Les décorations restent25px/current_border_width2.

## S8 : justification et phases saved

Le replay historique E6 démontre déjà HOLD→timeout naturel→release→ACK/live, H2 entière exacte. Sa capture post-release n’était pas manquante. Son verdict INCONCLUSIVE reste inchangé ; manquaient surtout normal-close explicite, SHM release et restauration finale après fermeture. S8 est réservé pour ces critères distincts, et non pour remplacer le reçu E6 rejeté.

S8-core-saved consomme10 PNG sur le même CORE, outputs800×600 scale1 transform normal, origines(-800,0)/(0,0). Les assertions sont faites par phase : une phase HOLD ne doit pas exiger une future ACK ; une phase live exige la release puis son ACK/commit. Le timeout expérimental demandé est cinq secondes, pas une qualification du timeout ordinaire200ms.

| Événement S8 | Temps monotone ns | Portée |
| --- | ---: | --- |
| Configure39 retenu | 274133187912812 | HOLD client observé |
| Observation après timeout naturel | 274138196687791 | Transaction expirée avant release |
| Release client | 274138248180402 | Commande de libération après observation |
| ACK39 | 274138251383305 | Après release |
| Nouveau commit | 274138252420086 | Après ACK |

La référence H2 entière est EXACT avant HOLD, durant HOLD, au timeout naturel, après restauration live et après fermeture finale. Le client répond à normalclose, ses trois SHM buffers sont relâchés3/3, le code Wayland est0 et le processus sort0. Les captures H1 distinguent les phases ; cette chronologie est corrélée au fil client et au timeout du CORE exact.

Le CORE n’a pas les hooks PI/C3 : l’identité native du saved node et son retrait sont **NOT_OBSERVABLE**. Une disparition visuelle après timeout n’identifie ni l’instance saved, ni le buffer GPU, ni sa retraite. C3 historique ne se transfère pas au CORE ; **CORE_SAVED_EPOCH=PARTIALLY_FEASIBLE**, **CORE_BUFFER_IDENTITY=NOT_PROVEN**, **CORE_ATOMIC_GENERATION=NOT_PROVEN**.

S8 utilise un vrai client saved SHM : initial636×573, configure39 demande636×513 ; la génération held reste au buffer initial jusqu’à release/ACK, puis commit live636×513. Le workspace redimensionné est[-770,30,740,540], destination owner636×513 ; ce n’est pas une simple déduction depuis la géométrie420×320 initiale IPC. Aucun popup/grab n’est lancé dans S8. Les détails natifs/configure/destination sont liés dans saved-evidence.json, sans identité native saved node.

## Fermeture, input et damage

Les deux runners sortent0 ; tous leurs clients et compositeurs sortent0 ; scientific_cleanup et mechanical_cleanup passent. Chacun conserve séparément terminal IPC1. Les reçus bruts architecture INCONCLUSIVE demeurent archivés. La [revue runtime limitée](../../tooling/probes/step20c-core-recovery/evidence/runtime-evidence-accepted.json) vérifie les captures/fermetures et accepte seulement la fidélité des conclusions ciblées.

Les snapshots applied et les callbacks pointer sont corrélés dans leurs fenêtres temporelles ; une origine antérieure à une mutation caméra ne remplace pas l’origine compatible avec le callback. Damage conserve les extents soumis et les RGB stabilisées ; les périodes sans trace, l’identité du buffer présenté et l’union minimale de toutes les régions ne sont pas observables. Aucun contrat de génération atomique n’est établi.

La prochaine petite étape serait un scope explicitement autorisé d’observabilité native saved/lifetime sur un nouveau diagnostic, en conservant l’exigence que rendu et input correspondent au même état appliqué. Aucun compteur particulier ni nouveau run n’est adopté ici.
