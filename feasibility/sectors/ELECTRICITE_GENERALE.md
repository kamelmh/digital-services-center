# Pack Sectoriel — Électricité Générale + Almasse Inventory

## Sector Pack — Quincaillerie Électrique avec Système Almasse (El Bayadh)

---

**Version:** 1.0
**Date:** 30/08/2026
**Région:** El Bayadh (32) et environs — wilaya ~300 000 hab., `market_index = 0.65` (32-El Bayadh)
**Secteur:** Commerce de détail — électricité générale, appareillage, luminaires — avec gestion informatisée Almasse
**Référence:** DSC-SECT-ELEC-2026-001

---

## 1. RÉSUMÉ EXÉCUTIF

### 1.1 Positionnement

Commerce de détail **électricité générale** vitrine rue — la quincaillerie-électricité moderne avec **moat logiciel**. L'offre physique (câbles, disjoncteurs, prises, LED, goulottes) est différenciée par le système **Almasse** : gestion SKU par code-barres, alertes stock bas, POS (point de vente) avec facture, inventaire périodique et traçabilité des lots. Positionnement : *le seul électricien-commerçant d'El Bayadh où le stock est temps réel*.

| Élément | Valeur |
|---------|--------|
| Concept | Storefront 50–80 m² + réserve + système Almasse (POS + inventaire) |
| Ticket moyen | 2 500–12 000 DZD (détail) ; 25 000–120 000 DZD (chantier) |
| Marge brute cible | 18–30 % (mix pondéré ~24 %) — commerce, non service |
| Investissement standard | ~2,75 M DZD (cf. §5) ; léger ~2,2 M / haut ~3,4 M |
| Emplois | 2–3 (gérant polyvalent + vendeur-conseil + magasinier/caissier) |
| Seuil de rentabilité | ~460–580 K DZD/mois de CA selon mix marge (cf. §8.4) |
| Horizon | VAN calculée à `12 %` (`policy_constants.VAN_DISCOUNT_RATE`) sur 5 ans ; TRI 8–14 % |

### 1.2 Pourquoi Almasse fait la différence

Sans logiciel : ruptures invisibles, écarts inventaire 5–8 %, réassort à l'instinct, facturation manuelle. Avec Almasse : SKU + code-barres dès réception, alerte seuil, historique par fournisseur, inventaire tournant mensuel, ticket POS avec TVA 19 % (`policy_constants.TVA_STANDARD_RATE`) ventilée, et reporting rotation — le gérant arbitre prix/stock au lieu de subir.

> Hypothèses chiffrées hors taxe ; TVA 19 % collectée/déductible neutre sur marge si assujetti au réel. IBS commerce/services 26 % (`policy_constants.IBS_SERVICES_COMMERCE_RATE`) au-delà du seuil IFU.

---

## 2. MARCHÉ LOCAL (EL BAYADH)

### 2.1 Données de cadrage

| Indicateur | Valeur | Source / Note |
|------------|--------|---------------|
| Population wilaya | ~300 000 (chef-lieu ~85 000) | ONS / RGPH extrapolé 2024 |
| `market_index` 32-El Bayadh | **0.65** | Référentiel interne DSC — coef. correcteur vs. moyenne nationale |
| Croissance construction | **8–12 %/an** (logements, AADL, rural) | DLEP El Bayadh, permis de construire |
| Transition solaire/LED | Forte — remplacement halogène → LED, chauffe-eau + kits solaires | Observation terrain 2025–2026 |
| Saisonnalité | Pic printemps-été (chantiers) ; creux hiver (janv.–fév.) | — |
| Panier chantier type | 40 000–90 000 DZD (câble + tableau + prises + LED) | Relevés quincailleries |

### 2.2 Concurrence locale

| Type | Nombre estimé (El Bayadh ville) | Prix / Marge constatée | Faiblesses |
|------|----------------------------------|------------------------|------------|
| Quincailleries avec rayon élec | **8–12** | Marge 15–25 % | Stock peu profond, pas de conseil technique, pas de facture |
| Magasins purs électricité | **2–3** | Marge 20–35 % sur LED/disjoncteurs | Peu de visibilité, pas de POS, ruptures fréquentes |
| Grossistes Oran/Saïda (appro.) | 4–5 fournisseurs habituels | — | Délai 48–72 h, franco à partir de 150 K DZD |
| Informel / marchés | diffus | -10 % mais sans garantie | Contrefaçon appareillage |

**Pouvoir de prix :** élevé sur LED, disjoncteurs différentiels, tableaux étanches, goulottes — où le conseil + disponibilité immédiate justifient +8–12 %. Faible sur câble au mètre (prix affiché partout).

### 2.3 Facteurs de demande

Lotissements neufs + auto-construction, rénovation parc ancien, mise aux normes, éclairage public/privé LED, et demande diffuse des électriciens installateurs (prescripteurs — 15–20 actifs identifiés).

---

## 3. PRODUITS & GRILLE TARIFAIRE

### 3.1 Familles de produits

| # | Famille | Exemples SKU | Prix vente constaté (DZD) | Marge brute | Rotation |
|---|---------|--------------|---------------------------|-------------|----------|
| 1 | **Câbles & fils** (ml) | 1,5 mm², 2,5 mm², RO2V 3G, terre | 35–85 /ml (1,5–2,5 mm²) ; 180–320 /ml (RO2V) | 12–18 % | Très haute |
| 2 | **Disjoncteurs & tableaux** | Disjoncteur 10–32A, diff. 30 mA, tableau 8–24 modules | 650–1 800 (disj.) ; 2 500–9 000 (tableau équipé) | 22–30 % | Moyenne |
| 3 | **Interrupteurs & prises** | Gammes encastrées, étanches, prises RJ45/TV | 180–650 /pièce ; 450–1 200 (étanche) | 25–35 % | Haute |
| 4 | **Luminaires LED** | Spots, réglettes, projecteurs 20–100W, hublots | 800–3 500 (spot/réglette) ; 3 500–9 000 (projecteur) | 28–35 % | Haute |
| 5 | **Appareillage & outillage** | Boîtes, dominos, colliers, testeurs, pinces | 15–1 500 | 20–30 % | Haute |
| 6 | **Goulottes & accessoires** | Goulottes 20×12 à 40×25, tubes IRL, fixations | 120–650 /2 ml ; 80–250 (tube) | 18–25 % | Moyenne |

> Prix TTC relevés El Bayadh / Saïda juin–août 2026 ; TVA 19 % incluse en vitrine (`policy_constants.TVA_STANDARD_RATE`). Achats HT récupérable si réel.

### 3.2 Mix de revenus type

| Famille | % du CA | % de la marge totale | Note |
|---------|---------|----------------------|------|
| Câbles | 28 % | 18 % | Volume, faible marge, appelle le reste |
| Disjoncteurs/tableaux | 20 % | 23 % | Prescription électricien |
| Interrupteurs/prises | 18 % | 22 % | Impulsion + chantier |
| Luminaires LED | 19 % | 24 % | Meilleure marge, showroom |
| Goulottes/accessoires | 10 % | 8 % | Complément |
| Appareillage | 5 % | 5 % | — |

---

## 4. FLUX OPÉRATIONNEL

### 4.1 Processus standard (avec Almasse)

```
accueil → écoute besoin / devis → vérif stock Almasse (SKU / code-barres)
    ↓
picking réserve → contrôle → caisse POS Almasse → facture (TVA 19 % si assujetti)
    ↓
livraison / retrait → encaissement (espèces / TPE / virement chantier)
    ↓
Almasse : décrément stock → alerte seuil → proposition réassort → commande fournisseur
    ↓
inventaire tournant mensuel → écart → ajustement → reporting rotation
```

### 4.2 Rôles

| Rôle | Effectif | Missions | Compétence clé |
|------|----------|----------|----------------|
| **Gérant polyvalent** | 1 | Achats, prix, relation électriciens/chantiers, clôture Almasse | Habilitation élec. souhaitée, gestion |
| **Vendeur-conseil technique** | 1 | Accueil, devis, conseil norme, relance devis | Lecture schéma, NIF/C 15-100 notions |
| **Magasinier / caissier** | 1 (mi-temps possible au démarrage) | Réception, étiquetage code-barres, picking, POS, inventaire | Rigueur stock |

Almasse : 1 licence POS + 1 douchette + imprimante ticket ; inventaire avec terminal ou smartphone.

### 4.3 Temps de cycle

| Opération | Durée | Goulot |
|-----------|-------|--------|
| Vente comptoir | 5–10 min | File caisse si 1 seul POS |
| Devis chantier (20–40 lignes) | 30–60 min | Vérif stock + prix fournisseur |
| Réception + étiquetage | 45 min / 30 SKU | — |
| Inventaire tournant (1 famille) | 2 h / mois | Fermeture partielle rayon |

---

## 5. INVESTISSEMENT & ÉQUIPEMENTS

### 5.1 Investissement initial (standard = ~2,75 M DZD)

| Poste | Détail | Montant (DZD) |
|-------|--------|---------------|
| Rayon & étalages | Gondoles, vitrines, présentoirs LED, éclairage showroom | **400 000** |
| Stock initial | 1 200 K DZD d'achats HT (assortiment 350–450 SKU) | **1 200 000** |
| Caisse POS + Almasse | POS tactile, tiroir-caisse, douchette, imprimante ticket, licence Almasse 12 mois | **150 000** |
| Outillage & étalonnage | Testeurs, échelles, petit outillage, étalonnage | **200 000** |
| Aménagement local | Électricité, peinture, enseigne, réserve | **300 000** |
| Fonds de roulement | Trésorerie 2–3 mois (loyer, salaires, réassort) | **500 000** |
| **Total standard** |  | **2 750 000** |

| Scénario | Total investissement | Note |
|----------|---------------------|------|
| Léger (local existant, stock réduit) | ~2 200 000 | 250 SKU, 1 POS |
| **Standard** | **~2 750 000** | 400 SKU, cf. ci-dessus |
| Haut (showroom LED + 2e caisse) | ~3 400 000 | 550 SKU, 2 POS |

> Stock compté HT ; TVA 19 % sur achats récupérable si réel (`policy_constants.TVA_STANDARD_RATE`). Hors pas-de-porte.

### 5.2 Équipements type — devis comparatifs indicatifs

| Équipement | Fournisseur A (Oran) | Fournisseur B (Alger) | Fournisseur C (Saïda) |
|------------|---------------------|----------------------|----------------------|
| Gondole 1,2 m | 28 000 | 31 000 | 26 000 |
| POS tactile + tiroir | 85 000 | 92 000 | 78 000 |
| Douchette + imprimante ticket | 32 000 | 35 000 | 29 000 |
| Licence Almasse 12 mois | 45 000 | 45 000 | 45 000 |

---

## 6. PLAN RH — ORGANISATION 2–3 PERSONNES

### 6.1 Organigramme

```
Gérant polyvalent (propriétaire-exploitant)
    ├── Vendeur-conseil technique
    └── Magasinier / Caissier (Almasse)
```

### 6.2 Salaires & charges — base SNMG 24 000 DZD (`policy_constants.SNMG_MONTHLY`)

| Poste | Salaire brut | Primes | Brut chargé employeur* | Net indicatif |
|-------|-------------|--------|------------------------|---------------|
| Gérant (exploitant) | — | — | CASNOS 15 % (`policy_constants.CASNOS_RATE`, min 3 000 DZD/mois `CASNOS_MIN_MONTHLY`) | — |
| Vendeur-conseil | 30 000–35 000 | 3 000–5 000 | +25,5 % CNAS employeur (`policy_constants.CNAS_EMPLOYER_RATE`) | ~28 000–34 000 |
| Magasinier/caissier | 24 000–28 000 | 2 000–3 000 | +25,5 % CNAS employeur | ~22 000–27 000 |

*Coût complet employeur = brut × 25,5 % ; total prélèvement CNAS 34,5 % = 25,5 % employeur + 9 % salarié (`policy_constants.CNAS_COMBINED_PAYROLL_RATE`). Masse salariale 2 pers. : ~75–95 K DZD/mois chargée.

### 6.3 Charges mensuelles type (hors COGS)

| Poste | Bas | Moyen | Haut |
|-------|-----|-------|------|
| Loyer (60–80 m² centre) | 18 000 | 22 000 | 28 000 |
| Salaires chargés (2 pers.) | 75 000 | 85 000 | 95 000 |
| Électricité / Internet / TPE | 8 000 | 11 000 | 14 000 |
| Comptable + assurances | 7 000 | 10 000 | 13 000 |
| Marketing (Facebook + bouche-à-oreille) | 4 000 | 7 000 | 10 000 |
| Divers / transport appro. | 6 000 | 9 000 | 12 000 |
| **Total** | **118 000** | **144 000** | **172 000** |

---

## 7. CADRE LÉGAL

### 7.1 Activités & codes

| Activité | Code CNRC | Autorisation |
|----------|-----------|--------------|
| Commerce de détail d'appareillage électrique | **607-003** (électricité générale) | Registre de commerce |
| Quincaillerie générale (si mix) | 607-002 | Idem — à adjoindre si outillage |
| Vente au détail divers (accessoires) | 607-xxx complément | — |

### 7.2 Spécificités & conformité

| Élément | Exigence | Délai / Note |
|---------|----------|--------------|
| NIF / NIS / AI | Inscription impôts, CASNOS | À l'immatriculation |
| Habilitation électricien | Souhaitée pour conseil ; obligatoire si prestation pose | Attestation CFPA / APAVE-like |
| IANOR / normes | Produits conformes CE / IANOR ; tableaux norme C 15-100 vulgarisée | Exiger certificats fournisseur |
| Sécurité local | Extincteur, disjoncteur diff. 30 mA, assurance RC + multirisque | Vérif. APC |
| Facturation | Facture avec TVA 19 % si réel ; ticket POS Almasse horodaté | `policy_constants.TVA_STANDARD_RATE` |
| Décret 26-154 (NESDA) | Éligibilité si <40 ans / chômeur / primo-entrepreneur — prêt 70 % bancaire à 0 % (`policy_constants.NESDA_INTEREST_RATE`), grâce 1,5 an, 7 ans | Guichet NESDA — dossier CNRC + local |

### 7.3 Régime fiscal recommandé

| Situation (CA annuel HT) | Régime | Justification |
|---------------------------|--------|---------------|
| < 6 M DZD | **IFU** 12 % services / 5 % production (`policy_constants.IFU_SERVICES_RATE` / `IFU_PRODUCTION_RATE`) — si éligible | Simplicité, pas de TVA |
| 6–10 M DZD | Réel simplifié | Récup. TVA 19 %, charges déductibles |
| > 10 M DZD ou chantiers facturés | **Réel normal**, IBS 26 % (`policy_constants.IBS_SERVICES_COMMERCE_RATE`), TVA 19 % | Crédit TVA, factures chantiers |

> CNAS 34,5 % au total (`policy_constants.CNAS_COMBINED_PAYROLL_RATE`), SNMG 24 000 DZD plancher (`policy_constants.SNMG_MONTHLY`), VAN actualisée à 12 % (`policy_constants.VAN_DISCOUNT_RATE`).

---

## 8. MODÈLE FINANCIER TYPE (3 SCÉNARIOS)

### 8.1 Hypothèses communes

| Paramètre | Valeur |
|-----------|--------|
| Investissement retenu | **2,75 M DZD** (standard) — cf. §5.1 |
| Marge brute | Prudent **18 %** / Base **24 %** / Ambitieux **30 %** |
| Formule CA indicative | `CA = Invest × (1 + marge) × market_index (0,65)` → borne basse théorique ; rotation réelle 2,5–3,5× du stock porte le CA effectif à 3,2–5,5 M (retenu ci-dessous) |
| Charges fixes annuelles | ~1,73 M DZD (144 K/mois moyen ×12) |
| Fiscalité | IFU→Réel selon seuil ; IBS 26 % (`policy_constants.IBS_SERVICES_COMMERCE_RATE`) si bénéficiaire au réel ; TVA 19 % neutre |
| Actualisation | **12 %** (`policy_constants.VAN_DISCOUNT_RATE`) sur 5 ans |
| Stock | 1,2 M HT, rotation 2,7–3,8×/an selon scénario |

### 8.2 Scénarios de revenus (HT, hors TVA 19 %)

| Scénario | Marge | CA annuel HT | COGS | Marge brute | Charges fixes | EBITDA* |
|----------|-------|-------------|------|-------------|---------------|---------|
| **Prudent** | 18 % | **3 200 000** | 2 712 000 | 488 000 | 1 730 000 | **-1 242 000** |
| **Base** | 24 % | **4 200 000** | 3 387 000 | 813 000 | 1 730 000 | **-917 000** (seuil proche) |
| **Ambitieux** | 30 % | **5 500 000** | 4 231 000 | 1 269 000 | 1 730 000 | **-461 000** → +230 K après effet volume/achats** |

*EBITDA avant amort. (amort. ~180 K/an sur 400 K étalages+POS sur 3–5 ans). **Ambitieux corrigé : remise fournisseur -3 % à 5,5 M + 0,5 rotation → EBITDA ~+230 K.

> Lecture : à 24 % de marge, le seuil comptable est à ~7,2 M de CA si charges pleines 2 pers. — d'où l'importance du scénario ambitieux ou du démarrage à 1,5 ETP (magasinier mi-temps) qui abaisse le seuil à ~5,2 M.

### 8.3 Seuil de rentabilité

| Indicateur | Valeur (base 24 %) | Valeur (ambitieux 30 %) |
|------------|--------------------|-----------------------|
| Charges fixes mensuelles | 144 000 DZD | 144 000 DZD (ou 118 000 à 1,5 ETP) |
| Marge sur coûts variables | 24 % | 30 % |
| **Seuil CA mensuel** | **600 000 DZD** | **480 000 DZD** (393 000 à 1,5 ETP) |
| Seuil annuel | ~7,2 M DZD | ~5,76 M (4,72 M à 1,5 ETP) |
| Date de rentabilité | Mois 18–24 si montée à 5,5 M | Mois 10–14 |

### 8.4 VAN, TRI, délai de récupération (5 ans, 12 %)

| Scénario | Cash-flow annuel moyen (après IBS) | **VAN @12 %** (`policy_constants.VAN_DISCOUNT_RATE`) | **TRI** | Payback | ROI 3 ans |
|----------|-------------------------------------|------------------------------------------------------|---------|---------|-----------|
| Prudent (3,2 M) | -1,1 M | **-5,9 M** | <0 % | — | négatif |
| Base (4,2 M, 2 ETP) | -0,75 M | **-4,6 M** | <0 % | — | négatif |
| Base allégée (4,2 M, 1,5 ETP) | -0,35 M | **-3,1 M** | ~2 % | >48 mois | ~-30 % |
| **Ambitieux (5,5 M, 30 %, 1,5 ETP + remises)** | **+0,35 M** | **-0,75 M** | **~8 %** | **42–48 mois** | **~15 %** |
| Ambitieux haut (6,5 M, 30 %) | +0,85 M | **+0,95 M** | **~18 %** | **28–34 mois** | **~65 %** |

**Interprétation sans fard :** à `market_index 0,65` et marge commerce 24 %, un 2,75 M investi à El Bayadh n'est rentable qu'en **rotation élevée + mix LED/disjoncteurs à 30 % + démarrage léger (1,5 ETP)**. La VAN 12 % ne devient positive qu'au-delà de ~6 M de CA/an — soit 5× le stock. C'est atteignable (un chantier AADL = 80–120 K) mais exige prospection électriciens. Ne pas présenter 2,4 M de CA comme viable — ce serait faux.

*Méthode : flux = EBITDA - amort. + amort. - IBS (26 % `policy_constants.IBS_SERVICES_COMMERCE_RATE` si >0) - investissement an 0 ; VAN = Σ flux/(1,12)^t.*

### 8.5 Sensibilité

| Variable | -20 % | Base | +20 % | Impact |
|----------|-------|------|-------|--------|
| CA | VAN -1,4 M | -0,75 M | +0,15 M | **Très élevé** |
| Marge (24→30 %) | seuil +1,5 M | 5,76 M | 4,8 M | Élevé |
| Loyer | +0,18 M VAN | — | -0,18 M | Faible |
| Masse salariale | +0,45 M VAN si -20 % | — | -0,45 M | Élevé |

---

## 9. RISQUES SPÉCIFIQUES

### 9.1 Matrice des risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| **Rupture fournisseur** (câble, disjoncteur star) | Moyenne | Élevé | Double sourcing Oran/Saïda + stock tampon 15 j sur top-20 SKU (Almasse alerte seuil) |
| **Impayés chantiers** (électriciens / promoteurs) | Moyenne | Élevé | Plafond encours 80 K par client, 50 % à la commande, relance Almasse, pas de livraison sans BL signé |
| **Concurrence prix** (quincaillerie casse prix câble) | Élevée | Moyen | Ne pas suivre sur câble ; marge sur LED/tableaux + service devis rapide |
| **Obsolescence LED / normes** | Faible | Moyen | Rotation courte LED (60 j), pas de surstock >90 j, veille fournisseur |
| **Vol / freinte / écart stock** | Moyenne | Moyen | Almasse code-barres + inventaire mensuel + réserve fermée + caméra 1 500 DZD/mois |

### 9.2 Indicateurs d'alerte (Almasse)

| Indicateur | Seuil d'alerte | Action |
|------------|----------------|--------|
| CA mensuel | < 380 000 DZD (1,5 ETP) / < 480 000 (2 ETP) | Prospection électriciens, promo LED |
| Marge brute | < 22 % | Revoir mix (pousser LED/disjoncteurs), renégocier achats |
| Rotation stock | < 2,5×/an | Déstocker, réduire profondeur câbles |
| Écart inventaire | > 1,5 % | Audit réception/caisse, contrôle accès réserve |
| Créances >45 j | > 250 000 DZD | Blocage encours, recouvrement |

---

## 10. PLAN D'ACTION 30/60/90 JOURS

### Jours 1–30 : Installation (J0–J30 — RC + stock + Almasse setup)

| Semaine | Actions |
|---------|---------|
| S1 | CNRC 607-003, NIF/NIS, CASNOS, bail 60–80 m², assurance ; ouvrir compte bancaire |
| S2 | Commander étalages + stock initial 1,2 M (350 SKU) — 2 devis Oran/Saïda ; commander POS + licence Almasse |
| S3 | Aménagement, étiquetage code-barres Almasse, paramétrage TVA 19 % (`policy_constants.TVA_STANDARD_RATE`), seuils alerte, import fournisseurs |
| S4 | Recrutement vendeur-conseil, formation Almasse (réception → POS → inventaire), test encaissement |

### Jours 31–60 : Ouverture (J30–J60 — bouche-à-oreille + Facebook)

| Semaine | Actions |
|---------|---------|
| S5–S6 | Ouverture soft (électriciens prescripteurs invités), flyers chantiers, page Facebook « Électricité Générale El Bayadh » — photos showroom LED |
| S7–S8 | Rodage flux `devis → vérif Almasse → picking → facture` ; premier inventaire tournant (famille câbles) ; ajuster prix LED/disjoncteurs |

### Jours 61–90 : Fidélisation (J60–J90 — chantiers + réassort optimisé)

| Semaine | Actions |
|---------|---------|
| S9–S10 | Tournée électriciens (15–20) : remise chantier 3–5 % + encours plafonné ; convention 2 promoteurs locaux |
| S11–S12 | Analyse Almasse : top-20 / dead stock, renégocier 3 fournisseurs, caler réassort auto, clôture mensuelle marge/rotation/écart |

---

### 10.4 Contacts sectoriels (références à compléter terrain)

#### Fournisseurs recommandés

| Catégorie | Fournisseur | Contact |
|-----------|-------------|---------|
| Câbles / fil | Sidi Bel Abbès Câbles (Oran dép.) | 0XX.XX.XX.XX |
| Appareillage / disjoncteurs | Legrand / Schneider grossiste Alger-Oran | 0XX.XX.XX.XX |
| LED / luminaires | Import LED Oran (El Kerma) | 0XX.XX.XX.XX |
| Goulottes / tubes | Plastique industriel Saïda | 0XX.XX.XX.XX |
| POS / Almasse | Almasse support + installateur local | 0XX.XX.XX.XX |

#### Partenaires

| Type | Partenariat |
|------|-------------|
| Comptable | Réel simplifié, TVA 19 %, IBS 26 % (`policy_constants.IBS_SERVICES_COMMERCE_RATE`) |
| Électriciens installateurs | Prescription contre disponibilité + devis <1 h |
| Banque / NESDA | Dossier Décret 26-154 si éligible — 70 % bancaire à 0 % |
| Transporteur Oran–El Bayadh | Franco 150 K, 48 h |

---

### 10.5 Checklist lancement — avant l'ouverture

| Étape | Statut | Date |
|-------|--------|------|
| Immatriculation CNRC 607-003 | ☐ | |
| NIF / NIS / CASNOS | ☐ | |
| Bail local 60–80 m² + assurance | ☐ | |
| Compte bancaire + TPE | ☐ | |
| Étalages / showroom LED posés | ☐ | |
| Stock initial 1,2 M réceptionné & étiqueté Almasse | ☐ | |
| POS + douchette + imprimante + licence Almasse | ☐ | |
| Paramétrage TVA 19 % (`policy_constants.TVA_STANDARD_RATE`) + seuils alerte | ☐ | |
| Personnel recruté (1–2) + contrats CNAS 25,5 % employeur | ☐ | |
| Grille tarifaire affichée (6 familles) | ☐ | |
| Page Facebook + flyers chantiers | ☐ | |
| Inventaire zéro + procédure mensuelle | ☐ | |

---

**Pack Sectoriel — Électricité Générale + Almasse Inventory**
**Digital Services Center — El Bayadh (32), Algeria — market_index 0.65**
**MAHI Kamel Abdelghani — kamelmahi71@gmail.com — +213 676 77 38 92**
*Rates : TVA 19 % (`policy_constants.TVA_STANDARD_RATE`), VAN 12 % (`policy_constants.VAN_DISCOUNT_RATE`), SNMG 24 000 DZD (`policy_constants.SNMG_MONTHLY`), CNAS 25,5 % employeur / 34,5 % combiné (`policy_constants.CNAS_EMPLOYER_RATE` / `CNAS_COMBINED_PAYROLL_RATE`), CASNOS 15 % (`policy_constants.CASNOS_RATE`), IBS 26 % commerce/services (`policy_constants.IBS_SERVICES_COMMERCE_RATE`), IFU 12 % services / 5 % production (`policy_constants.IFU_SERVICES_RATE`), NESDA 0 % 7 ans dont 1,5 an grâce (`policy_constants.NESDA_INTEREST_RATE`).*
