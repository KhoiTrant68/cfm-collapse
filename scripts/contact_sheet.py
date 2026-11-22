"""Tile rendered PDF pages (p-*.png from pdftoppm) into one image, for a quick layout check.

Usage: python contact_sheet.py <dir> <out.png> <first_page> <last_page> [cols]
"""
import glob
import sys

from PIL import Image

d, out, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 4
files = sorted(glob.glob(d + "/p-*.png"))[a - 1 : b]
ims = [Image.open(f) for f in files]
w, h = ims[0].size
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (w * cols, h * rows), "white")
for i, im in enumerate(ims):
    sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(out)
