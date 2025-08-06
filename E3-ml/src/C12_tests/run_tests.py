"""
Fichier principal pour orchestrer tous les tests
"""
import subprocess
import sys
import os
from pathlib import Path

def run_tests(target_path=None):
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
    
    parser = argparse.ArgumentParser(description="Lance les tests de l'API")
    parser.add_argument(
        "--unit", 
        action="store_true",
        help="Lance uniquement les tests unitaires"
    )
    parser.add_argument(
        "--integration", 
        action="store_true",
        help="Lance uniquement les tests d'intégration"
    )
    
    args = parser.parse_args()
    
    test_dir = Path(__file__).parent
    
    if args.unit:
        target_path = test_dir / "unit"
        exit_code = run_tests(target_path)
    elif args.integration:
        target_path = test_dir / "integration"
        exit_code = run_tests(target_path)
    else:
        exit_code = run_tests()  # Tous les tests
    
    if exit_code == 0:
        print("Tous les tests ont réussi!")
    else:
        print("Certains tests ont échoué")
    
    sys.exit(exit_code)
