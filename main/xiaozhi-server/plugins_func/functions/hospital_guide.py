from config.logger import setup_logging
from plugins_func.register import register_function, ToolType, ActionResponse, Action
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.connection import ConnectionHandler

TAG = __name__
logger = setup_logging()

# 急危重症红旗症状关键词，命中后优先引导急诊/120
RED_FLAG_KEYWORDS = [
    "胸痛", "胸口疼", "胸口痛", "压榨", "呼吸困难", "喘不上气", "喘不过气",
    "大出血", "出血不止", "吐血", "咯血", "便血不止",
    "意识不清", "昏迷", "昏倒", "晕倒", "叫不醒", "神志不清",
    "抽搐", "惊厥", "口吐白沫",
    "说话不清", "口齿不清", "嘴歪", "口角歪斜", "半边不能动", "偏瘫", "肢体无力",
    "中毒", "误服", "农药", "过量服药",
    "严重过敏", "全身荨麻疹", "喉头水肿",
    "车祸", "高处坠落", "严重外伤", "刀伤", "烧伤面积",
    "临产", "破水", "羊水破", "产前出血",
]

# 症状 → 推荐科室 的本地分诊知识库（作为大模型分诊的参考依据）
SYMPTOM_DEPARTMENT_MAP = {
    "呼吸内科": ["咳嗽", "咳痰", "气喘", "哮喘", "发烧", "发热", "感冒", "流鼻涕", "肺"],
    "消化内科": ["肚子疼", "腹痛", "腹泻", "拉肚子", "便秘", "胃疼", "胃痛", "反酸", "烧心", "恶心", "呕吐", "消化不良", "食欲不振"],
    "心血管内科": ["胸闷", "心慌", "心悸", "高血压", "血压高", "心脏"],
    "神经内科": ["头晕", "头疼", "头痛", "失眠", "记忆力下降", "手脚发麻", "手抖", "眩晕"],
    "内分泌科": ["糖尿病", "血糖高", "甲状腺", "肥胖", "消瘦", "多饮多尿"],
    "肾内科": ["水肿", "浮肿", "尿蛋白", "肾"],
    "普外科": ["疝气", "阑尾", "胆结石", "腹部包块", "肿块"],
    "骨科": ["骨折", "扭伤", "关节疼", "腰疼", "腰痛", "颈椎", "肩膀疼", "腿疼", "膝盖疼", "崴脚"],
    "泌尿外科": ["尿频", "尿急", "尿痛", "血尿", "肾结石", "前列腺"],
    "妇科": ["月经不调", "痛经", "白带", "妇科"],
    "产科": ["怀孕", "产检", "孕吐", "胎动"],
    "儿科": ["孩子", "宝宝", "小孩", "儿童", "婴儿"],
    "眼科": ["眼睛", "视力", "看不清", "眼红", "眼痛", "白内障", "青光眼", "麦粒肿"],
    "耳鼻咽喉科": ["耳鸣", "耳朵", "听力", "鼻塞", "流鼻血", "嗓子疼", "咽喉", "扁桃体", "鼻炎", "打呼噜"],
    "口腔科": ["牙疼", "牙痛", "蛀牙", "拔牙", "口腔溃疡", "牙龈"],
    "皮肤科": ["皮疹", "瘙痒", "过敏", "湿疹", "痘痘", "痤疮", "脱发", "荨麻疹", "皮肤"],
    "精神心理科": ["焦虑", "抑郁", "心情不好", "睡不着", "心理", "情绪低落"],
    "感染性疾病科": ["肝炎", "结核", "传染"],
}

recommend_department_function_desc = {
    "type": "function",
    "function": {
        "name": "recommend_department",
        "description": (
            "医疗导诊核心工具：根据患者描述的症状推荐就诊科室。"
            "当用户描述身体不适、询问挂什么科、看什么科室时必须调用。"
            "例如用户说'我头晕想挂号'，参数symptom为：头晕。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symptom": {
                    "type": "string",
                    "description": "患者描述的症状原文，例如：头晕、肚子疼、咳嗽三天",
                },
                "patient_group": {
                    "type": "string",
                    "description": "患者人群类型：成人/儿童/孕妇/老人，未提及则为成人",
                },
            },
            "required": ["symptom"],
        },
    },
}

get_hospital_info_function_desc = {
    "type": "function",
    "function": {
        "name": "get_hospital_info",
        "description": (
            "查询医院基础信息。当用户询问门诊时间、挂号方式、医保报销、"
            "科室位置楼层、急诊位置、导诊台位置等医院信息时调用。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "查询主题：门诊时间/挂号/医保/科室位置/急诊/导诊台/全部",
                },
                "department": {
                    "type": "string",
                    "description": "当查询科室位置时，科室名称，例如：儿科",
                },
            },
            "required": ["topic"],
        },
    },
}


def _get_guide_config(conn: "ConnectionHandler") -> dict:
    return conn.config.get("plugins", {}).get("hospital_guide", {})


def _parse_departments(config: dict):
    """解析配置中的科室列表：科室名称,楼层位置,主要接诊范围"""
    departments = []
    for item in config.get("departments", []):
        parts = str(item).split(",", 2)
        if len(parts) == 3:
            departments.append(
                {"name": parts[0].strip(), "location": parts[1].strip(), "scope": parts[2].strip()}
            )
    return departments


def _check_red_flags(symptom: str):
    return [kw for kw in RED_FLAG_KEYWORDS if kw in symptom]


@register_function(
    "recommend_department", recommend_department_function_desc, ToolType.SYSTEM_CTL
)
def recommend_department(
    conn: "ConnectionHandler", symptom: str, patient_group: str = "成人"
):
    """根据症状推荐就诊科室"""
    try:
        config = _get_guide_config(conn)
        hospital_name = config.get("hospital_name", "本院")
        departments = _parse_departments(config)
        triage_desk = config.get("triage_desk_location", "人工导诊台")

        # 急危重症优先引导急诊
        red_flags = _check_red_flags(symptom)
        if red_flags:
            emergency_phone = config.get("emergency_phone", "120")
            emergency_location = config.get("emergency_location", "急诊科")
            report = (
                f"【急危重症预警】患者症状“{symptom}”命中红旗症状：{'、'.join(red_flags)}。"
                f"请立刻、冷静地建议患者马上前往急诊（位置：{emergency_location}），"
                f"情况紧急或行动不便时拨打{emergency_phone}。"
                f"不要继续常规问诊，不要推荐普通门诊科室。"
            )
            return ActionResponse(Action.REQLLM, report, None)

        # 关键词匹配候选科室
        matched = []
        for dept_name, keywords in SYMPTOM_DEPARTMENT_MAP.items():
            hits = [kw for kw in keywords if kw in symptom]
            if hits:
                matched.append((dept_name, len(hits)))
        matched.sort(key=lambda x: x[1], reverse=True)

        # 人群修正
        group = patient_group or "成人"
        if "儿童" in group or "孩" in group:
            matched.insert(0, ("儿科", 99))
        elif "孕" in group:
            matched.insert(0, ("产科", 99))

        dept_locations = {d["name"]: d["location"] for d in departments}
        if matched:
            lines = []
            for name, _ in matched[:3]:
                location = dept_locations.get(name, "位置请咨询导诊台")
                lines.append(f"{name}（{location}）")
            candidates = "；".join(lines)
            report = (
                f"根据{hospital_name}本地分诊知识库，患者症状“{symptom}”（人群：{group}）"
                f"的候选科室为：{candidates}。"
                f"请结合症状用一两句话向患者推荐最合适的一个科室并说明位置；"
                f"如果信息不足，只追问一个最关键的问题。"
                f"提醒：你只做导诊建议，不做诊断，最终以医生判断为准。"
            )
        else:
            all_depts = "、".join(d["name"] for d in departments) if departments else "各科室"
            report = (
                f"本地分诊知识库未直接匹配到症状“{symptom}”对应的科室。"
                f"{hospital_name}现有科室：{all_depts}。"
                f"请根据医学常识从中推荐最合适的科室；实在无法判断时，"
                f"建议患者挂全科医学科或前往{triage_desk}咨询。"
            )
        return ActionResponse(Action.REQLLM, report, None)
    except Exception as e:
        logger.bind(tag=TAG).error(f"科室推荐失败: {e}")
        return ActionResponse(Action.REQLLM, "科室推荐服务暂时不可用，请建议患者前往人工导诊台咨询", None)


@register_function(
    "get_hospital_info", get_hospital_info_function_desc, ToolType.SYSTEM_CTL
)
def get_hospital_info(
    conn: "ConnectionHandler", topic: str, department: str = None
):
    """查询医院基础信息"""
    try:
        config = _get_guide_config(conn)
        hospital_name = config.get("hospital_name", "本院")
        info_map = {
            "门诊时间": config.get("outpatient_hours", "门诊时间请咨询导诊台"),
            "挂号": config.get("registration_guide", "挂号方式请咨询导诊台"),
            "医保": config.get("insurance_guide", "医保政策请咨询医保窗口"),
            "急诊": f"急诊位置：{config.get('emergency_location', '请咨询导诊台')}，急救电话：{config.get('emergency_phone', '120')}",
            "导诊台": f"人工导诊台位置：{config.get('triage_desk_location', '门诊大厅')}",
        }

        if "科室" in topic or department:
            departments = _parse_departments(config)
            if department:
                hits = [d for d in departments if department in d["name"] or d["name"] in department]
                if hits:
                    d = hits[0]
                    report = (
                        f"{hospital_name}{d['name']}位置：{d['location']}，"
                        f"主要接诊：{d['scope']}。请自然地告知患者。"
                    )
                else:
                    report = f"未找到科室“{department}”，请建议患者到{info_map['导诊台']}咨询。"
            else:
                dept_list = "；".join(f"{d['name']}在{d['location']}" for d in departments)
                report = f"{hospital_name}科室分布：{dept_list}。请挑选患者关心的内容简短回答。"
            return ActionResponse(Action.REQLLM, report, None)

        matched_info = [v for k, v in info_map.items() if k in topic]
        if not matched_info or "全部" in topic:
            matched_info = list(info_map.values())
        report = (
            f"{hospital_name}相关信息：" + "。".join(matched_info) +
            "。请根据患者的问题挑选相关内容，用简短口语化的方式回答。"
        )
        return ActionResponse(Action.REQLLM, report, None)
    except Exception as e:
        logger.bind(tag=TAG).error(f"医院信息查询失败: {e}")
        return ActionResponse(Action.REQLLM, "医院信息查询服务暂时不可用，请建议患者前往人工导诊台咨询", None)
