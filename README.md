# Éclaire

Site pour lire des essais cliniques en langage courant. On y cherche une fiche, on filtre celles qui ont des résultats, et on ouvre la vulgarisation : de quoi il s’agit, pour qui, comment se déroule la participation, et ce qu’il faut demander à son médecin.

Les textes sont dans une base Neon Postgres. Le serveur local ne fait que les lire. Lancer le site ne modifie pas la base et ne la recrée pas.

## Installation

Il faut Python 3.11 ou plus récent, et une connexion Internet. La base est distante. Les polices et les styles de la page sont aussi chargés depuis Internet.

Le dossier reçu doit contenir `.env`, avec l’adresse de lecture seule `DATABASE_URL`. Ne pas y placer d’adresse d’écriture, et ne pas copier un dossier `.venv` venant d’une autre machine.

Sur Linux ou macOS, depuis ce dossier :

```bash
./serve.sh
```

Le script crée un environnement virtuel au premier lancement, installe la dépendance (`psycopg`), puis démarre le site. Si `python3 -m venv` échoue sur Ubuntu :

```bash
sudo apt install python3 python3-venv
```

Sous Windows, dans PowerShell, depuis ce dossier :

```powershell
py -3 -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python serve.py
```

Ouvrir ensuite http://127.0.0.1:8765. Le serveur n’écoute que sur cette machine. L’arrêter avec Ctrl+C.
