# SWAYFX_MOSAIC_STEP20C_COREC_V2_FULLSCREEN_OOM_GLES_NATIVE_CLOSURE_BATCH_V1

2026-10-15. Décision expérimentale V4, subordonnée aux contrats canoniques.
Résultat global : **PARTIALLY_ADVANCED**.
Recommandation : **PRIVATE_COREC_V2_NEEDS_TARGETED_EVIDENCE**.
Politique OOM production et disponibilité générale : **UNDECIDED**.

Le nouveau lot améliore migration/refocus et première/deuxième réservations
OOM dans des échantillons natifs revus. Le fullscreen comparatif reste non
exercé ; G3 s'arrête sur une fixture client avant acquisition. Il ne satisfait
donc pas la fermeture des gates d'intégration. Aucune readiness production
ne découle du progrès documentaire, offline, build ou échantillonné.

```text
STEP20A=DONE
STEP20B=EXPERIMENTAL
STEP20C=NEXT
STEP20D–G=PLANNED
PRODUCTION_MULTI_OUTPUT=NOT_YET_SUPPORTED
PRODUCTION_AUTHORIZED=FALSE
SWAYFX_MOSAIC_STEP20C_COREC_V2_FULLSCREEN_OOM_GLES_NATIVE_CLOSURE_BATCH_V1=PARTIALLY_ADVANCED
```

## 1. Deux tickets et deux provenances à conserver

La [décision V2 historique](STEP20C_COREC_V2_INTEGRATION_DECISION.md) clôt
12 runs et 102 captures dans `/var/tmp/swayfx-mosaic-corec-v2-i516p6po`.
Ce LAB reste en lecture seule ; P1/C7/C8/O1/G2, leurs erreurs et budgets ne
sont pas réécrits. Aucun octet ancien disparu n'est recréé par récit.
Le nouveau LAB est `/var/tmp/swayfx-mosaic-step20c-native-closure-qseaqp39` ;
artefacts lourds, captures, builds, sockets et logs restent hors Git.

L'ouverture de ce ticket utilisait `main` propre à
`d46f854b3026e911659528fe94792aa13837a1d6`. Le nouveau
[kit de suivi source-only](../../tooling/probes/step20c-corec-v2-followup/README.md)
est publié à `c55373eab3c53132bf1157acc9cfc9edd451156e` avant les cinq runs.
La [publication source](evidence/step20c-native-closure/source-publication.json)
est une preuve distincte d'une publication finale de résultats.
`origin` reste Forgejo canonique, `github` miroir, `upstream` fetch-only.
État au contrôle documentaire prépublication du 2026-10-15 : la publication
source c553 est vérifiée ; la publication des résultats suit l'audit final.
Sa preuve sera extérieure au commit qu'elle décrit :
`LAB/final-publication.json` et rapport final après vérification directe des
refs distantes. Ce document n'anticipe ni son propre SHA ni des refs finales.

Le [manifeste V2 exécuté](evidence/step20c-native-closure/source-manifest-v2.json)
porte le SHA256 `2e9fe75a48466fa1a9e3081137146d5cfffb35145c1749160e2c4f350bc6e5b7`,
digest `f21ea193aedfada620c251f0cf6a22375fb993483905129208864e22e535b140`.
La [reprise depuis clone](evidence/step20c-native-closure/clone-validation.json)
vérifie 49/49 fichiers et modes, 66 tests, six clients et reproduction source
G3. Les sources CORE/OOM/pristine ne sont pas reconstruites pour ces runs :
leurs ELF retenus sont requalifiés par identité. G3 est un nouvel ELF distinct.

## 2. Corrections prospectives et revues avant runs

Les fixtures dérivées apportent quatre corrections offline : groupe fullscreen
comparatif, calcul migration avec refocus natif, oracles root/nested adaptés
aux hiérarchies réellement créées et admission GLES/readback par capacités.
Les sources de production, UX, package et mécanismes CORE/OOM restent inchangés.
La revue initiale trouve trois findings ; la
[revue de delta](evidence/step20c-native-closure/source-delta-review.json)
accepte la version corrigée, 66 tests, sans effacer les refus initiaux.
Les validations C et mutations sont des preuves offline bornées ; elles ne
prouvent pas le moteur de scène natif complet.

La [revue B4](evidence/step20c-native-closure/gpu-b4-semantic.json) couvre le
vrai `g2_read` : 29 cas FakeGL, quatre mutants, 12 commandes source et les
tests d'admission. Elle manque le premier `draw()` sous le nouveau TMPDIR.
FS-P manque également l'enregistrement de l'errno original de son guard.
Ces lacunes sont conservées, et motivent une réparation **OFFLINE_ONLY**
post-campagne ; elles ne changent pas les octets c553 réellement exécutés.

## 3. Binaires, renderer et ABI exacts

| Rôle | SHA256 ELF | Build ID |
| --- | --- | --- |
| Pristine | `b7fa32116e3c42706b9b02da7df12f27e76d82dd253deb8bdec81519eed145f6` | `ba9751c82e73d4043b7651354f20936d070c2227` |
| CORE-C V2 | `91f48aae2675331e0a2c60ec2fedf983745c521c75232c704a6516a4140801fb` | `d5d304533f2c8db9d738365e9bd7f2c96779ef8d` |
| OOM V2 | `6067946bd79ad6fd8da7669ab9b0b3bacfd2638f5d3d8382002b9118db20d835` | `9bc3dc9055106b343c80a51ded111a382e98442d` |
| Diagnostic G3 | `9da90b178f20ea79bc9fb2a105c227f9d5d66a9de7eac77ff4ec3ea102908658` | `afdde13d52f3a5fe07c096c1221fcf0c8ae223fc` |

Les PID, `/proc/exe`, maps, SHA et Build IDs sont liés aux runs dans le
[résumé runtime](evidence/step20c-native-closure/runtime-summary.json).
Le renderer observé est GLES SceneFX sur AMD Radeon 780M/radeonsi ; son startup
ne prouve pas un readback diagnostic. Le fournisseur wlroots partagé exact
est `/usr/lib/libwlroots-0.20.so`, SHA256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
Les pins restent Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754`, SwayFX
`fd71a6bdc061bd633b488ae7b83e8a6981d22f86`, SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc`, wlroots source
`d783533489e1f75d6886c2ab5c5960090ef268f8`.

L'[audit ABI](evidence/step20c-native-closure/abi-baseline.json) et la
[revue build G3](evidence/step20c-native-closure/gpu-build-review.json)
qualifient uniquement la paire SceneFX statique/wlroots partagé exacte :
symboles privés, interpositions diagnostiques, structures et dépendances ELF.
Aucune ABI publique installée ni compatibilité avec une autre version n'est
adoptée. Le premier setup G3 échoue sur arguments fusionnés ; son FAIL reste
dans le ledger. Une continuation autorisée de la même paire corrige les flags,
puis build et stage passent : **une paire, un DESTDIR**, sans source CORE
modifiée. Le stage privé contient le binaire et quatre notices, cinq fichiers ;
aucune installation ni modification de PKGBUILD/patch production.
Licences **LEGAL_NOT_APPROVED**.

## 4. Matrice des huit IDs et budget clos

H1/H2 sont deux outputs headless privés, initialement `[-800,0,800,600]` et
`[0,0,800,600]`, scale 1, transform normal. DY-C change réellement la largeur
H1 puis migre le workspace. Les entrées ci-dessous utilisent les ELF du §3.

| ID | ELF / PID compositeur | Input et objet réellement exercés | Résultat | Captures / cap nommé | Durée ledger | Cleanup scientifique |
| --- | --- | --- | --- | --- | ---: | --- |
| FS-P | Pristine / 3491656 | Guard client ; avant groupe/fullscreen | NOT_EXERCISED | 0/12 | 6,097521916 s | PASS |
| FS-C | CORE / aucun | Dépendance FS-P non satisfaite | NOT_RUN | 0/16, non réservé | — | NOT_RUN |
| DY-C | CORE / 3492726 | Deux grabs ; quatre mutations et quatre points B wire/local | PARTIALLY_FEASIBLE | 16/16 | 35,995476057 s | PASS |
| OM-ROOT | OOM / 3494614 | Panne A, un grab, input voisin | PARTIALLY_FEASIBLE | 8/10 | 17,761603037 s | PASS |
| OM-NESTED | OOM / 3497491 | Panne B, deux grabs, input A puis voisin | PARTIALLY_FEASIBLE | 8/10 | 20,408873591 s | PASS |
| GPU-G3 | G3 / 3510983 | Client avant SHM ; aucun armement | INCONCLUSIVE ; objectif NOT_EXERCISED | 0/12 | 7,623459039 s | false / INCONCLUSIVE |
| OM-EXTRA | Aucun | Pas de discriminant distinct revu ; NOT_ADMITTED | NOT_RUN | 0/12, non réservé | — | NOT_RUN |
| GPU-CTRL | Aucun | Pas d'attribution indépendante admise ; pas de substitut G3 | NOT_RUN | 0/12, non réservé | — | NOT_RUN |

Le [ledger](evidence/step20c-native-closure/ledger.json) clôt **cinq réservations,
32 captures output**, sur plafonds huit runs/110 captures, 18 par run et
150 secondes par run. Les caps nommés totalisent 100. Aucun reset, refund,
retry ou transfert des jetons historiques ; aucun nouveau runtime autorisé.
Les actions brutes restent par ID dans le ledger : DY-C quatre mutations,
six clics/deux grabs ; OOM un hook par run ; G3 zéro hook, mutation et epoch.
Les runtimes et sockets sont privés avec IPC explicitement ciblé ; le LAB
lourd reste hors Git et conservé. Les écarts de workflow du §9 empêchent
d'affirmer une absence universelle d'écart de stockage.

## 5. Fullscreen et migration : conclusion circonscrite

Le [rapport fullscreen](STEP20C_COREC_V2_FULLSCREEN_COMPARATIVE_GATE.md)
enregistre `actual fullscreen client executable` avant groupe et fullscreen,
zéro capture. Le probe contrôlé reproduit EACCES sur `/proc/exe` avec
dumpable=0, mais l'errno FS-P original reste **NOT_OBSERVED** ; causalité
précise **NON_PROUVÉE**, aucun défaut fullscreen natif établi. FS-C reste
non réservé. La preuve P1 historique ne remplace pas la comparaison nouvelle.

Le [rapport migration/refocus](STEP20C_COREC_V2_MIGRATION_REFOCUS_GATE.md)
recalcule 800→800→1120→1120, largeur cellule 640, ordre `[8,9,10]`, focus 10.
Les snapshots courants restent `IPC_PENDING_CANDIDATE`, génération native
APPLIED non observable. Quatre points B redérivés, pixels et livraison réelle
wire/local corroborent les étapes. H2 entière est exacte quand la référence
s'applique ; le workspace sur H2 n'est pas exigé vide. H2 finale exacte,
aucun résidu A/B sur H1/H2 ; C7 historique reste INCONCLUSIVE.

## 6. OOM : absence de publication et disponibilité échantillonnée

Le [rapport OOM](STEP20C_COREC_V2_NATIVE_OOM_COMPLETION.md) lie panne unique,
PID/nonce/rôle, `matched=1 failures=1`, retour caller NULL et
`initialized=listeners=published=0`. Root : successes0, enfants parent0,
A jamais MAP, B non créé, fermeture A→TOPLEVEL normale error0.
Nested : root A réussi/mappé avant panne B, successes1/enfants parent1,
xdg root correspondant au parent B ; B jamais MAP. A demeure peint et reçoit
le bouton droit réel `[-215,108]` avant le clic voisin ; fermeture
B→A→TOPLEVEL normale error0. Aucun disconnect `no_memory` observé.

L'identité exacte, maps/wlroots, IPC tree/outputs et vraie livraison exclusive
au voisin sont archivés avant cleanup, sur le même PID. H2 entière pré/post/final
est exacte ; aucune couleur du rôle échoué sur H1/H2 et finales sans A/B.
Cette absence de fail-open est bornée aux injections observées. Disponibilité
générale, stale listeners universels et couverture OOM globale **NOT_PROVEN**.

| Option OOM | Arbitrage restant | Preuve de ce lot |
| --- | --- | --- |
| A abort | Mort fail-closed, disponibilité sacrifiée | Aucun nouveau recovery qualifié |
| B bool + masque | Recovery, setters et masque à qualifier | Pas de nouvelle preuve native |
| C préallocation | NULL avant publication ; coût pour toute factory | Root/nested PARTIALLY_FEASIBLE, disponibilité SAMPLED_ONLY |

Sidecar C : 64 octets par arbre, y compris inactif/non Mosaic, plus overhead
allocateur **NOT_MEASURED** ; lookup linéaire et coût global/performance
**NOT_MEASURED**. `OOM_PRODUCTION_POLICY=UNDECIDED`. Ce choix demande une
décision humaine ; aucun résultat n'adopte A, B ou C en production.

## 7. GLES/readback : objectif non exercé, défaut de fixture établi

Le [rapport G3](STEP20C_GLES_CONTEXT_READBACK_FOLLOWUP.md) conserve startup
EGL1.5, log création ES2.0, GL3.2 Mesa26.2.4 AMD780M ; aucune query native du
hook, uniforme, DCC, READ_SUCCESS, erreur/restauration ou A/B/A nouveaux.
Le client SHA `4e791780ac62152245891459864283750681b136a246c3c39ccf36b4f33972b4`
sort à 2 après configure/ACK avant SHM : `draw:92` exige le TMPDIR de l'ancien
LAB. Cette attribution combine source, environnement, wire et code brut ;
aucun errno/message client absent n'est inventé. Le runner atteint une attente
bornée. L'acquisition est vide, zéro capture/armement/epoch/raw.

La divergence historique EGL_CONTEXT_CLIENT_VERSION2 / GL_VERSION3.2 n'est
pas résolue par des logs startup. Precision mediump, plans auxiliaires DCC,
queue d'erreurs consommée/non restaurable et intrusion du readback restent
des limites de méthode, sans nouvelle mesure native ni ajustement de shader.
L'acceptation B4 est offline ; la préparation client n'avait pas couvert ce
TMPDIR. G2 historique et son premier-A refusé restent inchangés.

## 8. Input, générations, damage et cleanup : niveaux distincts

| Niveau | Statut du lot | Portée |
| --- | --- | --- |
| Sources/offline corrigées et publiées avant runs | CLOSED, périmètre des reçus | Aucune équivalence avec qualification runtime |
| DY-C, OM-ROOT, OM-NESTED | SAMPLED_ONLY / PARTIALLY_FEASIBLE | Pixels stables, vrais événements input et OOM ciblé |
| Fullscreen comparatif et diagnostic G3 | NOT_EXERCISED | FS-C NOT_RUN ; G3 run INCONCLUSIVE |
| Buffer natif, génération atomique, damage complet, GPU completion | NOT_PROVEN | Aucune promotion par captures ou ordre des logs |
| Autres cellules non exécutées | NOT TESTED | Aucun succès extrapolé |

Les corrélations nouvelles portent sur run/output/PID, serials, owner/workspace
IDs et nonce/xdg OOM. Aucun `commit_seq` ou identifiant natif de présentation
n'est instrumenté dans ces runs ; aucune identité de buffer soumis/présenté
ni génération universelle n'en découle. Saved buffers restent des preuves
historiques : aucun nouveau run saved dans ce lot.

Les quatre runs non GPU ont cleanup scientifique/mécanique PASS, tous processus
0. G3 conserve runner1, client référence PID3511049=2 sans CLOSE_RECEIVED ni
SHM_CLOSURE, compositeur3510983=0 et pointeur3511036=0 ; scientifique false,
mécanique PASS. Les cinq IPC terminaux sont à 1/EOF, séparés des compositeurs
0. Aucun rescue ni watchdog ; processus récoltés et runtimes privés supprimés.
Ces codes ne sont ni masqués ni assimilés les uns aux autres.

## 9. Réparations post-campagne, écarts et publication restante

Un delta post-campagne vise seulement la portabilité du client GPU et le
diagnostic FS-P : validation d'un scratch fourni, canonique, UID propriétaire,
mode0700 sans symlink ; errno FS explicite et arrêt fail-closed si identité
non observable. Le guard d'identité n'est pas assoupli ; aucune identité
`/proc` inaccessible n'est inventée. Cette correction reste **OFFLINE_ONLY**,
sans rebuild compositeur, retry ni requalification d'un run consommé.
Le [manifeste post-campagne final](evidence/step20c-native-closure/postcampaign-source-manifest-final.json)
compte 50 fichiers mode0644, SHA256
`1db849c1152bb29d512bf62e3db53cba18d0179c0008ca116887eb572d76a080`,
digest `14e24501658f1c4c29e7d8c06db71ed07a77b8e80e283453420bbc5b3e2f03c8`.
Le [gel GPU final](evidence/step20c-native-closure/postcampaign-gpu-manifest-final.json)
porte le SHA256 `a89926241a871bdc492348f922df1232962e622c4703720984ef681b5e6d98cb`.
Le [reçu de réparation](evidence/step20c-native-closure/postcampaign-repair.json)
et la [validation indépendante](evidence/step20c-native-closure/postcampaign-offline-validation.json),
SHA256 indépendant
`5905e2002041148d7a104e195132f56c8b4152952547be4ed0985da4eacc3852`,
enregistrent 73 tests réussis : 66 existants, trois d'identité et quatre du
vrai helper C validation/template, sans dessin Wayland.

Les gels intermédiaires f13da722…/230f131a… restent immuables. Seul
`gpu/README.md` change ensuite pour expliciter SMX_LAB et la commande des
quatre tests TMPDIR. La
[revue initiale](evidence/step20c-native-closure/postcampaign-delta-initial-review.json)
reste CORRECTION_REQUIRED ; la
[revue documentaire finale du delta](evidence/step20c-native-closure/postcampaign-delta-review.json),
SHA256 `4d459c0963c6535a404bfaa68d11dff0cf738e2d21167c148c12315e954ffe86`,
est ACCEPTED, sur égalité des octets code/tests déjà validés, sans rejeu des
73 tests dans cette revue. Le nouveau client SHA256
`bfc7d47596d5f69b68cd7000e257c7819949081ee7c6d66635eb9accf9ad7f36`
n'a jamais été exécuté en campagne native. Aucune preuve des runs c553 n'est
transférée à ce nouveau gel.

Les [écarts de workflow](evidence/step20c-native-closure/workflow-deviations.json)
doivent conserver les faits suivants : deux pyc temporaires créés dans le kit
puis retirés ; fichier temporaire de lecture documentaire déplacé vers LAB ;
logs de premières tentatives G3 écrasés par index, avec note préservée ;
premier environnement Git sans SSH, puis refus de configuration d'identité
sans HOME avant commit, enfin lecture de la configuration utilisateur sans
modification. Aucun « zéro écart de stockage » ou succès initial fictif.

Le [contrôle système de clôture](evidence/step20c-native-closure/system-audit.json)
vérifie 316 hashes protégés sans échec, 267 PID possédés absents et les cinq
runtimes `/tmp/smx-*` absents. La lecture seule du PID quotidien 2325,
`/usr/bin/sway`, startticks 2833, correspond à la baseline historique de clôture ;
ce n'est pas une nouvelle baseline pré-lancement ni une opération IPC.
Le LAB mesure alors 230680734 octets et le SSD dispose de 277259689984 octets
libres : mesures ponctuelles, susceptibles d'évoluer avec les reçus finaux.
Les 19612 entrées du manifeste historique initial et les reçus de clôture
restent vérifiés et inchangés. La
[requête coredump finale](evidence/step20c-native-closure/coredump-final.json)
depuis le bootstrap `2026-10-15 08:40:36 UTC` retourne 1, stderr
`No coredumps found`, dans le journal accessible à l'UID ; aucun nettoyage.
Le ledger reste SHA256
`cd79d42a97e630564ba5f3c119ee24db25f65799211ea30e440cf5b257e7705c` :
cinq runs, 32 captures, une paire G3 avec FAIL initial conservé/continuation
PASS et un stage de cinq fichiers.

La [revue finale approfondie](evidence/step20c-native-closure/final-review.json)
est **PASS**, SHA256
`3b15b5093730d6c43897e0adad4a1b2987fbc1097694a03645e928023ba23814`,
zéro constat bloquant, une remarque documentaire non bloquante NB-ENUM-1.
Cette remarque est corrigée dans le rapport GLES : marqueur `ACCEPTED`,
portée OFFLINE_ONLY séparée ; le reçu original reste inchangé. L'audit rejoue
69+4 tests réussis, rejette six contre-exemples bruts, vérifie 86 hashes
d'artefacts et les 316 hashes protégés. Une première assertion de son harnais
cherchait un mapping après fermeture ; elle est replacée avant
`CLOSE_RECEIVED`, avec l'erreur initiale conservée dans `raw-replay.json`.
Ce défaut d'oracle d'audit ne décrit pas un défaut de production.
Les contrôles finaux après audit sont consignés dans le
[reçu de validation finale](evidence/step20c-native-closure/final-validation.json).
La publication source pré-run vérifiée et la publication finale des résultats
restent distinctes. Cette dernière sera attestée par le reçu externe
`LAB/final-publication.json` et le rapport final, après push et vérification
directe des deux remotes, sans autoréférence au SHA de ce document.
Aucun changement production, installation, UX, PKGBUILD ou patch cumulatif
n'est autorisé par cette décision.

## 10. Revues et prochaines décisions

La [revue non GPU](evidence/step20c-native-closure/nongpu-results-review.json)
porte le SHA256 original
`a8a9ea6c9c1fab09687c1b43378d53d7add0eb421a9b2e626d60d59445578e86` ;
la [revue GPU](evidence/step20c-native-closure/gpu-results-review.json),
`78ce6fe03955d62d1b079b9a8e81161dcb5bfceef71bd2b71d13892bcf7e4d78`.
Elles acceptent les interprétations bornées des résultats, sans nouveau runtime.
Les contre-exemples pixels échoués et clamp hors bornes sont rejetés par les
validateurs ; aucune réussite du parser ne remplace les données natives absentes.

Responsables release, sécurité et maintenance SceneFX statique :
**UNASSIGNED**. Une mise à jour future doit revoir pins et delta, ABI/ELF,
requalifier la paire par offline/headless ciblés, contrôler le manifeste DESTDIR
et permettre le retour vers SwayFX stock ; ces obligations ne désignent aucun
responsable et n'autorisent aucune installation. Revue humaine des licences
et politique OOM restent ouvertes.

Le plus petit pas scientifique futur est d'établir une identité FS observable
sans relâcher dumpability ni le guard, avant toute nouvelle campagne
fullscreen ; une acquisition readback native demeure également nécessaire.
Ces campagnes exigent une instruction et un budget distincts, sans réouverture
des IDs clos. Les gates native buffer identity, atomic generation, complete
damage et GPU completion restent **NOT_PROVEN** ; la recommandation demeure
**PRIVATE_COREC_V2_NEEDS_TARGETED_EVIDENCE**.
