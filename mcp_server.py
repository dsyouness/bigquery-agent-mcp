#!/usr/bin/env python3
"""
Serveur MCP pour les agents BigQuery et Dashboard.
Compatible avec Claude Desktop et d'autres clients MCP.

Le serveur expose des outils qui utilisent le LLM du client MCP (ex: Claude pour Claude Desktop).
Pour BigQuery, nous utilisons seulement les capacités d'exploration et d'exécution SQL.
"""

import asyncio
import os
import json
from typing import Any
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from google.cloud import bigquery
import pandas as pd
import plotly.express as px

load_dotenv()

# Initialiser le serveur MCP
app = Server("bigquery-dashboard-agent")

# Client BigQuery global
bq_client = None
last_query_result = None


def initialize_bigquery_client():
    """Initialise le client BigQuery."""
    global bq_client

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT_ID doit être défini dans les variables d'environnement.")

    bq_client = bigquery.Client(project=project_id)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Liste les outils disponibles."""
    return [
        Tool(
            name="list_bigquery_datasets",
            description="Liste tous les datasets disponibles dans le projet BigQuery.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_bigquery_tables",
            description="Liste toutes les tables dans un dataset BigQuery spécifique.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "L'ID du dataset à explorer"
                    }
                },
                "required": ["dataset_id"]
            }
        ),
        Tool(
            name="get_table_schema",
            description="Récupère le schéma détaillé d'une table BigQuery (colonnes, types, descriptions).",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "L'ID du dataset contenant la table"
                    },
                    "table_id": {
                        "type": "string",
                        "description": "L'ID de la table"
                    }
                },
                "required": ["dataset_id", "table_id"]
            }
        ),
        Tool(
            name="execute_bigquery_sql",
            description=(
                "Exécute une requête SQL sur BigQuery et retourne les résultats. "
                "Utilisez le format complet: project.dataset.table dans les requêtes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "La requête SQL à exécuter sur BigQuery"
                    }
                },
                "required": ["sql_query"]
            }
        ),
        Tool(
            name="create_plotly_visualization",
            description=(
                "Génère et affiche une visualisation Plotly à partir des dernières données récupérées. "
                "Nécessite d'avoir exécuté une requête SQL auparavant. "
                "Fournissez le code Python Plotly Express à exécuter."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "plotly_code": {
                        "type": "string",
                        "description": (
                            "Code Python utilisant plotly.express (importé comme 'px') et le DataFrame 'df'. "
                            "Exemple: fig = px.bar(df, x='category', y='value'); fig.show()"
                        )
                    }
                },
                "required": ["plotly_code"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Exécute un outil."""
    global bq_client, last_query_result

    # Initialiser le client BigQuery si nécessaire
    if bq_client is None:
        initialize_bigquery_client()

    try:
        if name == "list_bigquery_datasets":
            try:
                datasets = list(bq_client.list_datasets())
                if not datasets:
                    return [TextContent(
                        type="text",
                        text="Aucun dataset trouvé dans ce projet BigQuery."
                    )]

                dataset_list = [f"- {dataset.dataset_id}" for dataset in datasets]
                result = "Datasets BigQuery disponibles:\n" + "\n".join(dataset_list)

                return [TextContent(type="text", text=result)]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Erreur lors de la récupération des datasets: {e}"
                )]

        elif name == "list_bigquery_tables":
            dataset_id = arguments.get("dataset_id")
            if not dataset_id:
                return [TextContent(type="text", text="Erreur: dataset_id est requis.")]

            try:
                tables = list(bq_client.list_tables(dataset_id))
                if not tables:
                    return [TextContent(
                        type="text",
                        text=f"Aucune table trouvée dans le dataset '{dataset_id}'."
                    )]

                table_list = [f"- {table.table_id}" for table in tables]
                result = f"Tables dans le dataset '{dataset_id}':\n" + "\n".join(table_list)

                return [TextContent(type="text", text=result)]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Erreur lors de la récupération des tables: {e}"
                )]

        elif name == "get_table_schema":
            dataset_id = arguments.get("dataset_id")
            table_id = arguments.get("table_id")

            if not dataset_id or not table_id:
                return [TextContent(
                    type="text",
                    text="Erreur: dataset_id et table_id sont requis."
                )]

            try:
                full_table_id = f"{bq_client.project}.{dataset_id}.{table_id}"
                table = bq_client.get_table(full_table_id)

                schema_info = []
                for field in table.schema:
                    schema_info.append(f"  - {field.name}: {field.field_type} ({field.mode})")
                    if field.description:
                        schema_info.append(f"    Description: {field.description}")

                result = f"Schéma de la table '{full_table_id}':\n"
                result += f"Nombre de lignes: {table.num_rows:,}\n"
                result += "Colonnes:\n" + "\n".join(schema_info)

                return [TextContent(type="text", text=result)]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Erreur lors de la récupération du schéma: {e}"
                )]

        elif name == "execute_bigquery_sql":
            sql_query = arguments.get("sql_query")
            if not sql_query:
                return [TextContent(type="text", text="Erreur: sql_query est requis.")]

            try:
                query_job = bq_client.query(sql_query)
                results = query_job.result()
                df = results.to_dataframe()

                if df.empty:
                    return [TextContent(
                        type="text",
                        text="La requête a été exécutée mais n'a retourné aucun résultat."
                    )]

                # Stocker le résultat pour une visualisation ultérieure
                last_query_result = df

                # Formater les résultats
                result_text = f"✅ Requête exécutée avec succès!\n\n"
                result_text += f"Nombre de lignes: {len(df):,}\n"
                result_text += f"Colonnes: {', '.join(df.columns)}\n\n"
                result_text += "Aperçu des données (10 premières lignes):\n"
                result_text += df.head(10).to_string(index=False)

                if len(df) > 10:
                    result_text += f"\n\n... et {len(df) - 10} lignes supplémentaires"

                return [TextContent(type="text", text=result_text)]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Erreur lors de l'exécution de la requête SQL:\n{e}"
                )]

        elif name == "create_plotly_visualization":
            plotly_code = arguments.get("plotly_code")
            if not plotly_code:
                return [TextContent(type="text", text="Erreur: plotly_code est requis.")]

            if last_query_result is None or last_query_result.empty:
                return [TextContent(
                    type="text",
                    text="❌ Aucune donnée disponible. Exécutez d'abord une requête SQL avec execute_bigquery_sql."
                )]

            try:
                # Préparer l'environnement d'exécution
                exec_scope = {
                    "df": last_query_result,
                    "px": px,
                    "pd": pd
                }

                # Nettoyer le code (enlever les marqueurs markdown si présents)
                clean_code = plotly_code.strip().replace("```python", "").replace("```", "").strip()

                # Exécuter le code de visualisation
                exec(clean_code, exec_scope)

                result_text = f"✅ Visualisation créée avec succès!\n\n"
                result_text += f"Données utilisées: {len(last_query_result)} lignes, {len(last_query_result.columns)} colonnes\n"
                result_text += f"Colonnes: {', '.join(last_query_result.columns)}\n\n"
                result_text += "La visualisation a été affichée dans le navigateur."

                return [TextContent(type="text", text=result_text)]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Erreur lors de la création de la visualisation:\n{e}\n\nCode fourni:\n{plotly_code}"
                )]

        else:
            return [TextContent(type="text", text=f"❌ Outil inconnu: {name}")]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Erreur inattendue lors de l'exécution de l'outil {name}:\n{str(e)}"
        )]


async def main():
    """Point d'entrée principal du serveur MCP."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run():
    """Point d'entrée synchrone pour le script."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
