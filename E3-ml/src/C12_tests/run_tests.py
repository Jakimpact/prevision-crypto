"""
Fichier principal pour orchestrer tous les tests
"""
import subprocess
import sys
import os
from pathlib import Path

def run_tests(target_path=None, domain=None):
    """Lance les tests avec pytest"""
    
    test_dir = Path(__file__).parent
    
    # Configuration des variables d'environnement pour les tests
    test_env = os.environ.copy()
    test_env.update({
        "API_E3_PASSWORD": "test_password",
        "SECRET_KEY": "test_secret_key_for_jwt_signing_in_tests_only",
        "API_E3_ALGORITHM": "HS256"
    })
    
    # Détermine le chemin cible
    if target_path is None:
        target = str(test_dir)
        print("Lancement de tous les tests...")
    else:
        target = str(target_path)
        if domain:
            print(f"Lancement des tests {domain} : {target_path.name}")
        else:
            print(f"Lancement des tests : {target_path.name}")
    
    # Commande pytest simplifiée
    cmd = [sys.executable, "-m", "pytest", target, "-v"]
    
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, env=test_env, cwd=test_dir.parent.parent)
        return result.returncode
    except Exception as e:
        print(f"Erreur lors de l'exécution des tests: {e}")
        return 1

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Lance les tests du projet E3-ml")
    
    # Sélection par domaine
    domain_group = parser.add_mutually_exclusive_group()
    domain_group.add_argument(
        "--api", 
        action="store_true",
        help="Lance uniquement les tests de l'API FastAPI"
    )
    domain_group.add_argument(
        "--app", 
        action="store_true",
        help="Lance uniquement les tests de l'application Streamlit"
    )
    domain_group.add_argument(
        "--ml", 
        action="store_true",
        help="Lance uniquement les tests du pipeline ML"
    )
    
    # Sélection par type
    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument(
        "--unit", 
        action="store_true",
        help="Lance uniquement les tests unitaires"
    )
    type_group.add_argument(
        "--integration", 
        action="store_true",
        help="Lance uniquement les tests d'intégration"
    )
    
    args = parser.parse_args()
    
    test_dir = Path(__file__).parent
    
    # Détermination du domaine
    if args.api:
        domain_path = test_dir / "api"
        domain_name = "API"
    elif args.app:
        domain_path = test_dir / "app"
        domain_name = "Application Streamlit"
    elif args.ml:
        domain_path = test_dir / "ml"
        domain_name = "Pipeline ML"
    else:
        domain_path = test_dir
        domain_name = None
    
    # Détermination du type
    if args.unit:
        if domain_name:
            target_path = domain_path / "unit"
        else:
            # Tous les tests unitaires de tous les domaines
            target_path = test_dir
            cmd_extra = ["-m", "unit"]
        type_name = "unitaires"
    elif args.integration:
        if domain_name:
            target_path = domain_path / "integration"
        else:
            # Tous les tests d'intégration de tous les domaines
            target_path = test_dir
            cmd_extra = ["-m", "integration"]
        type_name = "d'intégration"
    else:
        target_path = domain_path
        type_name = None
    
    # Affichage du type de tests lancés
    if domain_name and type_name:
        print(f"=== Tests {type_name} - {domain_name} ===")
    elif domain_name:
        print(f"=== Tous les tests - {domain_name} ===")
    elif type_name:
        print(f"=== Tests {type_name} - Tous domaines ===")
    else:
        print("=== Tous les tests ===")
    
    exit_code = run_tests(target_path, domain_name)
    
    if exit_code == 0:
        print("✅ Tous les tests ont réussi!")
    else:
        print("❌ Certains tests ont échoué")
    
    sys.exit(exit_code)
