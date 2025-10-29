# 🤖 Agents BigQuery & Dashboard avec MCP

Système d'agents intelligents pour interroger BigQuery et créer des visualisations automatiquement, avec support du protocole MCP pour Claude Desktop.

**🎯 Nouveau : Support multi-LLM !** Le système est maintenant agnostique au modèle LLM. Choisissez entre Gemini, Claude, OpenAI ou Ollama.

**⚡ Utilise `uv` pour une installation ultra-rapide et fiable !**

## ✨ Fonctionnalités

- 🔍 **Agent BigQuery Intelligent** : Découverte automatique des datasets et tables
- 📊 **Agent Dashboard** : Génération automatique de visualisations Plotly
- 🔌 **Support MCP** : Compatible avec Claude Desktop et autres clients MCP
- 🤝 **Interaction naturelle** : Posez vos questions en langage naturel
- 🎯 **Exploration autonome** : L'agent raisonne et trouve les bonnes données
- 🔄 **Multi-LLM** : Choisissez votre modèle préféré (Gemini, Claude, OpenAI, Ollama)
- ⚡ **Installation moderne avec `uv`** : 10-100x plus rapide que pip

## 📦 Installation rapide avec `uv` (Recommandé)

### 1. Installer uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Cloner et configurer

```bash
git clone <votre-repo>
cd agent-py

# Créer le fichier .env
cp .env.example .env
# Éditez .env et ajoutez votre GOOGLE_CLOUD_PROJECT_ID

# Authentification Google Cloud
gcloud auth application-default login
```

### 3. C'est tout ! 🎉

Pas besoin d'installer manuellement les dépendances. `uv` s'en charge automatiquement.

## 🚀 Utilisation

### Mode 1 : MCP avec Claude Desktop (Recommandé)

**Configuration minimale - Juste ça suffit :**

Éditez `~/Library/Application Support/Claude/claude_desktop_config.json` :

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

**Avantages :**
- ✅ Pas de clé API LLM nécessaire (utilise Claude)
- ✅ Installation automatique des dépendances par `uv`
- ✅ Pas de gestion d'environnement virtuel
- ✅ Mises à jour simplifiées

**Redémarrez Claude Desktop et c'est prêt !**

### Mode 2 : Utilisation directe en terminal

#### Avec uv (recommandé)

```bash
# Configure ton LLM dans .env
echo 'LLM_PROVIDER=gemini' >> .env
echo 'GEMINI_API_KEY=ta-cle' >> .env

# Lance le script
uv run python main.py
```

#### Avec pip classique

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 🔧 Comparaison des méthodes

| Méthode | Installation | Performance | Gestion dépendances | Recommandé pour |
|---------|--------------|-------------|---------------------|-----------------|
| **uv** | Automatique | ⚡ Ultra-rapide | Automatique | MCP, production |
| **pip + venv** | Manuelle | Lent | Manuelle | Développement local |

## 🛠️ Test et débogage

### Tester le serveur MCP

```bash
# Avec uv
uv run bigquery-dashboard-mcp

# Avec Python
python mcp_server.py
```

### MCP Inspector (débogage visuel)

```bash
npx @modelcontextprotocol/inspector uv --directory $(pwd) run bigquery-dashboard-mcp
```

Cela ouvre une interface web pour tester vos outils interactivement.

```
┌─────────────────────────────────────────────────┐
│              Interface Utilisateur              │
├─────────────────┬───────────────────────────────┤
│  Claude Desktop │  Terminal Direct (main.py)    │
│  (utilise       │  (LLM configurable)           │
│   Claude)       │                               │
└────────┬────────┴───────────────────────────────┘
         │                │
         │ MCP            │ Direct
         │                │
┌────────▼────────────────▼───────────────────────┐
│            Orchestration Layer                  │
│  - mcp_server.py (pas de LLM interne)          │
│  - main.py (LLM configurable)                  │
└────────┬────────────────────────────────────────┘
         │
    ┌────┴──────────────────────┐
    │                           │
┌───▼──────────────┐    ┌──────▼──────────────┐
│ BigQuery Agent   │    │ Dashboard Agent     │
│ (LangChain)      │    │ (LangChain)         │
│                  │    │                     │
│ Outils:          │    │ Fonctions:          │
│ - list_datasets  │    │ - Génération code   │
│ - list_tables    │    │ - Visualisation     │
│ - get_schema     │    │   Plotly            │
│ - execute_sql    │    │                     │
└───┬──────────────┘    └──────┬──────────────┘
    │                          │
┌───▼────────────┐      ┌──────▼──────┐
│  Google        │      │   Plotly    │
│  BigQuery      │      │   Express   │
└────────────────┘      └─────────────┘
```

## 📦 Installation

### 1. Cloner le projet

```bash
git clone <votre-repo>
cd agent-py
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Copiez le fichier `.env.example` vers `.env` et configurez-le :

```bash
cp .env.example .env
```

Éditez `.env` selon votre cas d'usage :

#### Pour MCP (Claude Desktop) - Configuration minimale :
```env
GOOGLE_CLOUD_PROJECT_ID="votre-projet-gcp"
```

#### Pour usage direct en terminal - Choisissez votre LLM :

**Option 1 : Gemini (Google)**
```env
GOOGLE_CLOUD_PROJECT_ID="votre-projet-gcp"
LLM_PROVIDER="gemini"
GEMINI_API_KEY="votre-cle-api-gemini"
```

**Option 2 : Claude (Anthropic)**
```env
GOOGLE_CLOUD_PROJECT_ID="votre-projet-gcp"
LLM_PROVIDER="claude"
ANTHROPIC_API_KEY="votre-cle-api-claude"
```

**Option 3 : OpenAI (GPT-4)**
```env
GOOGLE_CLOUD_PROJECT_ID="votre-projet-gcp"
LLM_PROVIDER="openai"
OPENAI_API_KEY="votre-cle-api-openai"
```

**Option 4 : Ollama (Local)**
```env
GOOGLE_CLOUD_PROJECT_ID="votre-projet-gcp"
LLM_PROVIDER="ollama"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama2"
```

### 5. Authentification Google Cloud

```bash
gcloud auth application-default login
```

## 🚀 Utilisation

### Mode 1 : MCP avec Claude Desktop (Recommandé)

**Avantage :** Pas besoin de clé API LLM ! Claude Desktop utilise son propre modèle Claude.

1. Configurez Claude Desktop avec seulement `GOOGLE_CLOUD_PROJECT_ID` :

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

2. Redémarrez Claude Desktop

3. Utilisez Claude naturellement :
   - "Montre-moi le nombre de vues par vidéo dans BigQuery"
   - "Crée un graphique à barres de ces données"

**Claude utilisera automatiquement les outils MCP pour explorer BigQuery !**

### Mode 2 : Utilisation directe en terminal

Lancez le script principal interactif avec votre LLM choisi :

```bash
python main.py
```

Le système affichera le modèle utilisé :
```
🤖 Utilisation du modèle: Google Gemini Pro
```
ou
```
🤖 Utilisation du modèle: Anthropic Claude 3.5 Sonnet
```

**Exemple d'interaction :**

```
=== Agent BigQuery Intelligent ===
🤖 Utilisation du modèle: Anthropic Claude 3.5 Sonnet

Posez votre question : donne moi le nombre de vues par vidéo

--- L'agent analyse votre question et explore BigQuery ---
[L'agent liste les datasets...]
[L'agent explore les tables...]
[L'agent examine les schémas...]
[L'agent exécute la requête...]

--- Résultats de la requête ---
   video_id  video_title        views
0  v123      Introduction       15000
1  v124      Tutorial Part 1    8500
2  v125      Demo              12300

Voulez-vous visualiser ces résultats dans un tableau de bord ? (oui/non): oui

--- Création de la Visualisation ---
🤖 Utilisation du modèle: Anthropic Claude 3.5 Sonnet
[Un graphique interactif s'affiche dans votre navigateur]
```

## 🔧 Comparaison des modes

| Caractéristique | MCP (Claude Desktop) | Terminal Direct |
|----------------|----------------------|-----------------|
| **Modèle LLM** | Claude (inclus) | Configurable (Gemini, Claude, OpenAI, Ollama) |
| **Configuration** | Minimale (juste BigQuery) | Nécessite clé API LLM |
| **Interface** | Interface graphique Claude | Ligne de commande |
| **Coût** | Inclus dans Claude Desktop | Selon API choisie |
| **Flexibilité** | Limité à Claude | Choix du modèle |
| **Recommandé pour** | Utilisateurs Claude Desktop | Développeurs, scripts |

## 🛠️ Outils MCP disponibles (Claude Desktop)

Quand vous utilisez Claude Desktop, Claude a accès à 5 outils :

### `list_bigquery_datasets`
Liste tous les datasets disponibles.

### `list_bigquery_tables`
Liste les tables d'un dataset.

### `get_table_schema`
Récupère le schéma d'une table.

### `execute_bigquery_sql`
Exécute une requête SQL sur BigQuery.

### `create_plotly_visualization`
Crée une visualisation à partir des données.

**Claude les utilise automatiquement de manière intelligente !**

## 🧪 Test et débogage

### Tester le serveur MCP

```bash
python mcp_server.py
```

### Déboguer avec MCP Inspector

```bash
npx @modelcontextprotocol/inspector python mcp_server.py
```

## 📁 Structure du projet

```
agent-py/
├── main.py                      # Script principal interactif
├── mcp_server.py                # Serveur MCP (agnostique au modèle)
├── requirements.txt             # Dépendances Python
├── .env                         # Variables d'environnement (à créer)
├── .env.example                 # Exemple de configuration
├── MCP_SETUP.md                 # Guide détaillé MCP
├── README.md                    # Ce fichier
└── src/
    ├── llm_config.py            # Configuration dynamique des LLM
    ├── bigquery_agent/
    │   ├── __init__.py
    │   ├── agent.py             # Agent BigQuery (multi-LLM)
    │   └── main.py              # Exemple standalone
    └── dashboard_agent/
        ├── __init__.py
        ├── agent.py             # Agent Dashboard (multi-LLM)
        └── main.py              # Exemple standalone
```

## 🔧 Technologies utilisées

- **Python 3.12+**
- **LangChain** : Orchestration des agents
- **Google Cloud BigQuery** : Base de données
- **LLM supportés** :
  - Gemini Pro (Google)
  - Claude 3.5 Sonnet (Anthropic)
  - GPT-4 (OpenAI)
  - Llama2/Mistral (Ollama - local)
- **Plotly Express** : Visualisations interactives
- **MCP (Model Context Protocol)** : Intégration avec Claude Desktop

## 📖 Documentation détaillée

- [Configuration MCP complète](MCP_SETUP.md)

## 🤝 Compatibilité

### Clients MCP
- ✅ Claude Desktop (utilise Claude automatiquement)
- ✅ Cline/VSCode (configurable)
- ✅ Cursor (configurable)
- ✅ Tout client MCP

### LLM supportés (mode terminal)
- ✅ Google Gemini Pro
- ✅ Anthropic Claude 3.5 Sonnet
- ✅ OpenAI GPT-4
- ✅ Ollama (Llama2, Mistral, etc.)

## 📝 Exemples de questions

- "Donne moi le nombre de vues par vidéo"
- "Quels sont les top 10 clients par montant de commandes ?"
- "Montre moi les tendances de ventes par mois"
- "Liste les produits les plus vendus"
- "Analyse les performances par région"

## 🚀 Avantages de l'approche multi-LLM

✅ **Pour MCP** : Pas de coûts API supplémentaires (utilise le LLM du client)
✅ **Pour terminal** : Flexibilité totale du choix du modèle
✅ **Pas de vendor lock-in** : Changez de modèle à tout moment
✅ **Optimisation des coûts** : Utilisez Ollama localement si besoin
✅ **Meilleure performance** : Chaque modèle a ses forces

## 🐛 Troubleshooting

### Pour MCP (Claude Desktop)

**Les outils n'apparaissent pas :**
- Vérifiez le chemin absolu dans `claude_desktop_config.json`
- Redémarrez Claude Desktop
- Vérifiez que `GOOGLE_CLOUD_PROJECT_ID` est défini

### Pour usage direct en terminal

**Erreur "Provider not found" :**
```bash
# Vérifiez votre fichier .env
cat .env | grep LLM_PROVIDER
```

**Erreur "API key not found" :**
```bash
# Assurez-vous que la clé API correspondante est définie
# Pour Gemini : GEMINI_API_KEY
# Pour Claude : ANTHROPIC_API_KEY
# Pour OpenAI : OPENAI_API_KEY
```

**Erreur d'authentification BigQuery :**
```bash
gcloud auth application-default login
```

## 📄 Licence

MIT

## 👤 Auteur

Créé avec ❤️ pour faciliter l'analyse de données avec l'IA
