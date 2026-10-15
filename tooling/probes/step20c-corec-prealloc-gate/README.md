# STEP20C — reçus du gate CORE-C préallocation et précision GPU

EXPERIMENTAL — preuves documentaires seulement, édition du 2026-10-15 avant revue finale et publication. Ticket `SWAYFX_MOSAIC_STEP20C_OOM_PREALLOC_NATIVE_CORE_AND_GPU_PRECISION_BATCH_V1` **BLOCKED** ; recommandation et politique OOM **UNDECIDED**. Aucun launcher, source CORE-C, patch natif, binaire, capture ou autorisation runtime dans ce répertoire.

Le [dossier consolidé](../../../docs/design/STEP20C_COREC_PREALLOCATION_NATIVE_AND_GPU_PRECISION.md) interprète les reçus sans changer les rapports historiques. Les marqueurs de revue finale NOT_PROVEN et de publication BLOCKED sont un snapshot ; d’éventuels reçus ultérieurs doivent consigner les actions réellement accomplies séparément.

| Reçu | Contenu et limite |
| --- | --- |
| [git-initial.json](evidence/git-initial.json) | main initial propre et SHA identique aux deux remotes directs ; constat antérieur aux nouveaux fichiers |
| [gate-a.json](evidence/gate-a.json) | Trois reçus historiques absents, 0/979 entrées et 0/916 fichiers revérifiés ; suppression volontaire confirmée par l’utilisateur |
| [offline-commands.json](evidence/offline-commands.json) | Cinq argv `python -B`, rc bruts1, comptes et hashes des logs ; aucun lancement compositor/IPC/build/stage |
| [results.json](evidence/results.json) | Gate BLOCKED, tous les nouveaux tests C/natifs et runs NOT_RUN, budgets neufs non consommés, aucune identité CORE-C inventée |
| [safety.json](evidence/safety.json) | 314 fichiers production sans delta ; hashes protégés/système inchangés, zéro IPC live/processus graphique du ticket ; pas de preuve de continuité PID sans snapshot initial |
| [relocation.json](evidence/relocation.json) | Déplacement du petit LAB de reçus hors home vers `/tmp`, sans réécrire les anciens argv |
| [khronos-primary-sources.json](evidence/khronos-primary-sources.json) | URLs primaires mobiles et hashes/tailles des quatre XML récupérés ; aucune preuve d’application au shader G1 absent |

LAB actuel : `/tmp/swayfx-mosaic-corec-prealloc-hm3xzpzi`. Ancien chemin conservé dans les reçus : `/home/fy59/swayfx-mosaic-corec-prealloc-hm3xzpzi`. Les logs privés sont dans `LAB/tests/` et les XML dans `LAB/inputs/`. Aucune conservation durable de `/tmp` n’est garantie. Aucun nouveau LAB ne reste dans home ; les anciens LAB supprimés ne sont pas reconstruits.

Les suites existantes échouent dans l’état actuel : graphics15 réussites/5 erreurs sur20 par inputs historiques absents ; GPU synthétique4 réussites mais setUpClass EDQUOT/errno122 ; replay G1 zéro test et erreur setUpClass par inputs absents ; native3 réussites/1 FAIL/1 erreur sur5 (log absent et agrégation vide0/0/0 au lieu de821/789/32) ; auditor traceback rc1 sans résultat créé. Les codes bruts des cinq commandes sont tous1. Les succès partiels ne valident ni CORE-C, ni un readback GPU. Aucun nouveau test exact-body C/native/sanitizer n’a été exécuté et aucun test existant n’a été corrigé ou relancé pour ce dossier.

Les preuves sont liées à leur édition. Un README, un résumé publié ou un hash attendu ne remplace pas les octets exacts manquants. La suite minimale est une instruction séparément cadrée modifiant/redéfinissant le gate de provenance, ou la restauration des inputs autoritatifs exacts si une sauvegarde existe. Aucun budget disponible ne vaut admission runtime. STEP20C reste NEXT, production multi-output NOT_YET_SUPPORTED et PRODUCTION_AUTHORIZED=FALSE.
