from pathlib import Path
import json

root = Path("app")


def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (root / path).write_text(content, encoding="utf-8")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise SystemExit(f"Trecho não encontrado: {label}")
    return content.replace(old, new, 1)


pkg = json.loads(read("package.json"))
pkg["version"] = "10.10.29"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html")
html = replace_once(
    html,
    'id="versionInfo" class="version-info">v10.10.28',
    'id="versionInfo" class="version-info">v10.10.29',
    "versão no cabeçalho",
)
write("public/index.html", html)

js = read("public/app.js")
js = replace_once(js, 'const atual="10.10.28"', 'const atual="10.10.29"', "versão do atualizador")
js = replace_once(
    js,
    'const url=imagemProdutoSegura101027(produto),size=tipo==="caixa"?64:40;',
    'const url=imagemProdutoSegura101027(produto),size=tipo==="caixa"?96:40;',
    "resolução da foto no Caixa",
)
write("public/app.js", js)

css = read("public/style.css") + r'''

/* 10.10.29 - duas colunas e foto grande somente no monitor antigo */
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product-grid,
body[data-monitor-profile="1024x768"] #caixa .pdv1094-service-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product:not(.pdv1094-service){grid-template-columns:92px minmax(0,1fr)!important;min-height:112px!important;padding:8px 26px 8px 8px!important;column-gap:10px!important;row-gap:3px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product:not(.pdv1094-service)>.product-thumb-caixa-101027{width:92px!important;height:92px!important;border:0!important;border-radius:7px!important;background:transparent!important;box-shadow:none!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product:not(.pdv1094-service)>.product-thumb-caixa-101027 img{width:100%!important;height:100%!important;object-fit:contain!important;border:0!important;border-radius:7px!important;background:transparent!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product:not(.pdv1094-service)>b{font-size:12.5px!important;line-height:1.22!important;-webkit-line-clamp:3;overflow-wrap:normal!important;word-break:normal!important;white-space:normal!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product:not(.pdv1094-service)>small{font-size:10.5px!important;line-height:1.2!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product:not(.pdv1094-service)>strong{font-size:14px!important;line-height:1.15!important}
'''
write("public/style.css", css)

print("10.10.29: monitor antigo com duas colunas, foto de 92 px e nomes legíveis.")
