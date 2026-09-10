from __future__ import annotations

from dataclasses import dataclass, asdict
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


@dataclass
class WeChatArticle:
    url: str
    title: str
    author: str
    account_name: str
    content_html: str
    content_text: str
    images: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def validate_wechat_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("链接必须以 http:// 或 https:// 开头")
    if parsed.hostname not in {"mp.weixin.qq.com", "weixin.qq.com"}:
        raise ValueError("当前只支持微信公众号文章链接")


def parse_wechat_html(url: str, html: str) -> WeChatArticle:
    soup = BeautifulSoup(html, "html.parser")
    title_node = soup.select_one("#activity-name") or soup.find("h1")
    content_node = soup.select_one("#js_content") or soup.find("article")
    if content_node is None:
        raise ValueError("未找到公众号正文，文章可能需要登录或已失效")

    author_node = soup.select_one("#js_name") or soup.select_one(".rich_media_meta_text")
    account_node = soup.select_one("#js_name")

    for node in content_node.select("script,style,noscript"):
        node.decompose()

    images: list[str] = []
    for img in content_node.find_all("img"):
        src = img.get("data-src") or img.get("src")
        if src:
            images.append(src)
            img["src"] = src

    title = title_node.get_text(" ", strip=True) if title_node else "未命名文章"
    author = author_node.get_text(" ", strip=True) if author_node else ""
    account_name = account_node.get_text(" ", strip=True) if account_node else author
    text = content_node.get_text("\n", strip=True)

    return WeChatArticle(
        url=url,
        title=title,
        author=author,
        account_name=account_name,
        content_html=str(content_node),
        content_text=text,
        images=list(dict.fromkeys(images)),
    )


async def fetch_wechat_article(url: str) -> WeChatArticle:
    validate_wechat_url(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/152 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=20.0, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
    return parse_wechat_html(str(response.url), response.text)
