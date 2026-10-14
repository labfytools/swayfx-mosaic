# STEP20C — options de politique OOM pour clip obligatoire

> EXPERIMENTAL — édition du 2026-10-14, avant audit final et publication. Ticket `SWAYFX_MOSAIC_STEP20C_CORE_RECOVERY_OOM_AND_DCC_QUALIFICATION_BATCH_V1`. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT_YET_SUPPORTED ; PRODUCTION_AUTHORIZED=FALSE. Aucun contrat production, UX ou package adopté.

LAB désigne `/home/fy59/swayfx-mosaic-core-recovery-qmhckba5`, hors Git. Le [dossier V3](STEP20C_CORE_QUALIFICATION_DECISION_V3.md), la [fixture source-only](../../tooling/probes/step20c-core-recovery/README.md), ses [résultats compacts](../../tooling/probes/step20c-core-recovery/evidence/results.json) et sa [provenance](../../tooling/probes/step20c-core-recovery/provenance.json) fixent les identités, budgets et limites. Les chemins LAB sont des références locales ; les binaires, PNG et traces restent privés. Aucun résultat historique n’est réécrit.

## Résultat et portée

**CORE_OOM_C_TESTS=PARTIALLY_FEASIBLE ; CORE_OOM_ALTERNATIVES_REVIEW=ACCEPTED ; CORE_PRODUCTION_OOM_POLICY=UNDECIDED.** L’acceptation porte sur une étude C privée limitée, pas sur la disponibilité d’une session réelle. A reste OOM_ABORT_EXPERIMENTAL et PRODUCTION_AVAILABILITY_NOT_APPROVED. L’abort est un blocage P1 pour intégration, sans modifier le CORE29baf31.

La [fixture OOM](../../tooling/probes/step20c-core-recovery/oom/README.md) conserve les patches privés A/B/C, extraction, bindings et harnais. Le [reçu indépendant ultérieur](../../tooling/probes/step20c-core-recovery/evidence/oom-initial-accepted.json) accepte la portée limitée ; les mentions NOT_PROVEN de handoff/README antérieurs reflètent leur date de pré-revue. Ils ne sont pas réécrits pour simuler une approbation production.

## Comparaison A/B/C

| Option | Échec d’allocation | Disponibilité / ownership | Coût / ABI privée | Preuve restante |
| --- | --- | --- | --- | --- |
| A, arrêt | abort sur allocation sidecar ciblée | Fail-closed par mort du processus ; session perdue |56 octets par arbre clippé ; setter parent inchangé | Récupération session NOT TESTED |
| B, bool + masque | Setter désactive synchroniquement l’arbre et retourne false | Owner décide admission ; popup OOM reste masqué, aucune récupération automatique |56 octets par arbre clippé ; déclaration privée void→bool,11 callers audités | Damage complet et admission native NOT PROVEN |
| C, préallocation | Réserve sidecar avant publication ; libère arbre si réservation échoue | Create retourne NULL avant init/listener ; setter n’alloue plus |64 octets sur chaque arbre créé ; aucun champ struct installé ajouté, signature conservée | Tous callers create et survie session NOT PROVEN |

A utilise les vrais corps parent byte-identiques ; six injections premières/deuxièmes allocations donnent-6/SIGABRT en normal/UBSan/ASan, sans core dump (`RLIMIT_CORE=0`). Le fait de refuser un clip absent ne constitue pas une politique production acceptée de perte du compositeur.

B audite11 appels setter dans transaction.c : deux tiling et neuf popup. Chaque échec est traité. Le setter ne réactive pas l’arbre ; le propriétaire garde l’autorité d’activation. Le risque de réactivation fading-out est protégé par `probe_clip_enable_tiling(ws, desired)`, dont le vrai corps et la statement fading exacte sont compilés. NULL standard peut être admis ensuite par la demande upstream ; un clip vide reste valide et sans hit. Un popup OOM demeure désactivé même après succès/retour standard : recovery reste un contrat futur, pas un choix UX implicite.

Le vrai enabled extrait transmet l’ancienne région visible au callback réduit avant disabled/update. Cette transmission est testée, mais les supports scene_node_visibility/update ne sont pas le moteur SceneFX complet. Ni visibility/damage réel, ni pixels périmés, ni effets/animation/present n’en sont prouvés.

C réserve après allocation arbre et avant scene_tree_init : échec de la seconde allocation n’expose ni parent/listener ni arbre partiellement publié. Le setter active/réutilise la réservation, NULL la rend inactive, zéro reste actif et destroy la libère. Les walkers/get ignorent les réservations inactives. Les arbres externes/embarqués ne sont pas couverts ; le root embarqué ne passe pas par create et ne peut être donné à ce setter C. Aucun appel Mosaic actuel ne clippe ce root, mais la généralisation n’est pas acquise.

Les tailles56/64 viennent de la déclaration sidecar exacte compilée avec vrai wlr_box et wl_listener, pas des structs réduits du harnais. C ajoute une allocation et retient64 octets sur tous les arbres jusqu’au destroy, plus un overhead allocateur non mesuré ; A/B allouent seulement aux arbres clippés. Aucun sizeof struct publique futur ni ABI installée n’est changé ou garanti par ces mesures.

## Validation C et revue

Les40 commandes attendues comprennent neuf builds normal/UBSan/ASan,27 exécutions defined/injections1/2, deux builds et deux exécutions mémoire. B/C sortent0 ; A produit les six abort attendus. Wayland listes/listeners/signaux et régions Pixman sont natifs ; le compositeur complet et les bibliothèques ne sont pas compilés sous sanitizer ici.

Six mutants sont tous rejetés : admission ignorée, abort retiré, false sans masque, réactivation setter, publication avant réservation, clip actif supprimé. Codes bruts `-6,99,-6,-6,-6,-6`. Les assertions des mutants restent distinctes des abort A attendus. Une première extraction fading trop large échouait à compiler ; `LAB/oom/attempt-4/` conserve les erreurs, corrigées par resserrement du marqueur à la statement exacte. Aucun échec transitoire de setup n’est caché.

La revue indépendante reproduit40/40 et6/6 dans un nouveau répertoire privé. Le manifeste fixture est `4a6dfda4f61d9c9f5a13588fe7ed7ac6ec6d9720cf2167a82e5f7c39f52d0c35`, sources `59207af208d13c43d0bb0aa3a1669dae697d22d20ba1199ece12817d754d9c1c`, slices `6c7092197a5055136356f1fad113f213b37dfea189c024eaebd437d2819c592e`. Les25 bindings exacts et neuf sources prototypes complètes sont vérifiés. Les scènes natives saved/GPU ne sont pas exercées par ces tests.

## Recommandation technique et décision humaine

C mérite l’étude native future pour éviter une allocation à l’exposition, sous réserve de son coût sur tous les arbres et des obligations create/NULL. B reste une alternative si admission/recovery est qualifiable. Ce conseil n’adopte ni C ni B, et ne tranche pas disponibilité contre fail-closed. **La politique production reste UNDECIDED.**

Un futur scope unique devra tester les allocations réelles, session survival, old/new damage, hide/return/fullscreen, popups nested/grabs, saved timeout, reparent/destroy, animations, retour standard, input/applied transaction/present, pixels périmés/FX et shutdown. Les harnais ne prouvent ni complete native damage, ni native reparent/saved, ni lifetime GPU. Aucune intégration, aucun build compositeur ni run OOM natif n’est autorisé par ce rapport.
