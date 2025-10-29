import os
from dotenv import load_dotenv
from google.cloud import bigquery
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
import pandas as pd
from ..llm_config import get_llm, get_provider_info

load_dotenv()


class BigQueryAgent:
    def __init__(self, project_id):
        self.project_id = project_id
        self.client = bigquery.Client(project=self.project_id)

        # Initialiser le modèle LLM dynamiquement selon la configuration
        print(f"🤖 Utilisation du modèle: {get_provider_info()}")
        self.llm = get_llm(temperature=0)

        # Créer les outils pour l'agent
        self.tools = self._create_tools()

        # Créer l'agent LangChain
        self.agent = self._create_agent()

    def _create_tools(self):
        """Crée les outils que l'agent peut utiliser pour interagir avec BigQuery."""

        client = self.client  # Capture pour la closure

        @tool
        def list_datasets() -> str:
            """Liste tous les datasets disponibles dans le projet BigQuery.
            Utilisez cet outil pour découvrir quels datasets sont disponibles."""
            try:
                datasets = list(client.list_datasets())
                if not datasets:
                    return "Aucun dataset trouvé dans ce projet."

                dataset_list = [f"- {dataset.dataset_id}" for dataset in datasets]
                return "Datasets disponibles:\n" + "\n".join(dataset_list)
            except Exception as e:
                return f"Erreur lors de la récupération des datasets: {e}"

        @tool
        def list_tables(dataset_id: str) -> str:
            """Liste toutes les tables dans un dataset BigQuery spécifique.

            Args:
                dataset_id: L'ID du dataset à explorer.
            """
            try:
                tables = list(client.list_tables(dataset_id))
                if not tables:
                    return f"Aucune table trouvée dans le dataset '{dataset_id}'."

                table_list = [f"- {table.table_id}" for table in tables]
                return f"Tables dans le dataset '{dataset_id}':\n" + "\n".join(table_list)
            except Exception as e:
                return f"Erreur lors de la récupération des tables du dataset '{dataset_id}': {e}"

        @tool
        def get_table_schema(dataset_id: str, table_id: str) -> str:
            """Récupère le schéma d'une table BigQuery spécifique.

            Args:
                dataset_id: L'ID du dataset contenant la table.
                table_id: L'ID de la table dont on veut le schéma.
            """
            try:
                full_table_id = f"{client.project}.{dataset_id}.{table_id}"
                table = client.get_table(full_table_id)

                schema_info = []
                for field in table.schema:
                    schema_info.append(f"  - {field.name}: {field.field_type} ({field.mode})")
                    if field.description:
                        schema_info.append(f"    Description: {field.description}")

                result = f"Schéma de la table '{full_table_id}':\n"
                result += f"Nombre de lignes: {table.num_rows}\n"
                result += "Colonnes:\n" + "\n".join(schema_info)

                return result
            except Exception as e:
                return f"Erreur lors de la récupération du schéma de {dataset_id}.{table_id}: {e}"

        @tool
        def execute_sql_query(sql_query: str) -> str:
            """Exécute une requête SQL sur BigQuery et retourne un aperçu des résultats.

            Args:
                sql_query: La requête SQL à exécuter.
            """
            try:
                query_job = client.query(sql_query)
                results = query_job.result()
                df = results.to_dataframe()

                if df.empty:
                    return "La requête n'a retourné aucun résultat."

                # Stocker le dataframe pour une utilisation ultérieure
                self.last_query_result = df

                return f"Requête exécutée avec succès. Aperçu des résultats:\n{df.head(10).to_string()}"
            except Exception as e:
                return f"Erreur lors de l'exécution de la requête SQL: {e}"

        return [list_datasets, list_tables, get_table_schema, execute_sql_query]

    def _create_agent(self):
        """Crée l'agent LangChain avec les outils."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """Vous êtes un assistant expert en BigQuery avec une capacité de raisonnement autonome. 
Votre mission est d'explorer intelligemment les données BigQuery pour répondre aux questions de l'utilisateur.

PROCESSUS DE RECHERCHE AUTONOME À SUIVRE SYSTÉMATIQUEMENT:

1. EXPLORATION DES DATASETS
   - Commencez TOUJOURS par lister tous les datasets disponibles avec list_datasets()
   - Identifiez les datasets qui pourraient être pertinents selon la question

2. EXPLORATION DES TABLES
   - Pour chaque dataset pertinent, listez toutes ses tables avec list_tables(dataset_id)
   - Analysez les noms des tables pour identifier les plus prometteuses
   - Ne présumez JAMAIS du nom d'une table, explorez-les systématiquement

3. ANALYSE DES SCHÉMAS
   - Examinez le schéma des tables candidates avec get_table_schema(dataset_id, table_id)
   - Comparez les colonnes disponibles avec ce qui est demandé dans la question
   - Si une table ne correspond pas, continuez à explorer d'autres tables
   - Cherchez les correspondances de noms de colonnes (ex: "vues", "views", "video", etc.)

4. SÉLECTION ET EXÉCUTION
   - Une fois que vous avez trouvé la table appropriée avec les bonnes colonnes, construisez une requête SQL
   - Utilisez TOUJOURS le nom complet de la table: project.dataset.table
   - Exécutez la requête avec execute_sql_query(sql_query)

RÈGLES IMPORTANTES:
- Soyez méthodique: explorez TOUS les datasets et tables si nécessaire
- Ne devinez JAMAIS le nom d'une table ou d'un dataset
- Si vous ne trouvez pas de table correspondante après exploration complète, informez l'utilisateur
- Privilégiez la précision sur la rapidité
- Utilisez des requêtes SQL optimisées pour BigQuery (avec LIMIT si approprié)

EXEMPLE DE RAISONNEMENT:
Question: "donne moi le nombre de vues par vidéo"
1. Je liste les datasets
2. Je trouve un dataset "youtube_analytics" 
3. Je liste ses tables
4. Je trouve une table "video_stats"
5. J'examine son schéma et je vois les colonnes: video_id, video_title, views
6. Je construis: SELECT video_id, video_title, views FROM project.youtube_analytics.video_stats
7. J'exécute la requête

Commencez toujours votre exploration maintenant."""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True, max_iterations=15)

    def query(self, natural_language_query: str) -> pd.DataFrame:
        """
        Prend une question en langage naturel et retourne un DataFrame avec les résultats.

        Args:
            natural_language_query: La question de l'utilisateur en langage naturel.

        Returns:
            Un DataFrame pandas contenant les résultats de la requête.
        """
        self.last_query_result = None

        try:
            # L'agent va explorer BigQuery, trouver la bonne table, et exécuter la requête
            result = self.agent.invoke({"input": natural_language_query})

            # Si nous avons des résultats stockés, les retourner
            if hasattr(self, 'last_query_result') and self.last_query_result is not None:
                return self.last_query_result

            # Sinon, retourner un DataFrame vide avec un message
            return pd.DataFrame({"message": ["L'agent n'a pas pu exécuter de requête. Voir les logs ci-dessus."]})

        except Exception as e:
            print(f"Erreur lors de l'exécution de la requête: {e}")
            return pd.DataFrame({"error": [str(e)]})
