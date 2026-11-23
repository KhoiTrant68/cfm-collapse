"""Convert the URW Nimbus Sans OpenType (CFF) fonts to TrueType for matplotlib.

matplotlib embeds fonts in PDFs as Type 42 (pdf.fonttype = 42) only from TrueType outlines; with
the CFF-based Nimbus Sans OTF it writes a mismatched font that poppler flags. This writes TrueType
copies, renamed to the family "Nimbus Sans TT", into the directory given (default
/mnt/data/khoitm8/cache/fonts), which scripts/figstyle.py registers if it exists.

Usage: python scripts/make_tt_fonts.py [out_dir]
"""
import sys
from pathlib import Path

from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable

SRC = Path("/usr/share/fonts/opentype/urw-base35")
STYLES = ("Regular", "Bold", "Italic", "BoldItalic")
FAMILY = "Nimbus Sans TT"


def otf_to_ttf(src: Path, dst: Path, style: str) -> None:
    font = TTFont(src)
    gs = font.getGlyphSet()
    glyf = newTable("glyf"); glyf.glyphOrder = font.getGlyphOrder(); glyf.glyphs = {}
    for name in font.getGlyphOrder():
        pen = TTGlyphPen(gs)
        gs[name].draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=True))
        glyf[name] = pen.glyph()
    font["loca"] = newTable("loca"); font["glyf"] = glyf
    del font["CFF "]
    if "VORG" in font:
        del font["VORG"]
    font.sfntVersion = "\x00\x01\x00\x00"
    font["maxp"].tableVersion = 0x00010000
    for attr in ("maxZones", "maxTwilightPoints", "maxStorage", "maxFunctionDefs",
                 "maxInstructionDefs", "maxStackElements", "maxSizeOfInstructions",
                 "maxComponentElements", "maxPoints", "maxContours", "maxCompositePoints",
                 "maxCompositeContours", "maxComponentDepth"):
        setattr(font["maxp"], attr, 0)
    font["maxp"].maxZones = 1
    font["head"].glyphDataFormat = 0
    font["post"].formatType = 2.0
    font["post"].extraNames = []; font["post"].mapping = {}
    font["post"].glyphOrder = font.getGlyphOrder()
    sub = "Regular" if style == "Regular" else {"Bold": "Bold", "Italic": "Italic", "BoldItalic": "Bold Italic"}[style]
    for rec in font["name"].names:
        if rec.nameID in (1, 16):
            rec.string = FAMILY
        elif rec.nameID == 4:
            rec.string = f"{FAMILY} {sub}"
        elif rec.nameID == 6:
            rec.string = f"NimbusSansTT-{style}"
    font.save(dst)


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/data/khoitm8/cache/fonts")
    out.mkdir(parents=True, exist_ok=True)
    for st in STYLES:
        otf_to_ttf(SRC / f"NimbusSans-{st}.otf", out / f"NimbusSansTT-{st}.ttf", st)
        print("wrote", out / f"NimbusSansTT-{st}.ttf")


if __name__ == "__main__":
    main()
