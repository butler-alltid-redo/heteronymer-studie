from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def load_data(data_dir: Path) -> pd.DataFrame:
    dfs = []
    for path in sorted(data_dir.glob("heteronyms_*.csv")):
        df = pd.read_csv(path)
        df["source_file"] = path.name
        dfs.append(df)
    if not dfs:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")

    data = pd.concat(dfs, ignore_index=True)
    required = {"language", "word", "sense_id", "meaning", "ipa"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Normalize
    data["word"] = data["word"].astype(str).str.strip()
    data["language"] = data["language"].astype(str).str.strip()
    data["ipa"] = data["ipa"].astype(str).str.strip()
    return data


def plot_variant_counts(data: pd.DataFrame, outdir: Path) -> Path:
    counts = (
        data.groupby(["language", "word"], as_index=False)
        .agg(n_variants=("ipa", "nunique"), n_senses=("sense_id", "nunique"))
    )

    # Take top 20 per language (by variants then senses)
    counts = counts.sort_values(["language", "n_variants", "n_senses", "word"], ascending=[True, False, False, True])

    g = sns.catplot(
        data=counts,
        x="n_variants",
        y="word",
        col="language",
        kind="bar",
        col_wrap=2,
        height=5,
        sharey=False,
    )
    g.set_titles("{col_name}")
    g.set_axis_labels("# unika uttal (IPA)", "ord")

    for ax in g.axes.flatten():
        ax.grid(True, axis="x", alpha=0.25)

    out = outdir / "variant_counts_by_word.png"
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close("all")
    return out


def plot_ipa_length(data: pd.DataFrame, outdir: Path) -> Path:
    tmp = data.copy()
    tmp["ipa_len"] = tmp["ipa"].str.len()

    plt.figure(figsize=(9, 5))
    sns.stripplot(
        data=tmp,
        x="language",
        y="ipa_len",
        jitter=0.25,
        alpha=0.8,
    )
    sns.boxplot(
        data=tmp,
        x="language",
        y="ipa_len",
        whis=1.5,
        width=0.35,
        boxprops={"facecolor": "none"},
    )

    plt.title("Längd på IPA-strängen per språk (grovt proxy-mått)")
    plt.xlabel("språk")
    plt.ylabel("IPA-längd (tecken)")
    plt.grid(True, axis="y", alpha=0.25)

    out = outdir / "ipa_length_distribution.png"
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close("all")
    return out


def plot_word_cards(data: pd.DataFrame, outdir: Path, max_words: int = 12) -> Path:
    # A compact "card" view: each word with its IPA variants
    words = (
        data.groupby(["language", "word"], as_index=False)
        .agg(n_variants=("ipa", "nunique"))
        .sort_values(["n_variants", "language", "word"], ascending=[False, True, True])
        .head(max_words)
    )

    rows = []
    for _, r in words.iterrows():
        subset = data[(data["language"] == r["language"]) & (data["word"] == r["word"])]
        ipas = sorted(subset["ipa"].dropna().unique().tolist())
        meanings = subset[["ipa", "meaning"]].dropna().drop_duplicates().sort_values(["ipa", "meaning"])
        rows.append((r["language"], r["word"], ipas, meanings))

    # Render as a figure with text
    fig_h = max(4, 0.9 * len(rows) + 1)
    fig = plt.figure(figsize=(11, fig_h))
    ax = fig.add_subplot(111)
    ax.axis("off")

    y = 0.98
    ax.text(0.01, y, "Exempelord och uttalsvarianter", fontsize=16, weight="bold", va="top")
    y -= 0.06

    for language, word, ipas, meanings in rows:
        ax.text(0.01, y, f"[{language}] {word}", fontsize=13, weight="bold", va="top")
        y -= 0.035
        ax.text(0.03, y, " / ".join(ipas), fontsize=12, va="top")
        y -= 0.03

        for _, m in meanings.iterrows():
            ax.text(0.05, y, f"{m['ipa']}: {m['meaning']}", fontsize=10.5, va="top")
            y -= 0.025
        y -= 0.02

        if y < 0.05:
            break

    out = outdir / "word_cards.png"
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close("all")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data", type=str)
    parser.add_argument("--out-dir", default="figures", type=str)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    outdir = Path(args.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    data = load_data(data_dir)

    sns.set_theme(style="whitegrid")

    outputs = []
    outputs.append(plot_variant_counts(data, outdir))
    outputs.append(plot_ipa_length(data, outdir))
    outputs.append(plot_word_cards(data, outdir))

    print("Wrote:")
    for p in outputs:
        print(f"- {p}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
