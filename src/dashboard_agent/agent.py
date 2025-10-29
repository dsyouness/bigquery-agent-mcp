import os
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from ..llm_config import get_llm, get_provider_info

load_dotenv()

class DashboardAgent:
    def __init__(self):
        # Configurer le modèle LLM dynamiquement selon la configuration
        print(f"🤖 Utilisation du modèle: {get_provider_info()}")
        self.llm = get_llm(temperature=0.3)

    def create_visualization(self, df: pd.DataFrame, description: str):
        """
        Génère et affiche une visualisation de données en utilisant Plotly,
        basée sur une description en langage naturel.

        Args:
            df (pd.DataFrame): Le DataFrame contenant les données à visualiser.
            description (str): Une description en langage naturel du graphique souhaité.
        """
        if df.empty:
            print("Le DataFrame est vide. Impossible de créer une visualisation.")
            return

        # Fournir au modèle un aperçu des données
        data_preview = df.head().to_string()
        column_names = ", ".join(df.columns)

        prompt = f"""
        En tant qu'expert en visualisation de données, votre tâche est de générer du code Python pour créer un graphique avec Plotly Express.
        Le code doit utiliser un DataFrame pandas nommé `df`.

        Voici un aperçu des données dans le DataFrame:
        {data_preview}

        Les colonnes disponibles sont : {column_names}.

        Description de la visualisation souhaitée : "{description}"

        Instructions :
        1. Importez plotly.express en tant que px.
        2. Utilisez le DataFrame `df` qui sera disponible dans le scope d'exécution.
        3. Créez une figure Plotly Express et assignez-la à une variable nommée `fig`.
        4. Appelez `fig.show()` pour afficher le graphique.
        5. Ne générez QUE le code Python. N'ajoutez pas d'explications, de commentaires ou de formatage markdown.
        6. Le code doit être prêt à être exécuté tel quel.
        """

        try:
            response = self.llm.invoke(prompt)
            generated_code = response.content.strip().replace("```python", "").replace("```", "").strip()

            print("\nCode de visualisation généré :")
            print(generated_code)

            # Préparer l'environnement d'exécution pour le code généré
            exec_scope = {
                "df": df,
                "px": px,
                "pd": pd
            }

            # Exécuter le code généré pour créer et afficher le graphique
            print("\nCréation de la visualisation...")
            exec(generated_code, exec_scope)
            print("Visualisation affichée.")

        except Exception as e:
            print(f"Une erreur est survenue lors de la création de la visualisation : {e}")
