from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl

from .wechat_article import fetch_wechat_article
from .wechat_connector import WeChatConnector
from .wechat_format import apply_template
from .writing_engine import rewrite_article


app = FastAPI(title="One Company OS Web API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:8787"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_INDEX = Path(__file__).resolve().parents[2] / "web" / "index.html"


class ImportRequest(BaseModel):
    url: HttpUrl


class RewriteRequest(BaseModel):
    title: str
    text: str
    style: str = "wechat"


class FormatRequest(BaseModel):
    html: str
    template: str = "minimal"


class DraftRequest(BaseModel):
    title: str
    author: str = ""
    digest: str = ""
    content_html: str
    thumb_media_id: str
    source_url: str = ""


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "service": "one-company-os-web", "version": "0.2.0"}


@app.post("/api/wechat/import")
async def import_wechat(req: ImportRequest) -> dict:
    try:
        article = await fetch_wechat_article(str(req.url))
        return article.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/writing/rewrite")
async def rewrite(req: RewriteRequest) -> dict:
    if len(req.text.strip()) < 50:
        raise HTTPException(status_code=400, detail="原文内容过短")
    try:
        return await rewrite_article(req.title, req.text, req.style)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Writing Skill 调用失败: {exc}") from exc


@app.post("/api/wechat/format")
def format_wechat(req: FormatRequest) -> dict:
    try:
        return {"html": apply_template(req.html, req.template), "template": req.template}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/wechat/draft")
async def push_draft(req: DraftRequest) -> dict:
    try:
        connector = WeChatConnector()
        return await connector.push_draft(
            title=req.title,
            author=req.author,
            digest=req.digest,
            content_html=req.content_html,
            thumb_media_id=req.thumb_media_id,
            source_url=req.source_url,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"公众号接口调用失败: {exc}") from exc


@app.get("/")
def index():
    if WEB_INDEX.exists():
        return FileResponse(WEB_INDEX)
    return {"message": "One Company OS API is running"}


def run() -> None:
    import uvicorn

    uvicorn.run("one_company_os.web_api:app", host="127.0.0.1", port=8787, reload=True)
