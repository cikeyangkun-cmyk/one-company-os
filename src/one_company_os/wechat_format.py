from __future__ import annotations

from bs4 import BeautifulSoup


TEMPLATES = {
    "minimal": {
        "p": "margin:0 0 18px;line-height:1.9;font-size:16px;color:#2b2f36;letter-spacing:.2px;",
        "h2": "margin:34px 0 18px;font-size:21px;line-height:1.45;color:#111827;",
        "h3": "margin:30px 0 16px;font-size:18px;line-height:1.5;color:#111827;text-align:center;",
        "blockquote": "margin:24px 0;padding:14px 18px;border-left:3px solid #111827;background:#f7f8fa;color:#475467;line-height:1.8;",
    },
    "knowledge": {
        "p": "margin:0 0 18px;line-height:1.9;font-size:16px;color:#30343b;",
        "h2": "margin:38px 0 18px;padding-left:12px;border-left:4px solid #2563eb;font-size:21px;color:#111827;",
        "h3": "margin:30px 0 16px;font-size:18px;color:#1d4ed8;",
        "blockquote": "margin:24px 0;padding:16px 18px;border-radius:8px;background:#eff6ff;color:#334155;line-height:1.8;",
    },
    "story": {
        "p": "margin:0 0 20px;line-height:2;font-size:16px;color:#343434;",
        "h2": "margin:38px 0 20px;font-size:21px;text-align:center;color:#222;",
        "h3": "margin:32px 0 16px;font-size:18px;text-align:center;letter-spacing:1px;color:#444;",
        "blockquote": "margin:24px 0;padding:16px 20px;background:#faf7f2;color:#6b5b4b;line-height:1.9;",
    },
}


def apply_template(html: str, template: str = "minimal") -> str:
    styles = TEMPLATES.get(template)
    if styles is None:
        raise ValueError(f"未知排版模板: {template}")
    soup = BeautifulSoup(html, "html.parser")
    for tag, style in styles.items():
        for node in soup.find_all(tag):
            node["style"] = style
    for img in soup.find_all("img"):
        img["style"] = "max-width:100%;height:auto;display:block;margin:24px auto;"
    return str(soup)
