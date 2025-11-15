# System Metrics Dashboard

Un tableau de bord professionnel pour visualiser les métriques système en temps réel (CPU, RAM, Disque, Réseau) avec exportation HTML interactive et PNG statique.

## Caractéristiques

- 📊 **Visualisations interactives** avec Altair (Vega-Lite)
- 📈 **4 métriques système** : CPU, RAM, Disque, Réseau
- 🎨 **Grille 2×2** avec statistiques (Moyenne, Max, Min)
- 💾 **Export multi-format** : HTML (interactif) et PNG (haute résolution)
- 🏗️ **Architecture modulaire** : séparation données/visualisation/orchestration
- 🔍 **Typage complet** : annotations de type Python 3.9+
- 📖 **Documentation PEP 257** : docstrings complètes

## Installation

### Prérequis

- Python 3.9+
- `uv` (gestionnaire de paquets ultrafast pour Python)

### Étapes

```bash
# Cloner le dépôt
git clone git@github.com:alexdjetic/lib_graphe_python.git
cd lib_graphe_python

# Les dépendances sont gérées automatiquement par uv
```

## Dépendances

- **altair** (≥6.0.0) - Visualisations Vega-Lite
- **pandas** (≥2.3.3) - Manipulation de données
- **numpy** (≥2.0.2) - Opérations numériques
- **polars** (≥1.35.2) - DataFrames haute performance
- **vl-convert-python** (≥1.1.0) - Export PNG/SVG

## Utilisation

### Exécution rapide

```bash
# Générer le rapport avec données synthétiques
uv run main.py
```

Cela créera :
- `cpu_usage_report.html` - Rapport interactif
- `cpu_usage_report.png` - Capture PNG haute résolution

### Utilisation dans le code

```python
from data_generator import generate_fake_data
from chart_generator import SystemMetricsChart

# Générer des données synthétiques (200 points, 1 par heure)
data = generate_fake_data(n=200)

# Créer le générateur de graphiques
chart_gen = SystemMetricsChart(data)

# Sauvegarder les rapports
chart_gen.save_report(
    html_path='mon_rapport.html',
    png_path='mon_rapport.png'
)

# Afficher les statistiques
chart_gen.print_statistics()
```

## Structure du projet

```
lib_graphe_python/
├── main.py                 # Point d'entrée principal
├── chart_generator.py      # Classe SystemMetricsChart (visualisations)
├── data_generator.py       # Fonction generate_fake_data()
├── pyproject.toml          # Configuration et dépendances
├── README.md              # Cette documentation
└── .gitignore             # Fichiers à ignorer
```

## Modules

### `data_generator.py`

Génère des données synthétiques de métriques système.

**Fonction principale :**
```python
def generate_fake_data(n: int = 200) -> pd.DataFrame
```

**Paramètres :**
- `n` : Nombre d'échantillons (1 par heure)

**Retour :**
DataFrame pandas avec colonnes : `timestamp`, `cpu_usage`, `ram_usage`, `disk_usage`, `network_usage`

**Distributions :**
- CPU: moyenne=50%, écart-type=15
- RAM: moyenne=65%, écart-type=12
- Disque: moyenne=45%, écart-type=10
- Réseau: moyenne=55%, écart-type=20

### `chart_generator.py`

Classe `SystemMetricsChart` pour la création des visualisations.

**Méthodes principales :**

- `__init__(data: pd.DataFrame)` - Initialise avec validation des données
- `create_full_report() -> alt.VConcatChart` - Génère le rapport complet 2×2
- `save_report(html_path: str, png_path: str)` - Exporte HTML et PNG
- `print_statistics()` - Affiche tableau des statistiques

**Configuration des métriques :**
```python
metrics = {
    'CPU': {'col': 'cpu_usage', 'color': '#1f77b4'},
    'RAM': {'col': 'ram_usage', 'color': '#2ca02c'},
    'Disk': {'col': 'disk_usage', 'color': '#ff7f0e'},
    'Network': {'col': 'network_usage', 'color': '#d62728'}
}
```

### `main.py`

Orchestration du pipeline complet :
1. Génération de 200 points de données
2. Création du rapport
3. Sauvegarde (HTML + PNG)
4. Affichage des statistiques

## Sorties

### Format HTML
- Graphiques interactifs (zoom, pan, info-bulles)
- Taille : ~1900×1080px
- Responsive et autonome

### Format PNG
- Image statique haute résolution
- Facteur d'échelle : 2x
- Idéal pour présentation/rapports

## Architecture

### Séparation des responsabilités

```
data_generator.py          → Logique métier (données)
       ↓
chart_generator.py        → Visualisation (Altair)
       ↓
main.py                   → Orchestration
```

### Typage complet

Tous les fichiers utilisent :
- Annotations de type Python 3.9+ (`Optional[T]` au lieu de `T | None`)
- Docstrings PEP 257 pour toutes les fonctions/classes/méthodes
- Types explicites pour tous les variables

## Exemples de sortie

```
✓ Saved HTML: cpu_usage_report.html
✓ Saved PNG: cpu_usage_report.png

Statistics:
  CPU      - Mean:   51.3%, Max:   87.0%, Min:    2.3%
  RAM      - Mean:   63.3%, Max:   91.5%, Min:   43.5%
  Disk     - Mean:   45.1%, Max:   68.9%, Min:   19.4%
  Network  - Mean:   55.2%, Max:  100.0%, Min:    4.7%
```

## Personnalisation

### Modifier les données d'entrée

```python
from data_generator import generate_fake_data
import pandas as pd

# Utiliser vos propres données
df = pd.DataFrame({
    'timestamp': pd.date_range('2025-01-01', periods=100, freq='h'),
    'cpu_usage': [45, 52, 48, ...],
    'ram_usage': [60, 65, 70, ...],
    'disk_usage': [40, 41, 42, ...],
    'network_usage': [50, 55, 52, ...]
})
```

### Modifier les couleurs

```python
from chart_generator import SystemMetricsChart

data = generate_fake_data()
chart_gen = SystemMetricsChart(data)

# Mettre à jour les couleurs
chart_gen.metrics['CPU']['color'] = '#FF0000'  # Rouge
chart_gen.metrics['RAM']['color'] = '#00FF00'  # Vert
```

## Dépannage

### Erreur d'export PNG

Assurez-vous que `vl-convert` est correctement installé :
```bash
uv pip install --upgrade vl-convert-python
```

### Colonnes manquantes

Vérifiez que votre DataFrame contient :
- `timestamp` (datetime)
- `cpu_usage`, `ram_usage`, `disk_usage`, `network_usage` (float)

## Développement

### Exécuter les tests

```bash
# À implémenter
uv run pytest
```

### Formater le code

```bash
black .
flake8 .
```

## Licence

MIT

## Auteur

Alexandre Djetic

## Contributions

Les contributions sont bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commiter vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request
