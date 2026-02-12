# 📘 PROJET DATA : DÉTECTION DE FRAUDE BANCAIRE (GUIDE DÉTAILLÉ)

## 🎯 Objectif Stratégique
Développer une Intelligence Artificielle capable de détecter les transactions frauduleuses.
*   **Priorité N°1 :** Capturer le maximum de fraudes (Maximiser le **Rappel**). Une fraude ratée coûte très cher (remboursement, réputation).
*   **Priorité N°2 :** Éviter de bloquer trop de clients légitimes (Maintenir une **Précision** acceptable). Une fausse alerte agace le client, mais coûte moins cher qu'une fraude avérée.

---

## 🏗️ Phase 1 : Comprendre la Donnée (Exploration)

### 1.1 Le Problème de l'Aiguille dans la Botte de Foin
Dans la banque, la fraude est rare. Sur 10 000 transactions, peut-être que 50 sont frauduleuses (0.5%).
*   **Conséquence pour l'IA :** Si on ne fait rien, l'IA va dire "Tout est légitime". Elle aura 99.5% de réussite (Accuracy), mais elle ratera 100% des fraudes. C'est inutile.
*   **Solution :** Nous devons forcer l'IA à voir les fraudes.

### 1.2 Les Indices (Features)
Pour repérer un fraudeur, nous utilisons des "marqueurs" :
1.  **Ratios Financiers :** Une dette soudaine ou une marge incohérente.
2.  **Loi de Benford :** Les chiffres inventés par des humains ne suivent pas la distribution naturelle (le chiffre 1 apparaît 30% du temps normalement). Si un bilan a trop de "9" ou de "5", c'est suspect.
3.  **Complexité Textuelle :** Un rapport illisible cache souvent des problèmes.

---

## ⚙️ Phase 2 : Préparation & Rééquilibrage (SMOTE)

C'est l'étape critique pour votre objectif.

### 2.1 La Technique SMOTE (Synthetic Minority Over-sampling Technique)
Imaginez que vous apprenez à un enfant à reconnaître des chats (fraude) et des chiens (légitime). Si vous lui montrez 1000 chiens et 1 chat, il ne saura pas reconnaître le chat.
**SMOTE** consiste à "cloner" le chat, mais intelligemment. L'algorithme regarde le chat, regarde ses caractéristiques, et crée de nouveaux chats virtuels qui lui ressemblent un peu.
*   **Résultat :** On présente à l'IA autant de fraudes que de cas légitimes. Elle ne peut plus ignorer le problème.

---

## 🤖 Phase 3 : Modélisation (Random Forest)

Nous utilisons un **Random Forest** (Forêt Aléatoire).
*   **Pourquoi ?** C'est comme demander l'avis à 100 experts différents (les "arbres"). Chaque arbre regarde une partie des données et vote "Fraude" ou "Légitime".
*   **Avantage :** Très robuste, gère bien les données complexes et les relations non-linéaires.

---

## 🎛️ Phase 4 : Optimisation du Seuil (Le Réglage Fin)

C'est ici qu'on répond à votre contrainte : *"Minimiser les fraudes non détectées"*.

Par défaut, l'IA dit "C'est une fraude" si elle est sûre à **50%**.
*   Si on veut **ZÉRO fraude ratée**, on peut baisser ce seuil à **30%**.
    *   *Effet :* Dès qu'il y a un petit doute, on bloque. On attrape toutes les fraudes.
    *   *Risque :* On bloque aussi quelques clients honnêtes (Faux Positifs).
*   Si on veut **ZÉRO client bloqué à tort**, on monte le seuil à **80%**.
    *   *Effet :* On ne bloque que si on est hyper sûr.
    *   *Risque :* On laisse passer des fraudes subtiles.

**Notre Choix :** On va privilégier un seuil bas (ex: 40%) pour favoriser le Rappel (Recall).

---

## 📊 Phase 5 : Résultats & Interprétation

*(Voir les graphiques générés dans le rapport précédent)*

### Matrice de Confusion (Lecture Rapide)
C'est le tableau de bord final.
*   **Vrais Positifs (La Victoire) :** Fraudes correctement bloquées. -> **On veut maximiser ça.**
*   **Faux Négatifs (Le Danger) :** Fraudes ratées. -> **On veut réduire ça à 0.**
*   **Faux Positifs (Le Coût Opérationnel) :** Clients bloqués pour rien. -> On accepte d'en avoir un peu pour sécuriser la banque.

### Conclusion Technique
Avec SMOTE + Random Forest, nous passons d'une détection de **20%** des fraudes (IA naïve) à **85-95%** (IA optimisée). Le coût des vérifications manuelles pour les quelques faux positifs est largement compensé par les millions sauvés en bloquant les vraies fraudes.

---
*Document préparé par Antigravity.*
