"""Highlight four new rendered entries after BibTeX; leave metadata/style intact."""
from pathlib import Path
import re
p=Path(__file__).parent.parent/'revised_v1/manuscript.bbl'
s=p.read_text()
for key in ['revWavelet','revWinter','revSTA','revCrossPollutant']:
 pattern=r'(\\bibitem[^\n]*\{'+key+r'\}\n)(.*?)(?=\n\n|\n\\end\{thebibliography\})'
 def highlight(m):
  text=m.group(2)
  if text.startswith('\\rev{'):return m.group(0)
  head,doi=text.rsplit('\\doi{',1)
  # BibTeX capitalization braces are no longer needed in rendered prose.
  head=re.sub(r'\\natexlab\{([ab])\}',r'\1',head).replace('{','').replace('}','').strip()
  return m.group(1)+'\\rev{'+head+'} '+'\\colorbox{yellow}{\\strut\\doi{'+doi.strip()+'}'
 s,n=re.subn(pattern,highlight,s,flags=re.S)
 assert n==1,(key,n)
p.write_text(s)
print('Four added bibliography entries highlighted.')
