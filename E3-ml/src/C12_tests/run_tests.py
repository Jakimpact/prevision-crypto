"""
Fichier principal pour orchestrer tous les tests
"""
import subprocess
import sys
import os
from pathlib import Path

def run_tests(target_path=None, domain=None, extra_pytest_args=None):
    """Lance les tests avec pytest (support sélection domaines/types et couverture)."""

    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent  # E3-ml/

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
            print(f"Lancement des tests {domain} : {Path(target).name}")
        else:
            print(f"Lancement des tests : {Path(target).name}")

    cmd = [sys.executable, "-m", "pytest", target, "-v"]
    if extra_pytest_args:
        cmd.extend(extra_pytest_args)

    print("-" * 50)
    print("Commande:", " ".join(cmd))

    try:
        result = subprocess.run(cmd, env=test_env, cwd=project_root)
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

    # Couverture
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Active la mesure de couverture (pytest-cov)"
    )
    parser.add_argument(
        "--fail-under",
        type=int,
        default=None,
        help="Échoue si la couverture globale est sous ce pourcentage"
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
    
    # Détermination du type + préparation arguments pytest supplémentaires
    extra_args = []
    if args.unit:
        if domain_name:
            target_path = domain_path / "unit"
        else:
            target_path = test_dir
            extra_args.extend(["-m", "unit"])
        type_name = "unitaires"
    elif args.integration:
        if domain_name:
            target_path = domain_path / "integration"
        else:
            target_path = test_dir
            extra_args.extend(["-m", "integration"])
        type_name = "d'intégration"
    else:
        target_path = domain_path
        type_name = None

    # Couverture : si --coverage on ajoute options pytest-cov
    if getattr(args, "coverage", False):
        # Utilise configuration .coveragerc (source=src). Ajout rapports.
        extra_args.extend([
            "--cov=src",
            "--cov-report=term-missing:skip-covered",
            "--cov-report=xml",
            "--cov-report=html"
        ])
        if args.fail_under is not None:
            extra_args.append(f"--cov-fail-under={args.fail_under}")
    
    # Affichage du type de tests lancés
    if domain_name and type_name:
        print(f"=== Tests {type_name} - {domain_name} ===")
    elif domain_name:
        print(f"=== Tous les tests - {domain_name} ===")
    elif type_name:
        print(f"=== Tests {type_name} - Tous domaines ===")
    else:
        print("=== Tous les tests ===")
    
    exit_code = run_tests(target_path, domain_name, extra_pytest_args=extra_args)
    
    if exit_code == 0:
        print("✅ Tous les tests ont réussi!")
    else:
        print("❌ Certains tests ont échoué")
    
    sys.exit(exit_code)

    
