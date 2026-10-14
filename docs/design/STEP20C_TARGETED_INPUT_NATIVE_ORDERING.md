# STEP20C — input ciblé et ordre natif

> EXPERIMENTAL — édition du 2026-10-14, clôture documentaire des quatorze runs ciblés, diagnostic C3 inclus. Revue finale indépendante : ACCEPTED, audit PASS pour la fidélité de l’évidence expérimentale. Publication documentaire autorisée et préparée, non exécutée à cette édition. Le diagnostic C3 est exécuté : résultat INCONCLUSIVE, observations natives partielles sans transfert à A/G. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED. Multi-output de production : NOT YET SUPPORTED. Aucune intégration, installation ou décision UX.

L’autorité brute est le LAB privé `/home/fy59/swayfx-mosaic-targeted-7gge6h8b` ; HIST désigne `/home/fy59/swayfx-mosaic-overnight-mcolx0gq`. Les chemins LAB/HIST sont des artefacts externes locaux, pas des fichiers distribués. Le [rapport de clôture](STEP20C_TARGETED_CLOSURE_DECISION.md) donne les identités exactes, la matrice des quatorze runs et les limites. Les sources de [fixture ciblé](../../tooling/probes/step20c-targeted/README.md) restent des entrées expérimentales ; elles n’ajoutent aucune dépendance de production. Les rapports historiques et leurs verdicts restent inchangés.

## Géométrie appliquée pendant le clic

Le pristine a huit PNG et complète le contrôle standard full/empty/full, focus/layout et fermeture normale. A/G ont cinq PNG chacun ; les deux s’arrêtent au troisième clic après restauration full. Les boutons owner45/46 sont réellement livrés au point global (-314,30). La fixture avait capturé une origine (-318,25), mais le focus provoqué dans la fenêtre du clic déplace la caméra ; la dernière origine native est (-638,25) et le motion livré (324,5) lui correspond exactement.

La nouvelle lecture avant clic n’a pas couvert la mutation camera/focus pendant clic. L’arrêt `Ambiguous: logical pointer correlation` reste **INCONCLUSIVE** pour la campagne. Ce n’est ni une panne démontrée de routing produit, ni une preuve d’atomicité. La suite camera/layout et normal owner close A/G sont **NOT EXERCISED** ; leur scientific cleanup est INCONCLUSIVE, distinct de processus 0/reaped/runtime_removed. Le pristine garde son contrôle standard FEASIBLE ; son runtime brut est lui aussi INCONCLUSIVE sur IPC terminal1, sans exigence de PI privée dans le contrôle.

## Replay des commits et presents

La relecture de tous les57 commits du F historique trouve55 paires et2 `MISSING_PRESENT`, clés (HEADLESS-1,2) et (HEADLESS-2,2). Le compte10/12 du rapport initial portait un sous-ensemble ; le rapport historique reste intact. Le replay complémentaire est LAB `parent/offline-native-summary.json`.

Les treize runs initiaux contiennent 788 commits,758 paires et 30 missing. C3 ajoute 33/31/2 : total final 14 runs,821 commits,789 paires et 32 missing. Le matching utilise **(output, commit_seq)**, jamais un numéro sans output. Pristine ne possède pas d’instrumentation PI :0 ne signifie pas absence de commits natifs. Le backend headless diffère le present d’un commit accepté et peut annuler un callback lors du teardown ; source audit et pairage sont des propriétés distinctes.

Aucune paire ne lie ici les pixels physiques, l’identité du buffer GPU, son lock/release ou la génération atomique du hit. La fenêtre naturelle commit→mutation input→present discriminante reste **NOT EXERCISED**. Les callbacks de scène appliquée, événements wire client, IPC et native present ne forment pas automatiquement une génération commune. Damage complet et lifetime restent **NOT PROVEN**.

Les observations fraîches input du run G dynamique qualifient leurs points propres ; elles ne complètent pas la suite input-A/G interrompue. Un futur fixture doit accepter ou mesurer la mutation pendant la livraison sans supposer une origine capturée immuable. Preuves : LAB `runs/input-{pristine,A,G}/run/`, `parent/run-summary.json`, `reviews/runtime-validation-13.json`, `parent/native-lifetime-audit.json`.
