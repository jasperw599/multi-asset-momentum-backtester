import subprocess
import sys


ANALYSES = [
    "src.analytics.performance",
    "src.analytics.robustness",
    "src.analytics.cost_sensitivity",
    "src.analytics.volatility_floor_sensitivity",
    "src.analytics.out_of_sample",
    "src.analytics.regime_analysis",
    "src.analytics.selection_bias",
    "src.analytics.walk_forward",
]


def run_module(module):
    print("\n" + "=" * 70)
    print(f"Running {module}")
    print("=" * 70)

    subprocess.run(
        [sys.executable, "-m", module],
        check=True,
    )


def main():
    for module in ANALYSES:
        run_module(module)

    print("\n" + "=" * 70)
    print("All analyses completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()