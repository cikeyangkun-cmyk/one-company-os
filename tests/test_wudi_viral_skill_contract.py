import json
from pathlib import Path

ROOT = Path('.agents/skills/wudi-viral-script')
SCHEMA = ROOT / 'schemas/wudi-viral-script-output.schema.json'
PERSONA = ROOT / 'references/wudi-persona.md'
TRUTH = ROOT / 'references/truth-check.md'
TOPIC = ROOT / 'references/topic-angle.md'
HOOK = ROOT / 'references/hook-engine.md'
SIX = ROOT / 'references/six-part-framework.md'
DOUYIN = ROOT / 'references/douyin-rules.md'
WECHAT = ROOT / 'references/wechat-video-rules.md'
REVIEW = ROOT / 'references/viral-review.md'
SCRIPT_TEMPLATE = ROOT / 'templates/script-output.md'
SCORE_TEMPLATE = ROOT / 'templates/scoring-card.md'
SHOOT_TEMPLATE = ROOT / 'templates/shooting-card.md'
SKILL = ROOT / 'SKILL.md'
AGENT = ROOT / 'agents/openai.yaml'
FIXTURE = Path('tests/fixtures/wudi_viral_topics.json')


def test_output_schema_exists_and_has_required_top_level_fields():
    assert SCHEMA.is_file()
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    required = set(schema['required'])
    assert {'topic_analysis','angles','hooks','recommended_direction','script','douyin_version','wechat_video_version','shooting','package','viral_score','missing_material'} <= required


def test_score_schema_has_exact_100_point_weights():
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    props = schema['properties']['viral_score']['properties']
    weights = {k: props[k]['maximum'] for k in ('hook','tension','persona','authenticity','insight','spoken_language','comment_potential')}
    assert weights == {'hook':20,'tension':15,'persona':15,'authenticity':15,'insight':15,'spoken_language':10,'comment_potential':10}
    assert sum(weights.values()) == 100


def test_persona_and_truth_contract_exist_before_generation():
    assert PERSONA.is_file() and TRUTH.is_file()
    persona = PERSONA.read_text(encoding='utf-8')
    truth = TRUTH.read_text(encoding='utf-8')
    for phrase in ('先做人，再讲知识','朴实','直接','老板视角','不装专家','真人一口气'):
        assert phrase in persona
    for phrase in ('不得编造','客户','价格','销量','竞争对手','【这里需要补吴迪真实经历】','missing_material'):
        assert phrase in truth
    assert '未经来源支持' in truth
    assert ('模糊表达' in truth) or ('标记待核实' in truth)


def test_topic_angle_requires_diagnosis_and_distinct_angles():
    text = TOPIC.read_text(encoding='utf-8')
    for phrase in ('核心矛盾','目标观众','吴迪有没有资格讲','至少3个','最多5个','弱角度直接淘汰'):
        assert phrase in text
    for angle in ('行业内幕型','老板观点型','真实经历型','客户痛点型','冲突反常识型'):
        assert angle in text
    for key in ('core_conflict','target_audience','audience_interest','wudi_authority','risk'):
        assert key in text
    assert '一个核心矛盾、一个核心观点、一个核心记忆点' in text


def test_hook_engine_requires_six_three_layer_hooks_and_no_bait_switch():
    text = HOOK.read_text(encoding='utf-8')
    for phrase in ('至少6个','口播 Hook','视觉 Hook','屏幕文字 Hook','spoken','visual','screen_text','3秒','钩子承诺必须被正文兑现'):
        assert phrase in text
    for hook_type in ('冲突型','反常识型','钱型','经历型','身份权威型','内幕型','问题型','具体场景型','对比型','立场型'):
        assert hook_type in text
    assert '不要只生成一句开头' in text
    assert 'payoff' in text.lower() and '匹配' in text


def test_six_part_framework_has_exact_narrative_jobs():
    text = SIX.read_text(encoding='utf-8')
    for label in ('第一段：冲突钩子','第二段：吴迪表态','第三段：真实经历','第四段：行业信息差','第五段：吴迪观点','第六段：开放式结尾'):
        assert label in text
    for key in ('conflict_hook','stance','real_story','insight','viewpoint','ending','missing_material'):
        assert key in text
    assert '【这里需要补吴迪真实经历】' in text


def test_platform_rules_are_distinct_not_copy_paste():
    d = DOUYIN.read_text(encoding='utf-8')
    w = WECHAT.read_text(encoding='utf-8')
    for phrase in ('35–60秒','15–25秒','第一句话直接制造冲突','一个视频只解决一个问题'):
        assert phrase in d
    for phrase in ('60–120秒','更强调经历','更强调因果','价值观','不是把抖音稿逐字复制'):
        assert phrase in w
    assert d != w


def test_review_rubric_totals_100_and_never_guarantees_virality():
    text = REVIEW.read_text(encoding='utf-8')
    for row in ('hook: 20','tension: 15','persona: 15','authenticity: 15','insight: 15','spoken_language: 10','comment_potential: 10'):
        assert row in text
    for band in ('0–64','65–74','75–84','85–89','90+'):
        assert band in text
    assert 'deductions' in text and '不能写“必爆”' in text


def test_human_rendering_templates_exist():
    for path in (SCRIPT_TEMPLATE,SCORE_TEMPLATE,SHOOT_TEMPLATE):
        assert path.is_file()
    script = SCRIPT_TEMPLATE.read_text(encoding='utf-8')
    for field in ('冲突钩子','吴迪表态','真实经历','行业信息差','吴迪观点','开放式结尾'):
        assert field in script
    score = SCORE_TEMPLATE.read_text(encoding='utf-8')
    assert '扣分原因' in score and 'classification' in score
    shoot = SHOOT_TEMPLATE.read_text(encoding='utf-8')
    for field in ('opening_frame','location','camera','b_roll','subtitle_notes'):
        assert field in shoot


def test_skill_orchestrates_all_references_and_machine_output():
    text = SKILL.read_text(encoding='utf-8')
    assert text.startswith('---\nname: wudi-viral-script\n')
    for ref in ('references/wudi-persona.md','references/topic-angle.md','references/hook-engine.md','references/six-part-framework.md','references/douyin-rules.md','references/wechat-video-rules.md','references/viral-review.md','references/truth-check.md','schemas/wudi-viral-script-output.schema.json'):
        assert ref in text
    for phrase in ('source_material','platform','douyin','wechat_video','both','missing_material','JSON','one core conflict'):
        assert phrase in text
    assert '不得编造' in text and '先真实性检查，再评分' in text


def test_agent_metadata_and_all_skill_files_exist():
    assert AGENT.is_file()
    text = AGENT.read_text(encoding='utf-8')
    assert 'Wudi Viral Script' in text and 'shoot-ready' in text
    expected = [SKILL,AGENT,PERSONA,TOPIC,HOOK,SIX,DOUYIN,WECHAT,REVIEW,TRUTH,SCHEMA,SCRIPT_TEMPLATE,SCORE_TEMPLATE,SHOOT_TEMPLATE]
    assert all(path.is_file() for path in expected)


def test_skill_supports_module_level_regeneration():
    skill = SKILL.read_text(encoding='utf-8')
    for mode in ('只重写Hook','只重写某一段','重新生成角度','优化口语','更像吴迪','转视频号','转抖音'):
        assert mode in skill
    assert 'preserve untouched human-edited fields' in skill


def test_schema_uses_classification_and_exact_six_parts():
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    assert set(schema['properties']['script']['required']) == {'conflict_hook','stance','real_story','insight','viewpoint','ending'}
    score = schema['properties']['viral_score']
    assert 'classification' in score['required'] and 'classification' in score['properties']


def test_acceptance_fixture_has_ten_unique_topics_and_required_cases():
    rows = json.loads(FIXTURE.read_text(encoding='utf-8'))
    assert len(rows) == 10
    assert len({row['topic'] for row in rows}) == 10
    assert all(row['platform'] in {'douyin','wechat_video','both'} for row in rows)
    tags = {tag for row in rows for tag in row['covers']}
    assert {'price','customer_pain','industry_insight','owner_stance','missing_story','weak_topic','both_platforms'} <= tags


def test_acceptance_fixture_never_supplies_invented_story_as_expected_content():
    rows = json.loads(FIXTURE.read_text(encoding='utf-8'))
    missing_story = [row for row in rows if 'missing_story' in row['covers']]
    assert missing_story
    assert all(row.get('source_material') in (None,'') for row in missing_story)
