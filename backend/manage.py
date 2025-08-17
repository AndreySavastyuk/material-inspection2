#!/usr/bin/env python
"""
Скрипт управления проектом Metal Inspection System
"""
import os
import sys
import subprocess
from pathlib import Path


# Цвета для консоли
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 50}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 50}{Colors.ENDC}\n")


def run_command(command, description=None):
    """Выполнение команды с выводом"""
    if description:
        print(f"{Colors.OKCYAN}▶ {description}{Colors.ENDC}")

    print(f"{Colors.OKBLUE}  Running: {command}{Colors.ENDC}")
    result = subprocess.run(command, shell=True)

    if result.returncode == 0:
        print(f"{Colors.OKGREEN}  ✓ Success{Colors.ENDC}\n")
    else:
        print(f"{Colors.FAIL}  ✗ Failed{Colors.ENDC}\n")
        sys.exit(1)

    return result.returncode


def main():
    print_header("Metal Inspection System - Management Tool")

    commands = {
        "1": ("init-db", "Initialize database (create tables)"),
        "2": ("migrate", "Create new migration"),
        "3": ("upgrade", "Apply migrations"),
        "4": ("downgrade", "Rollback last migration"),
        "5": ("run", "Run development server"),
        "6": ("test", "Run tests"),
        "7": ("clean", "Clean temporary files"),
        "8": ("seed", "Seed database with test data"),
        "9": ("shell", "Open Python shell with app context"),
        "0": ("exit", "Exit")
    }

    # Показываем меню
    print("Available commands:")
    for key, (cmd, desc) in commands.items():
        print(f"  {Colors.BOLD}{key}{Colors.ENDC}. {desc}")

    choice = input(f"\n{Colors.WARNING}Select command (0-9): {Colors.ENDC}")

    if choice == "1":
        # Инициализация БД
        print_header("Initializing Database")
        run_command(
            "python scripts/init_db.py --sync",
            "Creating database tables"
        )

    elif choice == "2":
        # Создание миграции
        print_header("Creating Migration")
        message = input(f"{Colors.WARNING}Enter migration message: {Colors.ENDC}")
        run_command(
            f'alembic revision --autogenerate -m "{message}"',
            "Generating migration"
        )

    elif choice == "3":
        # Применение миграций
        print_header("Applying Migrations")
        run_command(
            "alembic upgrade head",
            "Upgrading database"
        )

    elif choice == "4":
        # Откат миграции
        print_header("Rolling Back Migration")
        run_command(
            "alembic downgrade -1",
            "Rolling back last migration"
        )

    elif choice == "5":
        # Запуск сервера
        print_header("Starting Development Server")
        print(f"{Colors.OKGREEN}Server will start at: http://localhost:8000{Colors.ENDC}")
        print(f"{Colors.OKGREEN}API Docs: http://localhost:8000/api/docs{Colors.ENDC}\n")
        run_command(
            "uvicorn src.main:app --reload --host 0.0.0.0 --port 8000",
            "Starting FastAPI server"
        )

    elif choice == "6":
        # Запуск тестов
        print_header("Running Tests")
        run_command(
            "pytest -v",
            "Running pytest"
        )

    elif choice == "7":
        # Очистка
        print_header("Cleaning Temporary Files")
        run_command(
            "find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true",
            "Removing __pycache__"
        )
        run_command(
            "find . -name '*.pyc' -delete 2>/dev/null || true",
            "Removing .pyc files"
        )
        print(f"{Colors.OKGREEN}Cleanup complete!{Colors.ENDC}")

    elif choice == "8":
        # Seed данные
        print_header("Seeding Database")
        print(f"{Colors.WARNING}This feature will be implemented soon{Colors.ENDC}")
        # run_command("python scripts/seed_db.py", "Seeding test data")

    elif choice == "9":
        # Python shell
        print_header("Python Shell")
        print(f"{Colors.OKCYAN}Opening interactive Python shell with app context...{Colors.ENDC}")
        os.system(
            "python -i -c 'from src.main import app; from src.core.database import *; from src.models import *; print(\"App context loaded!\")'")

    elif choice == "0":
        print(f"\n{Colors.OKGREEN}Goodbye!{Colors.ENDC}")
        sys.exit(0)

    else:
        print(f"{Colors.FAIL}Invalid choice!{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    # Проверяем, что мы в правильной директории
    if not Path("src").exists():
        print(f"{Colors.FAIL}Error: Please run this script from the backend directory{Colors.ENDC}")
        sys.exit(1)

    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
        sys.exit(0)