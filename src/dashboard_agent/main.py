import pandas as pd
from agent import DashboardAgent

def main():
    """
    Exemple d'utilisation de DashboardAgent pour créer une visualisation
    à partir d'un DataFrame et d'une description en langage naturel.
    """
    # 1. Créer un exemple de DataFrame.
    # Dans une application réelle, ces données pourraient provenir de l'agent BigQuery.
    data = {
        'ville': ['Paris', 'Lyon', 'Marseille', 'Lille', 'Bordeaux', 'Toulouse'],
        'population': [2141000, 513275, 861635, 232741, 249712, 471941],
        'region': ['Île-de-France', 'Auvergne-Rhône-Alpes', 'Provence-Alpes-Côte d\'Azur', 'Hauts-de-France', 'Nouvelle-Aquitaine', 'Occitanie']
    }
    sample_df = pd.DataFrame(data)

    print("Voici un aperçu des données disponibles :")
    print(sample_df)
    print("\n")

    # 2. Initialiser l'agent de tableau de bord.
    dashboard_agent = DashboardAgent()

    # 3. Demander à l'utilisateur quel type de graphique il souhaite.
    description = input("Décrivez le graphique que vous souhaitez créer (par exemple, 'un diagramme à barres montrant la population par ville') : ")

    # 4. Générer et afficher la visualisation.
    dashboard_agent.create_visualization(sample_df, description)

if __name__ == "__main__":
    main()

