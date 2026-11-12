"""Write a class-balanced CIFAR-10 training subset in the zip format EDM's train.py reads
(PNG images + dataset.json with labels), and the indices into CIFAR-10 train that
scripts/n3_edm_memorization.py uses for the exact field.

Indices follow torchvision's CIFAR10(train=True) order, which is the order EDM's dataset_tool
writes (data_batch_1..5), so the public EDM model and a subset share one indexing.

    python -m scripts.make_edm_cifar_subset --cifar-root data/cifar10 --n 1000 --seed 0 --out data/edm_subsets
"""
import argparse
import io
import json
import pathlib
import zipfile

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cifar-root", default="data/cifar10")
    ap.add_argument("--n", type=int, required=True, help="total size, divisible by 10")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import torchvision
    from PIL import Image
    ds = torchvision.datasets.CIFAR10(root=a.cifar_root, train=True, download=False)
    y = np.asarray(ds.targets)
    assert a.n % 10 == 0, "--n must be divisible by 10"
    rng = np.random.default_rng(a.seed)
    idx = np.sort(np.concatenate([rng.choice(np.flatnonzero(y == c), a.n // 10, replace=False) for c in range(10)]))
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    stem = f"cifar10_sub{a.n}_s{a.seed}"
    np.save(out / f"{stem}_indices.npy", idx)
    labels = []
    with zipfile.ZipFile(out / f"{stem}.zip", "w", compression=zipfile.ZIP_STORED) as z:
        for j, i in enumerate(idx):
            name = f"{j // 1000:05d}/img{j:08d}.png"
            buf = io.BytesIO(); Image.fromarray(ds.data[i]).save(buf, format="png")
            z.writestr(name, buf.getvalue())
            labels.append([name, int(y[i])])
        z.writestr("dataset.json", json.dumps({"labels": labels}))
    print(f"wrote {out / (stem + '.zip')} and {stem}_indices.npy: {len(idx)} images, {a.n // 10} per class")


if __name__ == "__main__":
    main()
