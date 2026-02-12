import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.neighbors import NearestNeighbors

class SMOTE_Engine:
    """
    Implémentation manuelle (ou via imblearn si dispo) de SMOTE.
    Synthetic Minority Over-sampling Technique.
    """
    
    def __init__(self, k_neighbors=5):
        self.k = k_neighbors
        
    def fit_resample(self, X, y):
        """
        Applique SMOTE sur le jeu de données.
        Génère des échantillons synthétiques pour la classe minoritaire (1).
        """
        # Séparation des classes
        X_minority = X[y == 1]
        X_majority = X[y == 0]
        
        n_minority = len(X_minority)
        n_majority = len(X_majority)
        
        if n_minority == 0:
            return X, y
            
        # Calcul du nombre d'échantillons à générer pour équilibrer
        n_synthetic = n_majority - n_minority
        
        if n_synthetic <= 0:
            return X, y
            
        # KNN sur la classe minoritaire
        nbrs = NearestNeighbors(n_neighbors=min(self.k + 1, n_minority)).fit(X_minority)
        distances, indices = nbrs.kneighbors(X_minority)
        
        synthetic_samples = []
        
        # Génération
        for i in range(n_synthetic):
            # Choisir un point aléatoire de la classe minoritaire
            idx_rand = np.random.randint(0, n_minority)
            origin_point = X_minority.iloc[idx_rand].values
            
            # Choisir un voisin aléatoire de ce point
            # indices[idx_rand] contient les index des k voisins (dont lui-même en 0)
            neighbor_idx_in_minority = indices[idx_rand][np.random.randint(1, len(indices[idx_rand]))]
            neighbor_point = X_minority.iloc[neighbor_idx_in_minority].values
            
            # Interpolation
            gap = np.random.random()
            new_point = origin_point + (neighbor_point - origin_point) * gap
            synthetic_samples.append(new_point)
            
        X_synthetic = pd.DataFrame(synthetic_samples, columns=X.columns)
        y_synthetic = pd.Series([1] * n_synthetic)
        
        # Fusion
        X_resampled = pd.concat([X, X_synthetic], ignore_index=True)
        y_resampled = pd.concat([y, y_synthetic], ignore_index=True)
        
        return X_resampled, y_resampled

class FraudDetector:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.smote = SMOTE_Engine(k_neighbors=5)
        
    def train(self, df):
        X = df.drop(columns=['is_fraud'])
        y = df['is_fraud']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Application SMOTE sur le train set UNIQUEMENT
        # (Jamais sur le test set pour ne pas biaiser l'évaluation)
        print(f"Avant SMOTE - Fraudes: {sum(y_train == 1)} / Total: {len(y_train)}")
        X_train_res, y_train_res = self.smote.fit_resample(X_train, y_train)
        print(f"Après SMOTE - Fraudes: {sum(y_train_res == 1)} / Total: {len(y_train_res)}")
        
        # Entraînement
        self.model.fit(X_train_res, y_train_res)
        
        # Évaluation
        y_pred = self.model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        return report, X_test, y_test, y_pred

    def predict_risk(self, company_data):
        """
        Prédit le score de risque (probabilité de fraude) pour une nouvelle entreprise.
        """
        # company_data doit être un DataFrame ou dict avec les mêmes colonnes
        if isinstance(company_data, dict):
            company_data = pd.DataFrame([company_data])
            
        prob_fraud = self.model.predict_proba(company_data)[0][1]
        return prob_fraud
