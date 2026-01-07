import os
import sys
import csv
import yaml
from pabutools import election
from pb_robustness_measures.sampling_robustness_measure.srm import (
    plurality_sampling_robustness_measure,
)

RES_DIR = os.path.join(os.getcwd(), "res", "csv")


def ensure_res_dir():
    os.makedirs(RES_DIR, exist_ok=True)
    return RES_DIR


def normalize_instance_name(fname: str) -> str:
    # Remove extension
    name = os.path.splitext(fname)[0]
    # Replace underscores and hyphens with spaces
    name = name.replace("_", " ").replace("-", " ")
    # Capitalize each word
    name = " ".join(w.capitalize() for w in name.split())
    return name


def compute_srm_for_instance(pb_file, sample_sizes):
    print(f"\n=== Loading instance: {pb_file} ===")
    instance, profile = election.parse_pabulib(pb_file)

    results = []

    for m in sample_sizes:
        if isinstance(m, float) and 0 < m <= 1:
            m_val = max(1, int(len(profile) * m))
        else:
            m_val = m

        print(f"  Computing SRM(m={m_val}) ...")
        res = plurality_sampling_robustness_measure(
            instance,
            profile,
            target=None,
            samples=m_val,
        )

        if isinstance(res, tuple):
            frac = res[0]
        else:
            frac = res

        try:
            value = float(frac)
        except Exception:
            value = float("nan")

        print(f"     → {value}")
        results.append(value)

    return results


def run_folder(folder_path, sample_sizes):
    pb_files = sorted(f for f in os.listdir(folder_path) if f.endswith(".pb"))
    if not pb_files:
        print(f"No .pb files found inside '{folder_path}'")
        return

    print(f"Found PB files in '{folder_path}':")
    for f in pb_files:
        print("  -", f)

    srm_results = {}
    folder_name = os.path.basename(os.path.normpath(folder_path))
    for fname in pb_files:
        full_path = os.path.join(folder_path, fname)
        # Normalize instance name
        instance_name = normalize_instance_name(fname)
        srm_results[(folder_name, instance_name)] = compute_srm_for_instance(full_path, sample_sizes)

    return srm_results


def save_csv(results, folder_name, sample_sizes):
    ensure_res_dir()
    out_csv = os.path.join(RES_DIR, f"{folder_name}_srm_results.csv")
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["folder", "instance"] + sample_sizes
        writer.writerow(header)

        for (folder_name, instance_name), vals in results.items():
            writer.writerow([folder_name, instance_name] + vals)

    print(f"Saved CSV → {out_csv}")


def run_tests_for_folder(folder, sample_sizes):
    results = run_folder(folder, sample_sizes)
    if results:
        folder_name = os.path.basename(os.path.normpath(folder))
        save_csv(results, folder_name, sample_sizes)


def main():
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]

        if first_arg.endswith((".yaml", ".yml")):
            # Config file mode
            config_file = first_arg
            if not os.path.exists(config_file):
                print(f"Config file '{config_file}' does not exist.")
                return

            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            for test in config.get("tests", []):
                folder = test.get("folder")
                sample_sizes = test.get("sample_sizes", [])

                if not folder or not os.path.exists(folder):
                    print(f"Folder '{folder}' does not exist, skipping...")
                    continue

                print(f"\n=== Running SRM for folder: {folder} (from config) ===")
                run_tests_for_folder(folder, sample_sizes)

        else:
            # Folder mode with CLI parameters
            folder = first_arg
            if not os.path.exists(folder):
                print(f"Folder '{folder}' does not exist.")
                return

            try:
                sample_sizes = [float(x) if '.' in x else int(x) for x in sys.argv[2:]]
            except Exception as e:
                print(f"Error parsing sample sizes: {e}")
                return

            print(f"\n=== Running SRM for folder: {folder} (from CLI args) ===")
            run_tests_for_folder(folder, sample_sizes)

    else:
        # Default: use tests_config.yaml if no CLI args
        config_file = "tests_config.yaml"
        if not os.path.exists(config_file):
            print(f"Config file '{config_file}' not found.")
            return

        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        for test in config.get("tests", []):
            folder = test.get("folder")
            sample_sizes = test.get("sample_sizes", [])

            if not folder or not os.path.exists(folder):
                print(f"Folder '{folder}' does not exist, skipping...")
                continue

            print(f"\n=== Running SRM for folder: {folder} (from config) ===")
            run_tests_for_folder(folder, sample_sizes)


if __name__ == "__main__":
    main()
