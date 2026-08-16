from pathlib import Path
p=Path('scripts/apply-v10.6.py')
s=p.read_text(encoding='utf-8')
s=s.replace("marker='''<main class=\"content\">'''", "marker='''<main'''")
p.write_text(s,encoding='utf-8')
print('Patch 10.6 preparado para localizar a tag <main> independentemente das classes.')
