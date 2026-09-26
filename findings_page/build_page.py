"""Put out/page_data.json into template.html -> out/findings.html, the page
to publish (one file: text, styles, chart code and data).

    .venv\\Scripts\\python findings_page\\build_page.py
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"

data = json.loads((OUT / "page_data.json").read_text(encoding="utf-8"))
# The data sits inside a <script> tag, where a "<" could end it early.
blob = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("<", "\\u003c")
tpl = (HERE / "template.html").read_text(encoding="utf-8")
assert tpl.count("__DATA__") == 1
page = tpl.replace("__DATA__", blob)
(OUT / "findings.html").write_text(page, encoding="utf-8", newline="\n")
print(f"{OUT / 'findings.html'}: {len(page.encode('utf-8')):,} bytes")
