# STEP20C — gate ciblé scale et popups

> EXPERIMENTAL — édition du 2026-10-14, clôture documentaire des quatorze runs ciblés, diagnostic C3 inclus. Revue finale indépendante : ACCEPTED, audit PASS pour la fidélité de l’évidence expérimentale. Publication documentaire autorisée et préparée, non exécutée à cette édition. Le diagnostic C3 est exécuté : résultat INCONCLUSIVE, observations natives partielles sans transfert à A/G. STEP20A DONE ; STEP20B EXPERIMENTAL ; STEP20C NEXT ; STEP20D–G PLANNED. Multi-output de production : NOT YET SUPPORTED. Aucune intégration, installation ou décision UX.

L’autorité brute est le LAB privé `/home/fy59/swayfx-mosaic-targeted-7gge6h8b` ; HIST désigne `/home/fy59/swayfx-mosaic-overnight-mcolx0gq`. Les chemins LAB/HIST sont des artefacts externes locaux, pas des fichiers distribués. Le [rapport de clôture](STEP20C_TARGETED_CLOSURE_DECISION.md) donne les identités exactes, la matrice des quatorze runs et les limites. Les sources de [fixture ciblé](../../tooling/probes/step20c-targeted/README.md) restent des entrées expérimentales ; elles n’ajoutent aucune dépendance de production. Les rapports historiques et leurs verdicts restent inchangés.

## Contrat et preuves retenues

`scale-A` et `scale-G` mesurent séparément leur propre SHA ; neuf PNG par run, quatre observations de clic, deux vrais grabs. Le contrôle pristine de scale est historique : aucun nouveau run pristine scale n’est revendiqué. H1 est à origine négative, mode physique 1000×750, scale 1,25, transform normal et taille logique 800×600 ; H2 conserve la référence statique. Les cinq marqueurs de couleur sont validés dans le cadre PNG 1000×750, distinct du cadre logique IPC. La conversion n’est pas déduite de la seule taille du fichier.

La fixture vérifie d’abord le host traversant la frontière, puis crée les popups XDG. Les logs wire donnent `TOPLEVEL → POPUP_A → POPUP_B`, les serials de bouton réellement utilisés pour grab 35 puis 44, ACK 36 puis 45 et buffers clients 350×170 puis 300×130. L’origine appliquée client est (-318,25) ; A est (-218,105,350,170), B (-118,165,300,130) : les deux franchissent x=0. Les observations associent la fenêtre d’ouverture, l’owner natif, la hiérarchie wire, la géométrie et les pixels. Cette association reste bornée par le source audit ; aucun join natif direct host/owner ID n’a été instrumenté.

Le clic B visible est livré ; le point interdit ne livre aucun bouton B et déclenche le dismissal observé. H2 entier reste RGB exact à sa référence, y compris l’image finale. Mesures PASS, architecture FEASIBLE pour cet échantillon ; résultat runtime INCONCLUSIVE dans chaque run (IPC terminal exit1), processus exit0 et scientific cleanup PASS séparément. La politique de click-through sous grab reste indécise.

## Portée et limites

Une chaîne/deux grabs par run seulement ; allocation de retour standard désactivée : **NOT EXERCISED**. Les markers, captures, camera et root clip ne prouvent ni toutes les générations de transaction, ni tous les frames, ni les buffers GPU réellement présentés. Aucun nouveau statut de production ne suit de la réussite des mesures.

Sources de preuve LAB : `runs/scale-A/run/`, `runs/scale-G/run/`, `parent/run-summary.json`, `reviews/runtime-validation-13.{md,json}` (681 checks validés). Le budget scale est exactement deux runs/dix-huit captures. Les fichiers wire, images et hashes par run figurent dans le résumé lié ; la validation documentaire ne relance aucun compositeur.
