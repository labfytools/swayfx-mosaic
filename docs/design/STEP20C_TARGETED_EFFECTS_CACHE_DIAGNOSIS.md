# STEP20C — diagnostic ciblé des effets et du cache

> EXPERIMENTAL — édition du 2026-10-14, clôture documentaire des quatorze runs ciblés, diagnostic C3 inclus. Revue finale indépendante : ACCEPTED, audit PASS pour la fidélité de l’évidence expérimentale. Publication documentaire autorisée et préparée, non exécutée à cette édition. Le diagnostic C3 est exécuté : résultat INCONCLUSIVE, observations natives partielles sans transfert à A/G. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED. Multi-output de production : NOT YET SUPPORTED. Aucune intégration, installation ou décision UX.

L’autorité brute est le LAB privé `/home/fy59/swayfx-mosaic-targeted-7gge6h8b` ; HIST désigne `/home/fy59/swayfx-mosaic-overnight-mcolx0gq`. Les chemins LAB/HIST sont des artefacts externes locaux, pas des fichiers distribués. Le [rapport de clôture](STEP20C_TARGETED_CLOSURE_DECISION.md) donne les identités exactes, la matrice des quatorze runs et les limites. Les sources de [fixture ciblé](../../tooling/probes/step20c-targeted/README.md) restent des entrées expérimentales ; elles n’ajoutent aucune dépendance de production. Les rapports historiques et leurs verdicts restent inchangés.

## Contrôles positifs et échec entier conservé

`FX-pristine`, `FX-A`, `FX-G` possèdent chacun seize PNG. Le fond XRGB haute fréquence, le filler ARGB transparent et le verre SHM connu, prémultiplié `0x88442010` (alpha 136, RGB 68/32/16), séparent l’effet du filtre de la composition alpha. Le classique est **EXERCISED** : 4096 pixels de ROI centrale prospective changent à source constante ; contraste adjacent 12,783069 → 0,090278. Les dumps sources A/B/A confirment A 1/A 3 byte-exacts. L’explication des anciennes images classiques uniformes par filler opaque est **SOURCE_AUDIT_ONLY** : les bytes SHM historiques n’ont pas été retenus.

| Retour optimisé A, image entière sans masque | pristine | A | G |
| --- | ---: | ---: | ---: |
| Pixels RGB différents | 37252 | 34323 | 34323 |
| Bbox locale | [400,0,800,600] | [480,0,800,600] | [480,0,800,600] |
| Delta maximal absolu | 6 | 6 | 6 |
| ROI centrale prospective différente | 0 | 0 | 0 |

La restauration entière H1 est **FAIL** dans les trois variantes. Tous les deltas natifs sont non positifs (R/G jusqu’à -6, B -1). Aucun masque ni ROI choisi après observation ne remplace ce verdict. Les verres ont des domaines visibles différents pristine/Mosaic ; les comptages seuls ne démontrent pas une régression causée par le clip.

Les seize captures homologues A/G sont RGB exactes, sources SHM et géométrie/focus/état IPC normalisé également égaux. Cela réduit l’hypothèse d’un effet visible propre à la trace A dans ce scope ; cela ne prouve pas la neutralité temporelle ou GPU. Les optimizations ont leurs traces natives dans A seulement : commit background → dirty H1 → reconstruction [0,0,800,600], résultat1 → clear dirty → usage du même cache/FBO → output submit et damage plein. Les traces OPT de G/pristine sont **NOT OBSERVABLE** ; aucun événement A n’est extrapolé.

## Modèle, attribution et limite instrumentale

Le diagnostic hors ligne LAB `results/fx-diagnosis/DIAGNOSIS.md` et `diagnosis.json` emploie les noyaux fixes radius 5/trois passes, bilinéaire idéale/arrondi8 bits, état froid zéro sans fit. Le clamp sur texture entière donne68969 pixels dépendants de l’historique ; le clamp au domaine fraîchement écrit donne0. Le modèle produit des deltas positifs jusqu’à33, différents du natif négatif jusqu’à6. Cette divergence est conservée : causalité native **NOT PROVEN / INCONCLUSIVE**. Les tests `diagnose.py` et `verify.py` sont rapportés PASS pour187 hashes d’entrée, comptages indépendants, seize comparaisons A/G, ordre A et noyaux du modèle ; aucun runtime GPU n’a été exécuté par ce diagnostic.

L’observation manquante est le contenu natif des queues ping/pong, du domaine frais, du cache choisi et du buffer output. Une nouvelle escalade de calcul ne supplée pas cette observabilité ; le plus petit discriminant futur est un readback FBO borné lié au vrai buffer output, dans un nouveau budget autorisé. Aucun clamp production, changement ABI ou attribution P0 propre à Mosaic n’est justifié.

## Fermeture clients, ombres et damage

Dans les trois runs les neuf clients FX (glass/background/filler) sont explicitement fermés avant le compositeur ; codes 0/error0, callbacks SHM release réels et absence de nouveau commit après close sont conservés. H1 final est vide, H2 exact. Scientific cleanup PASS pour ce scope, mais ces releases SHM ne prouvent pas la lifetime GPU. Le runtime brut reste INCONCLUSIVE, IPC terminal1.

L’ombre pristine déborde sur21598 pixels H2 ; Mosaic n’en montre aucun sur H2. À l’intérieur H1, activer l’ombre ne change aucun RGB : ombre intérieure permise **NOT EXERCISED**, qualification complète **NOT PROVEN**. Les extents damage couvrent des différences stabilisées échantillonnées ; ni tous les frames, ni minimalité, ni absence exhaustive de stale pixels ne sont établis. Verdict architectural FX **PARTIALLY_FEASIBLE**, attribution du bord INCONCLUSIVE.

L’audit complémentaire LAB `parent/damage-envelopes.json` compare99 transitions de captures des treize runs initiaux
adjacentes entières : 18 différences contenues dans les enveloppes physiques A,
79 NOT OBSERVABLE et deux changements de dimensions NOT COMPARABLE. Les extents
sur un intervalle large ne prouvent pas la région pixman exacte/minimale ni un
buffer réellement présenté. Les autres runs n’héritent pas de la trace A.
