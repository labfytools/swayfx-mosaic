# STEP20C — décision d’intégration production, draft

> EXPERIMENTAL — édition du 2026-10-14, avant audit final et publication. Ticket `SWAYFX_MOSAIC_STEP20C_CORE_RECOVERY_OOM_AND_DCC_QUALIFICATION_BATCH_V1`. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED ; production multi-output NOT_YET_SUPPORTED ; PRODUCTION_AUTHORIZED=FALSE. Aucun contrat production, UX ou package adopté.

LAB désigne `/home/fy59/swayfx-mosaic-core-recovery-qmhckba5`, hors Git. Le [dossier V3](STEP20C_CORE_QUALIFICATION_DECISION_V3.md), la [fixture source-only](../../tooling/probes/step20c-core-recovery/README.md), ses [résultats compacts](../../tooling/probes/step20c-core-recovery/evidence/results.json) et sa [provenance](../../tooling/probes/step20c-core-recovery/provenance.json) fixent les identités, budgets et limites. Les chemins LAB sont des références locales ; les binaires, PNG et traces restent privés. Aucun résultat historique n’est réécrit.

## Recommandation unique

**PRIVATE_CORE_NEEDS_TARGETED_EVIDENCE.** La tranche est PARTIALLY_ADVANCED. Ce draft actualise les réponses du dossier de décision sur le CORE exact29baf31 ; les rapports source-only, A/G/C3 et minimal-core historiques restent immuables. Il ne sélectionne aucune politique OOM ou UX et n’autorise aucune intégration. Audit final/publication encore pendants à cette édition ; reçus réels hors Git après les étapes correspondantes.

## Matrice du CORE exact

| Question | État réellement établi | Gate restant |
| --- | --- | --- |
| Périmètre minimal | CORE privé existant, SceneFX0.5 statique, wlroots0.20.2 exact, hooks PI/C3/OPT retirés dans sa provenance propre | Aucun transfert de garanties d’autres SHAs |
| Standard pristine/CORE |12 RGB entières homologues exactes, overflow et input B/A/fermetures | Généralisation au-delà des captures NOT PROVEN |
| Horizontal Mosaic→splith | Deux chaînes/quatre grabs, H2 exacte en Mosaic, overflow standard/B-close/A-survie/final | Complete frame/damage et autres layouts NOT TESTED ici |
| Vertical | Traversée Y600 démontrée ; pristine H2 A6000/B19550 et CORE0 ; input ciblé | Champ brut crossing X/0 limité, matrices non mesurées NOT TESTED |
| Fullscreen non feuille | Ancêtre current10/fullscreen1 réel dans les deux contrôles | Popups wholly H1, arbres2/1 enfants et owners275/575 : NOT_EXERCISED / INCONCLUSIVE |
| Hidden owner | Même chaîne59/68 sans popup_done, H1 revenue exacte, input B visible | Dismissal destructif séparé non réexécuté ; politique UX UNDECIDED |
| Saved | HOLD39→timeout naturel→release/ACK/commit, normal-close et SHM3/3, H2 exacte | Saved node identity/retirement NOT_OBSERVABLE ; GPU lifetime NOT_PROVEN |
| OOM |40 commandes C attendues, six mutants rejetés, alternatives revues | A abort=P1 ; B/C natifs/session survival/damage NOT_PROVEN ; politique UNDECIDED |
| GPU DCC | Correction metadata par plan isolée et36 tests offline passent | effective halfpixel rejeté ; read_success NOT_PROVEN/GL queue UNOBSERVED ; G2 NOT_RUN |
| Rendu/input/present | Corrélations sampled applied/input/damage | Buffer identity/atomic generation/complete damage NOT_PROVEN |
| ABI/package | ELF exact/relocations/provider statique et Stage1 historique5 fichiers revérifiés | Maintenance future pair, full package, notices/legal/release/security ouverts |

Les [rapports V3](STEP20C_CORE_QUALIFICATION_DECISION_V3.md) et [résultats compacts](../../tooling/probes/step20c-core-recovery/evidence/results.json) séparent runner brut0, terminal IPC1, clients/compositeur0, scientific cleanup et mechanical cleanup PASS, et architecture brute INCONCLUSIVE. Neuf nouveaux runs,102 output PNG/120 slots réservés,9/11 cap, aucun retry/build/stage/install nouveau. Un succès de fixture n’est pas un contrat architectural.

## Disponibilité du clip obligatoire

L’abort actuel est **un motif P1 de blocage d’intégration** tant qu’une politique humaine n’est pas acceptée et qualifiée. Il refuse fail-open mais peut tuer tout le compositeur. Les harnais C rendent le risque reproductible, sans rendre sa disponibilité acceptable.

B propose retour bool et masque synchrone sous autorité owner, avec11 callers et garde fading audités ; il laisse volontairement le popup OOM désactivé, sans récupération automatique. C réserve64 octets pour tous les arbres avant publication, contre56 aux arbres effectivement clippés pour A/B, sans ajout de champ struct installé ; ses callers create/NULL et racines embarquées restent à qualifier. Préférer l’étude future de C pour enlever l’allocation à l’exposition est un avis technique, **pas son adoption**. Session survival, damage natif complet, saved/reparent/effects/GPU restent non prouvés.

## Contrat transactionnel obligatoire

Rendu appliqué et input doivent rester cohérents avec le même état de transaction. Les snapshots et fenêtres de callback ne suffisent pas à garantir une génération atomique jusqu’au buffer présenté. Aucun mécanisme particulier de compteur n’est imposé. Une tranche minimale d’intégration doit définir les mutations couvertes, leurs frontières pending/current/applied et la preuve native de leur cohérence ; les hooks historiques d’autres binaires ne dispensent pas ce travail sur le futur SHA candidat.

Les comptes historiques57/55/2,821/789/32 et414/400/14 restent séparés par LAB/run/output/commit_seq ; missing cause UNKNOWN. CORE_NATIVE_ORDERING=INCONCLUSIVE et le run optionnel est NOT_RUN faute de discriminant. Damage soumis et RGB stabilisées ne prouvent pas all-frame coverage ni GPU completion.

## Questions UX à soumettre

Offscreen hide/dismiss/reposition, input sous grab et comportement fullscreen restent UNDECIDED. S7 démontre un retour move-only sans dismissal ; il ne choisit pas une UX finale. S5/S6 ne permettent pas d’attribuer une divergence fullscreen à Mosaic ni de promettre la préservation d’un débordement non exercé. Un futur contrôle comparable doit précéder toute proposition de changement UX canonique. Aucun click-through universel, taille finale, animation ou binding n’est adopté.

## ABI statique, maintenance et distribution

Le CORE exact est ELF64 PIE, sans DT_NEEDED SceneFX/RPATH/RUNPATH ni relocations non résolues sur sa paire locale. Les mesures historiques43 bindings/40 symboles et node112/tree128 sont des observations locales, pas une promesse ABI ;85 overlaps ne sont ni85 bugs ni un certificat de sûreté. Un changement de wlroots/SceneFX doit refaire provider/layout/headers, callers et source ownership, build/C failure, clipping/input/fullscreen/saved/damage/lifetime sur le nouveau SHA. La responsabilité de maintenance embarquée appartient déjà au projet Mosaic selon le contrat privé accepté. Les responsables nommés de release et de sécurité restent à désigner ; aucun calendrier ni SLA nouveau n’est fixé. Aucun fork permanent ou ABI publique n’est accepté.

Le stage historique vérifié contient `/usr/bin/swayfx-mosaic`755 et quatre notices644, aucune autre entrée. Notices PARTIAL/LEGAL_NOT_APPROVED, distribution interdite sans revue juridique humaine et preuve package propre. Release/security owners restent à nommer ; aucun SLA inventé. PKGBUILD réel et patch cumulatif inchangés, aucun nouvel install/stage ni modification Packaging/Upstream/UX canonique.

## Rollback et prochaine décision

Aucun déploiement n’a lieu et aucun rollback réel n’est exécuté. Le chemin existant workspace-local `layout toggle mosaic` conserve le retour au layout standard ; le binaire distinct préserve la coexistence avec SwayFX ordinaire. Ce chemin ne constitue pas une récupération de session après abort et cette dernière demeure NOT TESTED. Un éventuel plan de livraison/retrait devra être soumis avec responsabilité release/security et notice juridique avant action système.

La prochaine plus petite étape est la revue exacte du dossier et des fixtures publiques, puis le choix d’un scope futur borné pour OOM natif, fullscreen comparable ou observabilité GPU/précision. Native coherence/lifetime, complete damage/effects, whole-field GPU, maintenance et legal sont des gates distincts ; aucune preuve positive n’en annule une autre. STEP20C NEXT ; production multi-output NOT_YET_SUPPORTED ; PRODUCTION_AUTHORIZED=FALSE.
