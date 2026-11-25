"""Historical entry point for the CIFAR handoff audit. Run from the repository root."""
from pathlib import Path
from runpy import run_path

if __name__ == "__main__":
    run_path(str(Path(__file__).resolve().parents[3] / "scripts/audit_cifar_handoffs.py"), run_name="__main__")
