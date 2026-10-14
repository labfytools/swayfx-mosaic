# STEP20C — causalité GPU, FBO et cache

> EXPERIMENTAL — édition du 2026-10-14. Ticket `SWAYFX_MOSAIC_STEP20C_SAVED_LIFETIME_INPUT_EPOCH_AND_GPU_CAUSALITY_BATCH_V1`. Revue finale indépendante du dossier complet : ACCEPTED / audit PASS pour la fidélité expérimentale ; publication PREPARED à cette édition, reçu final hors Git après push. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT YET SUPPORTED. Aucun contrat UX, package ou production adopté.

LAB désigne `/home/fy59/swayfx-mosaic-saved-input-gpu-pz4z428f`, laboratoire privé hors Git. Les chemins LAB sont des références locales, pas un kit distribué. Le [dossier V2](STEP20C_GATE_CLOSURE_DECISION_V2.md) fixe la provenance commune et les limites. Les rapports historiques restent immuables.

## Identité et acquisition bornée

Le binaire diagnostic nouveau est SHA256 `2d1d221ea34461e538e5b5c6bd811bc865089ac133a6e48578998347c58b97dd`, Build ID `41a24e90859655314196efaa3d34659330000af0`. Le gel GPU accepté est `49baa41f0afe78b13de8d8272039081fcd9551d814d4241786720517f68bded3` (118 liaisons). Patch privé C SHA `b92268faf3780a3b7f57ec916cea44e57f11b768e08155c02243dba2230a0743`. Revue `LAB/reviews/gpu-delta-review.*` ACCEPTED après correction de la gate d’arrêt d’epoch ; six tests revalident 21 anciens et 30 nouveaux faults.

Un run, trois epochs d’acquisition A/B/A, douze points par epoch, trois ROI 16×16 par point : 108 lectures, 27 648 pixels RGBA, 110 592 octets. Tuples fx/wlr/fbo/rbo/tex concordants dans chaque pass, contexte EGL commun, bindings GL/PACK restaurés. Les epochs sont locales aux acquisitions ; les pointeurs ne sont pas des identités persistantes entre epochs. La queue `glGetError` est UNOBSERVED et n’a pas été vidée. Lecture, logging et fsync perturbent le timing ; absence de fences, GPU completion et identité exacte du buffer présenté NOT PROVEN.

## Discrimination locale conservée

Main-before-blur et down-0 sont A/A-return exacts dans les ROI. Down-1 diverge uniquement dans la queue hors domaine frais : ce n’est pas une divergence fraîche. Le candidat prospectif down-1 (199,75) demeure exact, ainsi que ses vingt texels source, destination (94,101,114,255). C’est une preuve négative, jamais remplacée par sélection opportuniste.

La première divergence fraîche observée est down-2. Onze supports complets contiennent six points centraux inchangés et cinq pixels frais divergents. Tous les texels frais source requis restent exacts ; leur contribution différentielle est zéro. Les texels hors domaine frais apportent idéalement jusqu’à (−6,5 ; −5,75 ; −0,375 ; 0), avec résidu différentiel maximum 0,5 U8 sur ces onze supports. Ceci étaye localement la dépendance au contenu préexistant de pong hors 200×150 dans sa texture physique 800×600. Up-1 ajoute une contribution hors domaine ; à up-2, le contenu hors domaine vient de down-0 du même rebuild : « hors domaine » ne signifie pas universellement « frame précédente ».

Up-0, résultat et cache sont exactement égaux en RGBA sur les 768 pixels par epoch. Les 27 648 alpha natifs valent 255. Les 2 304 RGB presubmit satisfont exactement `round((68,32,16) + (119/255) * cache_RGB)`. Le coefficient 136/255 est l’alpha du verre historique, pas le coefficient transmis au fond. Cette formule opaque locale ne qualifie pas tous les cas d’alpha/strength.

## Causalité entière et modèle

Whole-H1 A/A-return reste FAIL : 34 323 pixels différents, minimum RGB (−6,−6,−1), maximum (0,0,0), delta absolu max6. Les trois images entières GPU sont RGB exactes aux trois G historiques homologues ; cela ne transfère ni événements FBO vers G ni neutralité temporelle universelle. Pristine historique reste 37 252 pixels différents ; les seize images homologues A/G historiques restent exactes.

Le modèle froid historique produit un signe positif/max33 : ses noyaux/copies/arrondis monotones et état initial nul imposent un retour non négatif. Le natif montre des queues préchauffées plus sombres. Le modèle froid ne reconstitue donc pas l’histoire native. Aucune initialisation ajustée, seuil, sampler, précision ou shader n’a été modifié. Mediump/quantification/coordonnées effectives ne sont pas mesurés ; les résidus absolus au modèle idéal, jusqu’à 11,5 dès down-0, sont conservés. Aucune borne universelle d’arrondi ±1 n’est inventée.

Le rapport scientifique `LAB/audit/gpu-xhigh/FINAL_FINDINGS.md` SHA `b58994389cd5f0e4ef3c0431d81683aa51b0f820c198e361d6ecbc31773bc768` et `XHIGH_SUMMARY.json` SHA `e9da85989cf3433824738940cc403213d1db6dba778c85152a248b37090e55ad` portent l’interprétation PARTIALLY_SUPPORTED_LOCAL_FBO_HISTORY. Le reçu validateur conserve CACHE_A_RETURN_CAUSALITY=INCONCLUSIVE pour la causalité entière. WHOLE_FIELD_NATIVE_CAUSALITY=INCONCLUSIVE ; HISTORICAL_A_G_PRISTINE_NATIVE_CAUSALITY=NOT_PROVEN. Les zones non lues et frames intermédiaires restent inconnues.

## Provenance bind-before-failed corrigée

L’ordre `fx_pass_submit` bind-before-failed existe déjà dans SceneFX pristine `37ccd723bef49e6891156ffafce8f549f01446cc`. Le fichier pristine/base/core est identique, SHA `398d594ace7257f4b69319290be7c1f14dc1ded446545ceb337404f5caab0cd3`. L’affirmation du draft antérieur d’un ordre différent de pristine est réfutée. Les anciens rapports restent historiques ; cette correction ne démontre aucune neutralité ni failure semantics complète.

measurements_pass=PARTIALLY_FEASIBLE ; runner0, IPC terminal1, runtime global INCONCLUSIVE ; quatre clients code0/error0, scientific_cleanup et mechanical cleanup PASS. architecture_verdict=PARTIALLY_FEASIBLE. Aucun shader/cache fix, contrôle pristine supplémentaire ou nouveau run n’est justifié dans ce ticket ; le prochain discriminant nécessiterait champ FBO entier/précision native exacte avec nouveau scope explicite.
