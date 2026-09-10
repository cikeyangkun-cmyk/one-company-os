from one_company_os.wechat_article import parse_wechat_html, validate_wechat_url
from one_company_os.wechat_format import apply_template


def test_validate_wechat_url_accepts_public_article():
    validate_wechat_url("https://mp.weixin.qq.com/s/example")


def test_validate_wechat_url_rejects_other_hosts():
    try:
        validate_wechat_url("https://example.com/post")
    except ValueError as exc:
        assert "微信公众号" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_parse_wechat_html_extracts_article_fields():
    html = """
    <html><body>
      <h1 id="activity-name">测试标题</h1>
      <span id="js_name">测试公众号</span>
      <div id="js_content">
        <p>第一段正文</p>
        <img data-src="https://mmbiz.qpic.cn/test.jpg" />
      </div>
    </body></html>
    """
    article = parse_wechat_html("https://mp.weixin.qq.com/s/example", html)
    assert article.title == "测试标题"
    assert article.account_name == "测试公众号"
    assert "第一段正文" in article.content_text
    assert article.images == ["https://mmbiz.qpic.cn/test.jpg"]


def test_apply_template_adds_inline_wechat_styles():
    result = apply_template("<h3>01 标题</h3><p>正文</p>", "knowledge")
    assert "border-left:4px solid #2563eb" not in result
    assert "color:#1d4ed8" in result
    assert "line-height:1.9" in result
