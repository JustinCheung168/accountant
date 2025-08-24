#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path

from accounting.analyst import Analyst
from accounting.spec import Specification

def main():
    parser = argparse.ArgumentParser(
        description="Generate accounting reports according to a specification file."
    )

    parser.add_argument("spec", type=str, help="Path to a specification (in `specs/`) to generate a report based on.")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    spec_path = Path(args.spec)
    if not spec_path.exists():
        raise FileNotFoundError(f"Could not find spec file {spec_path}")

    spec = Specification(spec_path)
    analyst = Analyst(spec)
    analyst.run_analysis()

if __name__ == "__main__":
    main()