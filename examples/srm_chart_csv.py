import os
import sys
import csv
import yaml
import matplotlib.pyplot as plt

DEFAULT_CONFIG = "plot_srm_config.yaml"
OUT_DIR_DEFAULT = os.path.join("res", "srm")


def ensure_out_dir(folder):
    os.makedirs(folder, exist_ok=True)
    return folder


def plot_csv(csv_file, figsize=(10, 6), dpi=300, out_dir=OUT_DIR_DEFAULT):
    ensure_out_dir(out_dir)

    with open(csv_file, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Detect if CSV has folder + instance columns
    header = rows[0]
    if header[0].lower() in ("folder", "dir") and header[1].lower() == "instance":
        sample_sizes = [float(x) if '.' in x else int(x) for x in header[2:]]
        instances = [row[1].replace("_", " ").replace("-", " ").title() for row in rows[1:]]
        values = [[float(v) for v in row[2:]] for row in rows[1:]]
    else:
        # old format fallback
        sample_sizes = [float(x) if '.' in x else int(x) for x in header[1:]]
        instances = [row[0].replace("_", " ").replace("-", " ").title() for row in rows[1:]]
        values = [[float(v) for v in row[1:]] for row in rows[1:]]

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    for inst_name, vals in zip(instances, values):
        xs, ys = zip(*sorted(zip(sample_sizes, vals)))  # ensure left-to-right
        ax.plot(xs, ys, marker="o", label=inst_name)

    ax.set_xlabel("Number of Samples", fontsize=14)
    ax.set_ylabel("SRM Probability", fontsize=14)
    ax.grid(True)

    # Legend on top
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=2, fontsize=10)

    plt.tight_layout()
    out_file = os.path.join(out_dir, os.path.basename(csv_file).replace(".csv", "_plot.png"))
    plt.savefig(out_file, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"Saved SRM plot → {out_file}")


def main():
    # Case 1: CSV file(s) given in CLI args
    csv_args = [arg for arg in sys.argv[1:] if arg.endswith(".csv")]
    config_arg = None
    for arg in sys.argv[1:]:
        if arg.endswith(".yaml") or arg.endswith(".yml"):
            config_arg = arg

    if csv_args:
        for csv_file in csv_args:
            if not os.path.exists(csv_file):
                print(f"CSV file '{csv_file}' does not exist, skipping...")
                continue
            plot_csv(csv_file)
        return

    # Case 2: Config file
    config_file = config_arg if config_arg else DEFAULT_CONFIG
    if not os.path.exists(config_file):
        print(f"Config file '{config_file}' not found and no CSV provided.")
        print("Usage: python plot_srm.py <csv_file1> <csv_file2> ...")
        return

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    for plot_cfg in config.get("plots", []):
        csv_file = plot_cfg.get("csv_file")
        figsize = tuple(plot_cfg.get("figsize", [10, 6]))
        dpi = plot_cfg.get("dpi", 300)
        out_dir = plot_cfg.get("output_folder", OUT_DIR_DEFAULT)

        if not os.path.exists(csv_file):
            print(f"CSV file '{csv_file}' not found, skipping...")
            continue

        print(f"\nPlotting {csv_file} → {out_dir} with figsize={figsize}, dpi={dpi}")
        plot_csv(csv_file, figsize=figsize, dpi=dpi, out_dir=out_dir)


if __name__ == "__main__":
    main()
