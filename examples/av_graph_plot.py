import sys
import os
import argparse
import logging
from glob import glob

sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..", "src")))

from pabutools import election
from pb_robustness_measures.visualization.av_graph import av_graph

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def extract_metadata(pb_path, instance):
    meta = instance.meta

    voters = int(meta["num_votes"])
    projects = int(meta["num_projects"])
    budget = float(meta["budget"])

    parts = []
    for key in ("unit", "country", "instance"):
        if key in meta and meta[key]:
            parts.append(str(meta[key]))

    if parts:
        name = "_".join(parts)
    else:
        name = os.path.splitext(os.path.basename(pb_path))[0]

    return name, voters, projects, budget


def ensure_output_dir():
    out_dir = os.path.join(os.getcwd(), "res", "greedy_av", "poland")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def process_pb_file(pb_path, show_labels=False):
    logging.info(f"Processing: {pb_path}")

    instance, profile = election.parse_pabulib(pb_path)
    name, voters, projects, budget = extract_metadata(pb_path, instance)

    out_dir = ensure_output_dir()
    output_path = os.path.join(out_dir, f"{name}.png")

    av_graph(
        instance,
        profile,
        name=name,
        show_labels=show_labels,
        voters=voters,
        projects=projects,
        budget=budget,
        save_path=output_path,
    )

    logging.info(f"Saved: {output_path}")


def collect_pb_files(paths_or_dirs):
    files = []
    for p in paths_or_dirs:
        if os.path.isdir(p):
            files.extend(sorted(glob(os.path.join(p, "*.pb"))))
        elif os.path.isfile(p) and p.endswith(".pb"):
            files.append(p)
    return files


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--dir", "-d")
    parser.add_argument("--show-labels", action="store_true")
    args = parser.parse_args(argv)

    input_paths = list(args.paths)
    if args.dir:
        input_paths.append(args.dir)

    if not input_paths:
        return 2

    pb_files = collect_pb_files(input_paths)
    if not pb_files:
        return 2

    for pb_file in pb_files:
        try:
            process_pb_file(pb_file, show_labels=args.show_labels)
        except Exception as e:
            logging.exception(f"Error processing {pb_file}: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
