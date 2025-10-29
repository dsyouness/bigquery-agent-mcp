# Configuration MCP pour Claude Desktop

## Installation avec `uv` (Recommandé)

[`uv`](https://github.com/astral-sh/uv) est un gestionnaire de paquets Python ultra-rapide. C'est la méthode recommandée pour les serveurs MCP.

### 1. Installer uv (si ce n'est pas déjà fait)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Cloner le projet

```bash
git clone <votre-repo>
cd agent-py
```

### 3. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet avec :

```env
GOOGLE_CLOUD_PROJECT_ID="votre-projet-gcp"
```

**Note:** Vous n'avez plus besoin de `GEMINI_API_KEY` pour le serveur MCP ! 
Le client MCP (Claude Desktop, etc.) utilise son propre modèle LLM.

### 4. Authentification Google Cloud

```bash
gcloud auth application-default login
```

## Configuration pour Claude Desktop

Ajoutez cette configuration à votre fichier de configuration Claude Desktop :

**Sur macOS/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Sur Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "bigquery-dashboard": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/younessdrissislimani/PycharmProjects/agent-py",
        "run",
        "bigquery-dashboard-mcp"
      ],
      "env": {
        "GOOGLE_CLOUD_PROJECT_ID": "votre-projet-gcp"
      }
    }
  }
}
```

**Important:** 
- Remplacez `/Users/younessdrissislimani/PycharmProjects/agent-py` par le chemin absolu vers votre projet
- Remplacez `votre-projet-gcp` par votre véritable ID de projet Google Cloud
- **Aucune clé API LLM n'est nécessaire** - Claude Desktop utilise son propre modèle Claude !
- `uv` gérera automatiquement l'installation des dépendances au premier lancement

## Alternative : Installation manuelle avec pip

Si vous préférez ne pas utiliser `uv` :

### 1. Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration Claude Desktop (avec Python)

```json
{
  "mcpServers": {
    "bigquery-dashboard": {
      "command": "python",
      "args": [
        "/Users/younessdrissislimani/PycharmProjects/agent-py/mcp_server.py"
      ],
      "env": {
        "GOOGLE_CLOUD_PROJECT_ID": "votre-projet-gcp"
      }
    }
  }
}
```

## Outils disponibles dans Claude Desktop

Une fois configuré, Claude aura accès à 5 outils pour interagir avec BigQuery :

### 1. `list_bigquery_datasets`
Liste tous les datasets disponibles dans votre projet.

### 2. `list_bigquery_tables`
Liste les tables d'un dataset spécifique.

### 3. `get_table_schema`
Récupère le schéma complet d'une table (colonnes, types, descriptions).

### 4. `execute_bigquery_sql`
Exécute une requête SQL sur BigQuery et retourne les résultats.

### 5. `create_plotly_visualization`
Crée une visualisation interactive à partir des données.

## Comment ça marche ?

Contrairement à la version précédente, le serveur MCP **n'utilise plus de modèle LLM interne**.
À la place :

1. **Claude Desktop utilise Claude** (son propre modèle)
2. **Autres clients MCP utilisent leur propre modèle**
3. Le serveur expose uniquement des **outils de bas niveau** pour interagir avec BigQuery

### Exemple d'utilisation dans Claude Desktop

**Vous:** Peux-tu me montrer le nombre de vues par vidéo dans BigQuery ?

**Claude fait automatiquement:**
1. Utilise `list_bigquery_datasets` pour voir les datasets
2. Utilise `list_bigquery_tables` pour explorer les tables
3. Utilise `get_table_schema` pour comprendre la structure
4. Génère une requête SQL avec son propre intelligence
5. Utilise `execute_bigquery_sql` pour exécuter la requête
6. Vous présente les résultats

**Vous:** Fais-moi un graphique de ces données.

**Claude fait automatiquement:**
1. Génère du code Plotly adapté aux données
2. Utilise `create_plotly_visualization` pour créer le graphique

## Avantages de cette approche avec `uv`

✅ **Installation automatique** : `uv` installe les dépendances à la volée
✅ **Isolation** : Pas besoin de gérer manuellement les environnements virtuels
✅ **Performance** : Installation 10-100x plus rapide que pip
✅ **Fiabilité** : Gestion déterministe des dépendances
✅ **Agnostique au modèle** : Fonctionne avec n'importe quel client MCP
✅ **Pas de coûts API Gemini** : Utilise le modèle du client
✅ **Plus simple** : Configuration minimale requise
✅ **Plus flexible** : Le client choisit son modèle préféré

## Test du serveur MCP

### Avec uv (recommandé)

```bash
uv run bigquery-dashboard-mcp
```

### Avec Python

```bash
python mcp_server.py
```

Le serveur communique via stdin/stdout selon le protocole MCP.

## Débogage avec MCP Inspector

Pour déboguer votre serveur MCP avec `uv` :

```bash
npx @modelcontextprotocol/inspector uv --directory /chemin/vers/agent-py run bigquery-dashboard-mcp
```

Ou avec Python :

```bash
npx @modelcontextprotocol/inspector python mcp_server.py
```

Cela ouvrira une interface web pour tester les outils interactivement.

## Compatibilité avec différents clients MCP

| Client | Modèle utilisé | Configuration requise | Méthode recommandée |
|--------|----------------|----------------------|---------------------|
| **Claude Desktop** | Claude (Anthropic) | `GOOGLE_CLOUD_PROJECT_ID` | `uv` |
| **Cline/VSCode** | Configurable | `GOOGLE_CLOUD_PROJECT_ID` | `uv` |
| **Cursor** | Configurable | `GOOGLE_CLOUD_PROJECT_ID` | `uv` |
| **Autres clients MCP** | Selon le client | `GOOGLE_CLOUD_PROJECT_ID` | `uv` |

## Architecture mise à jour

```
┌─────────────────────────────────────┐
│   Client MCP (ex: Claude Desktop)   │
│   Utilise son propre LLM (Claude)   │
└────────────────┬────────────────────┘
                 │ MCP Protocol
                 │
┌────────────────▼────────────────────┐
│       uv run bigquery-dashboard-mcp │
│       (mcp_server.py)               │
│   (Pas de LLM interne)              │
│                                     │
│   Outils exposés:                   │
│   - list_bigquery_datasets          │
│   - list_bigquery_tables            │
│   - get_table_schema                │
│   - execute_bigquery_sql            │
│   - create_plotly_visualization     │
└────────────────┬────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐    ┌────▼─────┐
│  BigQuery    │    │  Plotly  │
└──────────────┘    └──────────┘
```

## Troubleshooting

### Le serveur ne démarre pas avec uv
- Vérifiez que `uv` est installé : `uv --version`
- Vérifiez que `GOOGLE_CLOUD_PROJECT_ID` est défini dans la configuration
- Vérifiez que vous êtes authentifié avec `gcloud auth application-default login`

### Les outils n'apparaissent pas dans Claude Desktop
- Vérifiez le chemin absolu dans `claude_desktop_config.json`
- Redémarrez Claude Desktop après modification de la configuration
- Consultez les logs de Claude Desktop (Menu > View > Show Logs)

### Erreurs d'authentification BigQuery
```bash
gcloud auth application-default login
```

### uv ne trouve pas le projet
Assurez-vous que le chemin dans `--directory` pointe vers le dossier contenant `pyproject.toml`

## Pour l'usage direct en terminal (sans MCP)

Si vous voulez utiliser les agents directement en terminal avec votre choix de LLM, 
consultez le README principal pour configurer le modèle de votre choix.

**Avec uv:**
```bash
uv run python main.py
```

**Avec Python classique:**
```bash
python main.py
```
