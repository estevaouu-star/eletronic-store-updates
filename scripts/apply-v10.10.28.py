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
pkg["version"] = "10.10.28"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html")
html = replace_once(
    html,
    'id="versionInfo" class="version-info">v10.10.27',
    'id="versionInfo" class="version-info">v10.10.28',
    "versão no cabeçalho",
)
write("public/index.html", html)

js = read("public/app.js")
js = replace_once(js, 'const atual="10.10.27"', 'const atual="10.10.28"', "versão do atualizador")
js = replace_once(
    js,
    'const url=imagemProdutoSegura101027(produto),size=tipo==="caixa"?46:40;',
    'const url=imagemProdutoSegura101027(produto),size=tipo==="caixa"?64:40;',
    "tamanho intrínseco da foto no Caixa",
)
write("public/app.js", js)

css = read("public/style.css") + r'''

/* 10.10.28 - cartão horizontal com foto legível no monitor compacto */
#caixa .pdv1094-product:not(.pdv1094-service){display:grid!important;grid-template-columns:64px minmax(0,1fr)!important;grid-template-rows:auto auto auto!important;align-content:center!important;justify-content:stretch!important;column-gap:9px!important;row-gap:2px!important;min-height:88px!important;padding:7px 24px 7px 7px!important}
#caixa .pdv1094-product:not(.pdv1094-service)>.product-thumb-caixa-101027{grid-column:1!important;grid-row:1/-1!important;align-self:center!important;width:64px!important;height:64px!important;margin:0!important;border:0!important;border-radius:6px!important;background:transparent!important;box-shadow:none!important}
#caixa .pdv1094-product:not(.pdv1094-service)>.product-thumb-caixa-101027 img{width:100%!important;height:100%!important;object-fit:contain!important;background:transparent!important;border:0!important;border-radius:6px!important}
#caixa .pdv1094-product:not(.pdv1094-service)>.product-thumb-caixa-101027 .product-thumb-fallback-101027{font-size:20px!important;opacity:.38}
#caixa .pdv1094-product:not(.pdv1094-service)>b,#caixa .pdv1094-product:not(.pdv1094-service)>small,#caixa .pdv1094-product:not(.pdv1094-service)>strong{grid-column:2!important;min-width:0!important;margin:0!important;text-align:left!important}
#caixa .pdv1094-product:not(.pdv1094-service)>b{display:-webkit-box!important;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden!important;font-size:11px!important;line-height:1.18!important}
#caixa .pdv1094-product:not(.pdv1094-service)>small{overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important;font-size:9px!important}
#caixa .pdv1094-product:not(.pdv1094-service)>strong{font-size:12px!important;line-height:1.1!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product:not(.pdv1094-service){grid-template-columns:58px minmax(0,1fr)!important;min-height:80px!important;padding:6px 22px 6px 6px!important;column-gap:7px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product:not(.pdv1094-service)>.product-thumb-caixa-101027{width:58px!important;height:58px!important;border:0!important;border-radius:5px!important;background:transparent!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product:not(.pdv1094-service)>.product-thumb-caixa-101027 img{border-radius:5px!important;background:transparent!important}
'''
write("public/style.css", css)

print("10.10.28: foto maior à esquerda, textos à direita e moldura clara removida.")
