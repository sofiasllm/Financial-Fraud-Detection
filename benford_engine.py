import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import chisquare

class BenfordAnalyzer:
    """
    Analyse forensique basée sur la Loi de Benford.
    La loi de Benford prédit la fréquence d'apparition du premier chiffre (1-9) 
    dans un jeu de données naturelles (financières).
    """

    # Fréquences théoriques (Loi de Benford)
    BENFORD_PROBS = {
        1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 
        5: 0.079, 6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
    }

    def __init__(self, data_series):
        """
        :param data_series: Pandas Series ou liste de valeurs numériques (montants financiers).
        """
        # Conversion en Series si nécessaire
        if not isinstance(data_series, pd.Series):
            data_series = pd.Series(data_series)
        
        # Nettoyage : suppression des NaN, valeurs nulles ou négatives (on travaille sur l'absolu)
        self.data = data_series.dropna()
        self.data = self.data[self.data != 0].abs()
        
        # Extraction du premier chiffre significatif (méthode vectorisée)
        # Convertir en string, supprimer les zéros à gauche et le point décimal
        self.digits = self.data.astype(str).str.lstrip('0.').str[0].astype(int)

    def analyze(self):
        """
        Calcule les fréquences observées vs attendues.
        Retourne un DataFrame avec les écarts et les Z-scores.
        """
        counts = self.digits.value_counts().sort_index()
        total_count = len(self.digits)
        
        # Créer un index complet 1-9 (au cas où certains chiffres manquent)
        full_index = pd.Index(range(1, 10), name='Digit')
        
        # Réindexer et remplir les NaN par 0
        counts = counts.reindex(full_index, fill_value=0)
        
        results = pd.DataFrame(index=full_index)
        results['Actual_Count'] = counts
        results['Actual_Freq'] = results['Actual_Count'] / total_count
        
        # Fréquences théoriques
        results['Expected_Freq'] = results.index.map(self.BENFORD_PROBS)
        results['Expected_Count'] = results['Expected_Freq'] * total_count
        
        # Différence absolue
        results['Difference_Abs'] = abs(results['Actual_Freq'] - results['Expected_Freq'])
        
        # Z-score pour tester la significativité de l'écart (approximation normale)
        # Z = (|p - P| - 1/2n) / sqrt(P(1-P)/n)
        # P = Expected_Freq, p = Actual_Freq, n = total_count
        P = results['Expected_Freq']
        p = results['Actual_Freq']
        n = total_count
        
        # Avoid division by zero if n is small (though unlikely in financial datasets)
        if n > 0:
            results['Z_Score'] = (abs(p - P) - (1/(2*n))) / np.sqrt(P*(1-P)/n)
        else:
            results['Z_Score'] = 0.0
            
        return results

    def plot_results(self, results):
        """
        Génère un graphique Plotly futuriste.
        """
        fig = go.Figure()

        # Barre pour les données réelles
        fig.add_trace(go.Bar(
            x=results.index,
            y=results['Actual_Freq'],
            name='Réel (Observé)',
            marker_color='#00F0FF', # Cyan néon
            opacity=0.8
        ))

        # Ligne pour la loi de Benford
        fig.add_trace(go.Scatter(
            x=results.index,
            y=results['Expected_Freq'],
            name='Théorique (Benford)',
            line=dict(color='#FF0055', width=4, dash='dot'), # Rose néon
            mode='lines+markers'
        ))

        fig.update_layout(
            title="<span style='font-size: 20px; color: #fff;'>ANALYSE BENFORD : DÉTECTION D'ANOMALIES</span>",
            plot_bgcolor='rgba(10, 10, 20, 1)',
            paper_bgcolor='rgba(10, 10, 20, 1)',
            font=dict(color='#fff', family="Courier New"),
            xaxis=dict(title='Premier Chiffre', tickmode='linear', dtick=1),
            yaxis=dict(title='Fréquence'),
            legend=dict(font=dict(color='#fff')),
            template="plotly_dark"
        )
        return fig

# Exemple d'utilisation (Simulation)
if __name__ == "__main__":
    # Génération de données factices (mélange log-normal + bruit uniforme suspect)
    np.random.seed(42)
    legit_data = np.random.lognormal(mean=10, sigma=1, size=1000)
    fraud_data = np.random.uniform(low=1000, high=9000, size=200) # Les fraudeurs inventent souvent des chiffres aléatoires (uniforme)
    
    mixed_data = np.concatenate([legit_data, fraud_data])
    
    analyzer = BenfordAnalyzer(mixed_data)
    res = analyzer.analyze()
    print("Résultats de l'analyse Benford :")
    print(res[['Actual_Freq', 'Expected_Freq', 'Z_Score']])
