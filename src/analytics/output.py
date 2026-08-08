from src.config import PROJECT_ROOT


TABLE_DIR = PROJECT_ROOT / "results" / "tables"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def save_table(dataframe, filename):
    path = TABLE_DIR / filename

    dataframe.to_csv(
        path,
        index=False,
    )

    print(f"Saved: {path}")