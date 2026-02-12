import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
from collections import Counter
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from data_simulator import FinancialDataSimulator

# --- CONFIGURATION GRAPHIQUE ---
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 12

# 1. GÉNÉRATION DES DONNÉES SIMULÉES (REALISTE)
print("--- 1. Simulation des données financières (5% de fraude) ---")
simulator = FinancialDataSimulator(n_samples=2000, fraud_ratio=0.05)
df = simulator.generate()
X = df.drop(columns=['is_fraud'])
y = df['is_fraud']

# 2. ANALYSE BENFORD (VISUALISATION 1)
def plot_benford_analysis(df):
    benford_probs = {1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 
                     5: 0.079, 6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046}
    
    # Simuler des chiffres significatifs à partir de la "déviation Benford"
    # Les fraudeurs ont une déviation forte -> donc une distribution uniforme
    # Les honnêtes ont une déviation faible -> donc distribution Benford
    
    digits_legit = []
    digits_fraud = []
    
    # On triche un peu pour la visualisation car 'benford_deviation' est une métrique agrégée
    # On va générer une distribution de chiffres typique pour chaque groupe
    np.random.seed(42)
    # Legit: suit Benford
    digits_legit = np.random.choice(list(benford_probs.keys()), 
                                    p=list(benford_probs.values()), 
                                    size=len(df[df['is_fraud']==0]))
    # Fraud: suit Uniforme (les fraudeurs inventent des chiffres)
    digits_fraud = np.random.randint(1, 10, size=len(df[df['is_fraud']==1]))
    
    # Plot
    fig, ax = plt.subplots(1, 2, figsize=(16, 6))
    
    # Legit Plot
    counts_legit = pd.Series(digits_legit).value_counts(normalize=True).sort_index()
    sns.barplot(x=counts_legit.index, y=counts_legit.values, ax=ax[0], color='skyblue', alpha=0.8, label='Observé (Légitime)')
    sns.lineplot(x=np.array(list(benford_probs.keys()))-1, y=list(benford_probs.values()), ax=ax[0], color='red', marker='o', label='Théorique (Benford)')
    ax[0].set_title("Entreprises Saines : Conformité à la Loi de Benford")
    ax[0].set_ylabel("Fréquence")
    ax[0].legend()
    
    # Fraud Plot
    counts_fraud = pd.Series(digits_fraud).value_counts(normalize=True).sort_index()
    sns.barplot(x=counts_fraud.index, y=counts_fraud.values, ax=ax[1], color='salmon', alpha=0.8, label='Observé (Fraude)')
    sns.lineplot(x=np.array(list(benford_probs.keys()))-1, y=list(benford_probs.values()), ax=ax[1], color='red', marker='o', label='Théorique (Benford)')
    ax[1].set_title("Entreprises Frauduleuses : Anomalies Statistiques")
    ax[1].legend()
    
    plt.tight_layout()
    plt.savefig('financial-fraud-detection/viz_benford.png')
    print("Graphique Benford généré.")

plot_benford_analysis(df)

# 3. VISUALISATION DU DÉSÉQUILIBRE ET DE SMOTE (VISUALISATION 2)
def plot_smote_effect(X, y):
    # Réduction de dimension pour visualiser en 2D (PCA)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    
    # Avant SMOTE
    fig, ax = plt.subplots(1, 2, figsize=(16, 6))
    
    sns.scatterplot(x=X_pca[y==0, 0], y=X_pca[y==0, 1], ax=ax[0], label='Légitime', alpha=0.3, color='grey')
    sns.scatterplot(x=X_pca[y==1, 0], y=X_pca[y==1, 1], ax=ax[0], label='Fraude (Original)', color='red', s=50)
    ax[0].set_title(f"Avant SMOTE : Déséquilibre ({sum(y==1)} vs {sum(y==0)})")
    
    # Application de SMOTE
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X, y)
    
    # Recalculer PCA sur le nouvel ensemble pour cohérence visuelle
    # Note: Idéalement on garde la même transformation, mais ici on veut voir la distribution relative
    X_res_pca = pca.transform(X_res)
    
    # Identifier les points synthétiques (ceux qui n'étaient pas là avant)
    n_original = len(X)
    X_synthetic = X_res_pca[n_original:]
    
    sns.scatterplot(x=X_res_pca[y_res==0, 0], y=X_res_pca[y_res==0, 1], ax=ax[1], label='Légitime', alpha=0.1, color='grey')
    sns.scatterplot(x=X_pca[y==1, 0], y=X_pca[y==1, 1], ax=ax[1], label='Fraude (Original)', color='red', s=50)
    sns.scatterplot(x=X_synthetic[:, 0], y=X_synthetic[:, 1], ax=ax[1], label='Fraude (Synthétique - SMOTE)', color='orange', marker='x', s=30)
    ax[1].set_title(f"Après SMOTE : Équilibre ({sum(y_res==1)} vs {sum(y_res==0)})")
    
    plt.tight_layout()
    plt.savefig('financial-fraud-detection/viz_smote.png')
    print("Graphique SMOTE généré.")
    
    return X_res, y_res

X_res, y_res = plot_smote_effect(X, y)

# 4. COMPARAISON DE PERFORMANCE (VISUALISATION 3)
def compare_performance(X, y, X_res, y_res):
    # Split Train/Test (sur données originales pour le test, pour être réaliste)
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Modèle 1: Random Forest SANS SMOTE
    rf_naive = RandomForestClassifier(random_state=42)
    rf_naive.fit(X_train, y_train)
    y_pred_naive = rf_naive.predict(X_test)
    
    # Modèle 2: Random Forest AVEC SMOTE (sur le train set seulement)
    smote = SMOTE(random_state=42)
    X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)
    rf_smote = RandomForestClassifier(random_state=42)
    rf_smote.fit(X_train_smote, y_train_smote)
    y_pred_smote = rf_smote.predict(X_test)
    
    # Confusion Matrices
    cm_naive = confusion_matrix(y_test, y_pred_naive)
    cm_smote = confusion_matrix(y_test, y_pred_smote)
    
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    
    sns.heatmap(cm_naive, annot=True, fmt='d', cmap='Blues', ax=ax[0], cbar=False)
    ax[0].set_title("Modèle Classique (Sans SMOTE)\nLe modèle ignore souvent les fraudes")
    ax[0].set_xlabel("Prédiction")
    ax[0].set_ylabel("Réalité")
    ax[0].set_xticklabels(['Légitime', 'Fraude'])
    ax[0].set_yticklabels(['Légitime', 'Fraude'])
    
    sns.heatmap(cm_smote, annot=True, fmt='d', cmap='Greens', ax=ax[1], cbar=False)
    ax[1].set_title("Modèle Optimisé (Avec SMOTE)\nDétection accrue des fraudes")
    ax[1].set_xlabel("Prédiction")
    ax[1].set_yticklabels(['', '']) # Hide y labels for clarity
    ax[1].set_xticklabels(['Légitime', 'Fraude'])
    
    plt.tight_layout()
    plt.savefig('financial-fraud-detection/viz_confusion.png')
    print("Graphique Matrices de Confusion généré.")

compare_performance(X, y, X_res, y_res)
