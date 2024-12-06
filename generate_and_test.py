import subprocess
import os
import sys

# Configuration
RUST_BINARY = (
    "./serialize_rust/target/release/serialize_rust"  # Path to the Rust executable
)
PYTHON_SCRIPT = (
    "./test_scripts/python/evaluator.py"  # Path to the Python analysis script
)
VISUALIZER = "./test_scripts/python/visualizer.py"
DATASETS_DIR = "./datasets"  # Directory where datasets will be generated
RESULTS_DIR = "serialization_test_results"  # Directory for results


# Ensure directories exist
os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


def run_rust_generator():
    """Run Rust dataset generator."""
    print(f"Generating datasets...")
    try:
        subprocess.run([RUST_BINARY], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Rust generator: {e}")
        sys.exit(1)


def verify_datasets():
    """Check if datasets were generated."""
    if not os.listdir(DATASETS_DIR):
        print("No datasets found. Rust generator may have failed.")
        sys.exit(1)
    print(f"Datasets available: {os.listdir(DATASETS_DIR)}")


def run_python_evaluator():
    """Run Python evaluator script."""
    print("Running Python evaluator...")
    try:
        subprocess.run(["python3", PYTHON_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Python evaluator: {e}")
        sys.exit(1)


def run_visualizer():
    """Run Visualizer Script"""
    print("Starting visualizer...")
    try:
        subprocess.run(["python3", VISUALIZER], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Python visualizer: {e}")
        sys.exit(1)


def main():

    run_rust_generator()
    return
    verify_datasets()
    run_python_evaluator()
    run_visualizer()

    print(f"All tasks completed. Results saved in {RESULTS_DIR}.")


if __name__ == "__main__":
    main()
