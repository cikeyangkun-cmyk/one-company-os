from __future__ import annotations

import os

import httpx


TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
DRAFT_ADD_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"


class WeChatConnector:
    def __init__(self, app_id: str | None = None, app_secret: str | None = None):
        self.app_id = app_id or os.getenv("WECHAT_APP_ID")
        self.app_secret = app_secret or os.getenv("WECHAT_APP_SECRET")
        if not self.app_id or not self.app_secret:
            raise RuntimeError("未配置 WECHAT_APP_ID / WECHAT_APP_SECRET")

    async def get_access_token(self) -> str:
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret,
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(TOKEN_URL, params=params)
            response.raise_for_status()
            data = response.json()
        if "access_token" not in data:
            raise RuntimeError(f"获取公众号 access_token 失败: {data}")
        return data["access_token"]

    async def push_draft(
        self,
        *,
        title: str,
        author: str,
        digest: str,
        content_html: str,
        thumb_media_id: str,
        source_url: str = "",
    ) -> dict:
        token = await self.get_access_token()
        payload = {
            "articles": [
                {
                    "title": title,
                    "author": author,
                    "digest": digest,
                    "content": content_html,
                    "content_source_url": source_url,
                    "thumb_media_id": thumb_media_id,
                    "need_open_comment": 1,
                    "only_fans_can_comment": 0,
                }
            ]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(DRAFT_ADD_URL, params={"access_token": token}, json=payload)
            response.raise_for_status()
            data = response.json()
        if data.get("errcode", 0) != 0:
            raise RuntimeError(f"推送公众号草稿失败: {data}")
        return data
