from dotenv import load_dotenv
import os
from agent import BigQueryAgent

def main():
    """
    Exemple d'utilisation de BigQueryAgent pour convertir du langage naturel en SQL,
    exécuter la requête et afficher les résultats.
    """
    load_dotenv()
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")

    if not project_id:
        print("La variable d'environnement GOOGLE_CLOUD_PROJECT_ID n'est pas définie.")
        return

    # Remplacez par votre ID de table BigQuery complet, par exemple "votre-projet.votre-dataset.votre-table"
    # J'utilise une table publique BigQuery pour cet exemple.
    table_id = "bigquery-public-data.samples.shakespeare"

    # Initialiser l'agent
    agent = BigQueryAgent(project_id=project_id)

    # Demander à l'utilisateur une question en langage naturel
    natural_language_query = input("Posez votre question sur les données (par exemple, 'compte le nombre de mots uniques') : ")

    # Convertir la question en SQL
    sql_query = agent.text_to_sql(natural_language_query, table_id)
    print("\nRequête SQL générée :")
    print(sql_query)

    if "SELECT" in sql_query.upper():
        # Exécuter la requête et afficher les résultats
        print("\nExécution de la requête...")
        results_df = agent.run_query(sql_query)
        print("\nRésultats :")
        print(results_df)
    else:
        print("\nAucune requête SQL valide n'a été générée.")

if __name__ == "__main__":
    main()

