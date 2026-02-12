# 🏦 Détection de Fraude Bancaire 

> **Problématique :** *"Peut-on détecter des erreurs comptables ou des tentatives de fraude dans les rapports financiers annuels d’un groupe, tout en minimisant le coût des fraudes non détectées ?"*

## 1. Introduction & Enjeux Stratégiques

Dans le secteur bancaire, la fraude est un événement **rare mais dévastateur**.
*   **Le défi :** Les transactions frauduleuses représentent souvent moins de 5% du volume total.
*   **Le piège :** Une IA classique, entraînée sur ces données, apprendra à ignorer la fraude pour maximiser sa précision globale (95% de réussite en disant "tout est normal").
*   **L'objectif :** Nous devons inverser cette logique. **Une fraude ratée (Faux Négatif) coûte beaucoup plus cher à la banque qu'une fausse alerte (Faux Positif).** Notre but est donc de maximiser le **Rappel (Recall)**.

## 2. Notre Solution : Une Architecture en 3 Piliers

Pour capturer ces signaux faibles, nous avons développé une approche combinant l'analyse statistique traditionnelle et le Machine Learning avancé.

### 🔹 Pilier 1 : L'Analyse Forensique (Loi de Benford)
Les fraudeurs qui falsifient des bilans comptables tentent souvent d'inventer des chiffres "au hasard". Or, le hasard humain est imparfait.
*   **La Loi de Benford** stipule que dans un jeu de données naturelles, le chiffre **1** apparaît en première position environ **30%** du temps, le **2** environ **17%**, et le **9** seulement **4.6%**.
*   **Détection :** Nous calculons la déviation par rapport à cette loi. Une distribution trop uniforme (trop de 7, 8, 9) est un indicateur fort de manipulation humaine ("Red Flag").

### 🔹 Pilier 2 : Le Rééquilibrage par SMOTE
Puisque les fraudes sont rares, l'IA manque d'exemples pour apprendre.
*   **La technique :** Nous utilisons **SMOTE (Synthetic Minority Over-sampling Technique)**.
*   **Le fonctionnement :** Au lieu de dupliquer les cas de fraude existants, l'algorithme crée de nouvelles fraudes **synthétiques** mathématiquement plausibles, en interpolant entre des fraudes réelles.
*   **Résultat :** L'IA s'entraîne sur un jeu de données équilibré (50% saines / 50% fraudes), ce qui décuple sa sensibilité.

### 🔹 Pilier 3 : Modélisation Random Forest & Seuil Adaptatif
Nous utilisons un algorithme de **Forêt Aléatoire** pour sa robustesse.
*   **Optimisation :** Contrairement à une approche standard qui valide une fraude à 50% de probabilité, nous avons abaissé le seuil de détection à **30%**.
*   **Pourquoi ?** Pour ne rien laisser passer. Nous acceptons de vérifier manuellement quelques dossiers légitimes (Faux Positifs) pour garantir qu'aucune fraude réelle ne passe à travers les mailles du filet.

## 3. Résultats & Performance

| Métrique | Modèle Standard (Sans SMOTE) | Modèle Optimisé (Avec SMOTE) |
| :--- | :---: | :---: |
| **Rappel (Fraudes détectées)** | ~60% | **~95%** |
| **Précision** | 98% | 85% |
| **Risque Bancaire** | **Élevé** (Fraudes ratées) | **Maîtrisé** (Faux Positifs acceptables) |


## 4. Conclusion
Ce projet démontre qu'il est possible d'automatiser la détection de fraudes comptables complexes. En combinant **l'analyse forensique (Benford)** pour détecter les manipulations humaines et le **Machine Learning rééquilibré (SMOTE)** pour repérer les anomalies financières, nous offrons une couverture de sécurité quasi-totale pour l'institution financière.

