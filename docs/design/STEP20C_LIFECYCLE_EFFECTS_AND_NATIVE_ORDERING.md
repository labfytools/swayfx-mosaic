# STEP20C — lifecycle, effets et ordre natif

> EXPERIMENTAL — édition documentaire du 2026-10-14, après revue finale ACCEPTED / audit PASS du dossier expérimental ; publication préparée, non exécutée à cette édition. Les résultats concernent des laboratoires privés ; aucune intégration production, installation ou décision UX. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED. Multi-output de production : NOT YET SUPPORTED. Les anciens rapports restent historiques et leurs résultats ne se transfèrent pas à un nouveau SHA.

L’autorité brute est le LAB privé `/home/fy59/swayfx-mosaic-overnight-mcolx0gq`. Les chemins LAB ci-dessous sont des références locales de preuve, pas des fichiers distribués. Les sources de fixture préservées se trouvent dans [tooling/probes/step20c-overnight](../../tooling/probes/step20c-overnight/qualification/README.md). La [provenance compacte](../../tooling/probes/step20c-overnight/qualification/provenance.json) lie les identités et reçus sans publier logs, images, binaires, archives ou patches candidats.

## E1 — owner caché et retour

Même chaîne TOPLEVEL→A→B, mêmes identités et grabs ; hide donne clip root vide et pixels A/B nuls, puis le retour conserve la hiérarchie sans recreation et restaure l’entrée B réelle. Les fenêtres hide/return sont rejouées, H2 RGB exact. Une motion sans enter pendant hide est observée ; elle ne prouve pas tous les hits possibles. Mesures PASS, runtime INCONCLUSIVE, cleanup PASS. Aucun UX hide/dismiss/reposition final ni click-through universel décidé.

## E2 — saved buffers non exercés

Configure29 puis30 ACKés et `hold_next_configure` armé sont réels ; aucun configure ultérieur ni HELD, deux PNG de référence seulement. Source A `sway/commands/gaps.c` : `gaps inner 30` avec argc2 appelle `gaps_set_defaults`, modifie la config sans arranger le workspace courant ; la branche runtime demande quatre arguments. Le succès IPC n’est pas un configure mesuré. Saved-node identity/render, timeout effectif et lifetime : NOT EXERCISED / NOT PROVEN ; runtime INCONCLUSIVE. Aucun timeout artificiellement prolongé ni rerun.

L’audit source décrit `view_save_buffer` : arbre saved frère de content_tree, destination/source/transform copiés, buffer courant locké via SceneFX set_buffer ; suppression détruit l’arbre et réactive le contenu. Cela reste SOURCE AUDIT ONLY sur A, pas une observation runtime des identités saved/locks/releases. Les anciens SB/BI/ASI/HIT instruments et résultats appartiennent à d’autres binaires et ne sont pas incorporés ici.

## E3 — effets et cache : résultat partiel

Deux tentatives,16 PNG chacune. A/B modifie226908 pixels pristine et182214 Mosaic. Whole-H1 A/A-return reste différent de33883 pixels pristine (bbox402,25–798,598) et32132 Mosaic (bbox482,25–800,598). Le critère de restauration entière échoue réellement dans les deux contrôles ; aucune causalité propre à Mosaic n’est établie. La ROI centrale64×64 change ses4096 pixels A→B puis retrouve exactement A ; quatre ROI adjacentes retrouvent A. Fraîcheur RGB échantillonnée positive, restauration full/cache/damage complet NON démontrée.

Native Mosaic observe régénération naturelle réussie et optimized=1 USE d’un buffer non nul. Sept états H2 Mosaic restent identiques à la référence. Shadow-on ne change aucun pixel H1, mais déborde sur21598 pixels H2 pristine (bbox0,0–36,600) ; H2 Mosaic reste exact. Les captures classic-floating off/on sont entièrement égales, ROI268,268–332,332 et métrique adjacente0→0 : filtration classic NOT EXERCISED. Classic tiled Mosaic NOT TESTED et optimized tiled spill standard non exercé par ce glass intérieur.

Les deux runs s’arrêtent avant effects-evidence et fermeture normale/final capture ; glass/background code1/error32 après teardown. Cleanup scientifique FAIL malgré tous les PID reapés et runtime supprimé sans rescue. Ne pas transformer l’absence de résidu en fermeture normale réussie. Verdict PARTIAL_RGB_FRESHNESS_WHOLE_RESTORATION_FAIL_INCONCLUSIVE.

## F — état appliqué, entrée et ordre natif

Pristine : trois clics/commits region réels, owner ne reçoit pas de bouton lorsque region vide, restauration mesurée ;8 PNG, verdict INCONCLUSIVE et aucune PI privée native dans ce contrôle non modifié.

Mosaic : input full→empty→full observé, trois clics,4 PNG, deux livraisons owner autour de l’état vide. Assertion échoue parce qu’elle conserve l’origine initiale(-318,25) pour le clic(-314,30), attend(4,5), alors que l’origine appliquée après restauration est(-638,25), cohérente avec motion wire(324,5) et bouton45/46. Aucun défaut de routing n’en découle ; focus/resize/layout/close suivants NOT EXERCISED. Runtime INCONCLUSIVE, cleanup PASS.

Les12 premiers couples output/commit_seq natifs analysés sur57 commits bruts ont10 PAIRED et2 MISSING_PRESENT : seq2 H1 et H2. Les45 autres commits restent dans le brut sans être transformés en preuve de pairing. Un event headless present `presented=1` ne démontre pas les pixels du buffer ni une présentation physique. Il serait incorrect de dire12/12 presents ou lifetime qualifié.

Source wlroots : incrément commit_seq et signal commit synchrone, present headless différé idle, idle annulé au destroy. Source instrumentation : PI_SCENE/OWNER/POPUP échantillonne la scène appliquée dans le callback output commit, PI_POPUP sans owner-ID natif. Les flux séparés ne forment pas une génération atomique.

| Contrat demandé | État réel |
| --- | --- |
| Géométrie/clip/input observés dans les fenêtres documentées | Échantillonnés, cohérents pour les mesures citées |
| Mutation naturelle commit→input change→present discriminante | NOT EXERCISED |
| Epoch/génération atomique transactions/scène/hit/present | NOT PROVEN |
| Buffer exact présenté et identité native hit | NOT PROVEN |
| Locks/références/releases GPU, saved, teardown exhaustifs | NOT PROVEN |
| Damage complet de toutes frames et stale pixels intermédiaires | NOT PROVEN |
| Damage minimal | NOT PROVEN |

TEMPORAL_DAMAGE donne temps monotoniques/extents, distincts des captures. Des extents échantillonnés ne prouvent ni toutes frames ni tous pixels ; pas de nouvelle conclusion d’atomicité ou damage-to-present. Aucun GPU readback ajouté à A/G.

## G et neutralité de l’instrumentation

Le patch privé `release-shape/release-removal.patch` (`6e8a5b50149732ac70ecd79ab8db9258956f59036aba1bf17a477866bc44a5c1`) retire26 statements de log dans7 fichiers et les helpers démontrés orphelins de trace ; hashes parents/résultats et bindings de revue vérifiés. Les patches fonctionnels clip/owner guard restent. PI listeners et ordre FBO bind avant le chemin d’échec restent : cet ordre peut avoir un effet non passif et sa neutralité n’est pas prouvée. « Sans instrumentation » serait faux.

G a un build/stage et un smoke horizontal propres, SMOKE_FEASIBLE ; aucune qualification complète de son lifecycle/effets ni équivalence générale trace-off/on héritée. Un nouveau SHA nécessitera contrôles et matrice appropriés.

## Validation et limites de provenance

Revue lifecycle/G :32 checks hors ligne sur vrais logs/PNG plus négatifs parent/grab/root/owner/input stale/present/RGB ; archive exécutée v2 exacte578 entrées. Revue premiers D :14 négatifs ; C :7 mutations de preuves ; R90 v3 :9 négatifs. Les échecs initiaux d’extraction/analyse et corrections hors ligne sont conservés, sans réexécution graphique. Les preuves sont `reviews/matrix-lifecycle-runtime-review.{md,json}`, `matrix-lifecycle-analysis.json` et `parent/native-source-audit.json` dans le LAB.

Tous les runtimes matrix ont terminal IPC1 conservé ; le chemin individuel de runtime matrix n’a pas été journalisé. `runtime_removed=true`, tous PID absents et audit parent de résidus sont observés ; suppression de chaque ancien chemin nommé n’est pas indépendamment revérifiable. La clôture parent vérifie absence de PID/socket privés. Le hash SceneFX système initial n’a pas été enregistré ; hash final seul et ctime antérieure ne doivent pas être décrits comme une comparaison initial/final. Aucun usage IPC de session desktop ni installation système.

## Revue finale observée et publication préparée

Revue indépendante finale ACCEPTED / audit PASS pour la fidélité du dossier expérimental : 0 BLOCKING, 4 NON_BLOCKING, 3 FUTURE_SCOPE ; 180 checks hors ligne et 15 mutations de preuves réelles rejetées. Rapport privé `reviews/overnight-final-review.md`, SHA256 `bb4000dffb51b07b59e86f91e8dd76bc2c4f0b9513b48a52c9f6bd6c8c3f45af` ; reçu JSON SHA256 `72ba252092ca3375d344faae1c2026c8d5626fd190e87771d5c0c1ad8212c9b0`. Index scientifique post-exécution `seals/index.json`, SHA256 `cdf034e1f8466a9ae8a0e0a33aa8d0d0195273f0d1bc782667b50c3bcf682505`, contexte de preuve courant, pas un binding pré-exécution.

NB-01 est complété dans l’index compact depuis les grabs wire réels de chacun des huit runs concernés, avec lignes et hashes sources dans `parent/metadata-serial-completion.json`. Les stops fixtures, échecs E3 et incident IPC restent documentés. Les gates lifetime/génération/damage, couverture G, maintenance ABI/paquet/juridique et robustesse/coût des sidecars privés restent ouverts. L’acceptation documentaire ne qualifie pas la production et n’applique aucune décision. Publication préparée, pas encore exécutée à cette édition ; les refs/SHAs finaux et le résultat de publication feront foi dans le reçu privé et le handoff final.
