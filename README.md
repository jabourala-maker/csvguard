# csvguard

`csvguard` is a small, dependency-free command-line tool for checking CSV files before they enter a data pipeline.

This workspace also contains five independent data utilities, each with its own README and tests:

- `jsonlstats` summarizes JSON Lines files.
- `schema-diff` compares CSV schemas.
- `category-drift` compares categorical distributions between snapshots.
- `pipeline-health` evaluates synthetic pipeline run logs.
- `text-normalizer` normalizes text locally for repeatable matching.

It reports missing values, duplicate rows, and columns whose values cannot be interpreted consistently as a simple type. The output is JSON so it can be consumed by CI jobs or other scripts.

## Usage

```bash
python -m csvguard data.csv --required customer_id,amount
```

The command exits with status `1` when a problem is found and `0` when the file passes the requested checks.

## Development

```bash
python -m unittest discover -s tests -v
```

This project uses only the Python standard library. Contributions that improve validation messages, add focused checks, or improve documentation are welcome.
