import numpy as np
import pandas as pd

class FinancialDataSimulator:
    """
    Générateur de données financières synthétiques pour l'entraînement de modèles de fraude.
    Crée un jeu de données déséquilibré (peu de fraudes) pour justifier l'usage de SMOTE.
    """
    
    def __init__(self, n_samples=1000, fraud_ratio=0.05):
        self.n_samples = n_samples
        self.fraud_ratio = fraud_ratio
        
    def generate(self):
        """
        Génère un DataFrame avec des ratios financiers et une variable cible 'is_fraud'.
        """
        np.random.seed(42)
        n_frauds = int(self.n_samples * self.fraud_ratio)
        n_legit = self.n_samples - n_frauds
        
        # 1. Génération des cas légitimes (Distribution Normale cohérente)
        # Ratios : Liquidité (Current Ratio), Levier (Debt/Equity), Marge (Net Margin), Benford Score (bas)
        legit_data = pd.DataFrame({
            'current_ratio': np.random.normal(loc=1.5, scale=0.3, size=n_legit),
            'debt_to_equity': np.random.normal(loc=0.5, scale=0.1, size=n_legit),
            'net_margin': np.random.normal(loc=0.10, scale=0.02, size=n_legit),
            'benford_deviation': np.random.exponential(scale=0.05, size=n_legit), # Déviation faible
            'text_complexity': np.random.normal(loc=10, scale=2, size=n_legit), # Fog Index moyen
            'is_fraud': 0
        })
        
        # 2. Génération des cas frauduleux (Anomalies)
        # Ratios souvent manipulés : Marge gonflée, Dette cachée, Benford Score élevé
        fraud_data = pd.DataFrame({
            'current_ratio': np.random.normal(loc=0.8, scale=0.4, size=n_frauds), # Souvent problèmes de liquidité
            'debt_to_equity': np.random.normal(loc=1.2, scale=0.5, size=n_frauds), # Dette élevée
            'net_margin': np.random.normal(loc=0.15, scale=0.05, size=n_frauds), # Marges artificiellement lissées
            'benford_deviation': np.random.normal(loc=0.3, scale=0.1, size=n_frauds), # Déviation forte (chiffres inventés)
            'text_complexity': np.random.normal(loc=16, scale=3, size=n_frauds), # Langage complexe pour masquer
            'is_fraud': 1
        })
        
        # Fusion et mélange
        df = pd.concat([legit_data, fraud_data], ignore_index=True)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        return df

if __name__ == "__main__":
    sim = FinancialDataSimulator()
    df = sim.generate()
    print(f"Data shape: {df.shape}")
    print(f"Fraud distribution:\n{df['is_fraud'].value_counts(normalize=True)}")
