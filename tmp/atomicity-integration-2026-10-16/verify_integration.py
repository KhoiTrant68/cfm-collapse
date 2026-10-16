from pathlib import Path
from collections import Counter
import re, json, hashlib
root=Path(__file__).resolve().parents[2]
work=Path(__file__).resolve().parent
s=(root/'paper/main.tex').read_text(encoding='utf-8')
old=(work/'main.tex.before').read_text(encoding='utf-8')
blocks=lambda t:[m.group(0) for m in re.finditer(r'\\begin\{(theorem|proposition|lemma|corollary|assumption|proof)\}.*?\\end\{\1\}',t,re.S)]
assert Counter(blocks(s))==Counter(blocks(old)), 'Formal statement/proof changed'
assert hashlib.sha256((work/'main.tex.before').read_bytes()).hexdigest()=='c38aacedd1b31a9c11838a7c85244c76331357605e86286bb67bdff4db178cf4'
assert (root/'paper/math_commands.tex').read_bytes()==(work/'math_commands.tex.before').read_bytes()
labels=re.findall(r'\\label\{([^}]+)\}',s)
assert len(labels)==len(set(labels))
refs=set(re.findall(r'\\(?:ref|eqref|proofin)\{([^}]+)\}',s))-{'#1'}
assert not refs-set(labels),refs-set(labels)
bib=(root/'paper/refs.bib').read_text(encoding='utf-8')
keys=re.findall(r'@\w+\s*\{\s*([^,]+)',bib)
assert len(keys)==len(set(keys))
cites={k.strip() for x in re.findall(r'\\cite\w*(?:\[[^\]]*\])*\{([^}]+)\}',s) for k in x.split(',')}
assert not cites-set(keys),cites-set(keys)
assert '359 checks passed, 0 failed' in (work/'numbers-check.txt').read_text()
assert (root/'paper/main.tex').read_bytes()==(work/'build/main.tex').read_bytes()
log=(work/'build/main.log').read_text(errors='replace')
assert not re.search(r'undefined|Overfull|Float too large|Label\(s\)|Citation\(s\)',log)
result=dict(status='passed',formal_blocks_preserved=len(blocks(s)),labels=len(labels),cited_keys=len(cites),existing_numerical_checks=359,source_sha256=hashlib.sha256((root/'paper/main.tex').read_bytes()).hexdigest(),pdf_sha256=hashlib.sha256((work/'build/main.pdf').read_bytes()).hexdigest())
(work/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
