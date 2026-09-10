# One Company OS · 公众号 Web V1

当前分支：`feature/wechat-web-v1`

## 已实现

- 公众号公开文章链接解析：标题、作者/公众号名、正文、图片 URL
- Writing Skill 适配层：读取仓库现有 `.agents/skills/one-company-os-hotspot-writing/SKILL.md`
- OpenAI-compatible LLM 接口调用，模型、Base URL、API Key 全部由环境变量配置
- 三套公众号排版模板：极简深度 / 知识读书 / 故事情绪
- 微信手机端实时预览
- 浏览器本地草稿保存
- 微信公众号 `draft/add` 草稿箱连接器
- FastAPI Web API

## 本地运行

```bash
git checkout feature/wechat-web-v1
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

配置模型：

```bash
export LLM_API_KEY='你的模型 API Key'
export LLM_BASE_URL='OpenAI-compatible API Base URL'
export LLM_MODEL='你的模型名称'
```

如果需要推送公众号草稿箱，再配置：

```bash
export WECHAT_APP_ID='公众号 AppID'
export WECHAT_APP_SECRET='公众号 AppSecret'
```

启动：

```bash
one-company-os-web
```

然后浏览器打开：

```text
http://127.0.0.1:8787
```

## 当前工作流

```text
公众号 URL
  ↓
POST /api/wechat/import
  ↓
解析标题 / 正文 / 图片
  ↓
POST /api/writing/rewrite
  ↓
Writing Skill + LLM
  ↓
POST /api/wechat/format
  ↓
公众号 HTML 排版
  ↓
手机预览 / 人工编辑
  ↓
POST /api/wechat/draft
  ↓
公众号后台草稿箱
```

## 公众号草稿箱注意事项

微信草稿接口需要公众号本身具备相应开发接口权限。当前 V1 需要手动提供已经上传到公众号素材系统的 `thumb_media_id` 作为封面图。下一版会补：封面上传、正文图片重新托管、公众号账号配置页和发布记录。

## 下一阶段

1. 增加图片上传与微信图片 URL 替换
2. 增加公众号账号管理页，不让用户手工输入环境变量
3. 将 Writing Skill 从“热点写作 Skill + 公众号规则”升级为独立的公众号写作 Skill
4. 增加文章历史、素材库入库、版本回滚
5. 部署测试站点并绑定测试域名
