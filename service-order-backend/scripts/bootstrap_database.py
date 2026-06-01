import os
import subprocess
import sys

from dotenv import load_dotenv

load_dotenv()


def run_command(command: list[str], label: str) -> None:
    print(f"Running {label}...")
    subprocess.run(command, check=True)


def main() -> int:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    python_executable = sys.executable

    run_command([python_executable, "-m", "alembic", "upgrade", "head"], "migrations")
    run_command([python_executable, os.path.join(project_root, "scripts", "seed_demo_data.py")], "seeds")

    print("Database bootstrap completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())