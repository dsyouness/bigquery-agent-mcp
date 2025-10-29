from dotenv import load_dotenv
import os
from src.bigquery_agent.agent import BigQueryAgent
from src.dashboard_agent.agent import DashboardAgent

def main():
    """
    Orchestre l'utilisation de BigQueryAgent et DashboardAgent pour
    passer du langage naturel à une visualisation de données de BigQuery.
    """
    load_dotenv()
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not project_id or not gemini_api_key:
        print("Veuillez définir GOOGLE_CLOUD_PROJECT_ID et GEMINI_API_KEY dans votre fichier .env ou vos variables d'environnement.")
        return

    # --- Étape 1: Interagir avec l'agent BigQuery ---
    print("=== Agent BigQuery Intelligent ===")
    print("L'agent va explorer automatiquement vos datasets et tables pour trouver les bonnes données.\n")

    # Initialiser l'agent BigQuery
    bq_agent = BigQueryAgent(project_id=project_id)

    # Obtenir la question de l'utilisateur pour la requête de données
    natural_language_query = input("Posez votre question (ex: 'donne moi le nombre de vues par vidéo') : ")

    # L'agent va automatiquement découvrir les tables et exécuter la requête
    print("\n--- L'agent analyse votre question et explore BigQuery ---")
    results_df = bq_agent.query(natural_language_query)

    # Vérifier si nous avons des résultats
    if results_df.empty or 'error' in results_df.columns or 'message' in results_df.columns:
        print("\nAucune donnée n'a été récupérée ou une erreur s'est produite.")
        if 'error' in results_df.columns:
            print(f"Erreur: {results_df['error'].iloc[0]}")
        elif 'message' in results_df.columns:
            print(f"Message: {results_df['message'].iloc[0]}")
        return

    print("\n--- Résultats de la requête ---")
    print(results_df)

    # --- Étape 2: Proposer et interagir avec l'agent de Tableau de Bord ---
    visualize_choice = input("\nVoulez-vous visualiser ces résultats dans un tableau de bord ? (oui/non): ").lower()
    if visualize_choice in ['oui', 'o', 'yes', 'y']:
        print("\n--- Création de la Visualisation ---")

        # Initialiser l'agent de tableau de bord
        dashboard_agent = DashboardAgent()

        # Utiliser la question originale comme description pour la visualisation
        print(f"Utilisation de la description : '{natural_language_query}' pour générer le graphique.")
        dashboard_agent.create_visualization(results_df, natural_language_query)
    else:
        print("La création de la visualisation a été ignorée.")

    print("\n--- Processus Terminé ---")

if __name__ == "__main__":
    main()
