from __future__ import annotations

import os
from pathlib import Path

import httpx


SKILL_PATH = Path(__file__).resolve().parents[2] / ".agents" / "skills" / "one-company-os-hotspot-writing" / "SKILL.md"


def load_skill_text() -> str:
    try:
        return SKILL_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return """
你是一名中文内容编辑。先拆解原文事实、结构、标题钩子和情绪节奏，再基于事实重写。
要求：不虚构事实，不照抄原句，不制造不存在的引用，输出适合公众号阅读的原创稿。
""".strip()


def build_rewrite_prompt(title: str, text: str, style: str = "wechat") -> str:
    skill = load_skill_text()
    platform_rules = """
公众号适配要求：
1. 先给出一个更有点击欲望但不夸大的标题。
2. 开头 120 字内进入冲突、问题或核心观点。
3. 正文使用短段落，必要时加入 01/02/03 小标题。
4. 保留原文可核验事实，不新增无法验证的时间、金额、人物经历和结论。
5. 禁止直接复刻原文句式；整篇重新组织表达。
6. 输出纯 HTML 片段，只允许 h2/h3/p/strong/blockquote/ul/ol/li 标签。
""".strip()
    return f"""{skill}\n\n{platform_rules}\n\n原文标题：{title}\n\n原文：\n{text}\n\n请直接输出改写后的 HTML，不要解释过程。"""


async def rewrite_article(title: str, text: str, style: str = "wechat") -> dict:
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("LLM_MODEL", "gpt-5.6")
    if not api_key:
        raise RuntimeError("未配置 LLM_API_KEY / OPENAI_API_KEY")

    prompt = build_rewrite_prompt(title, text, style)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是 One Company OS 的 Writing Skill 执行器。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(f"{base_url.rstrip('/')}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    html = data["choices"][0]["message"]["content"].strip()
    return {"html": html, "model": model}
