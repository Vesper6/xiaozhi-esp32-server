from plugins_func.register import register_function, ToolType, ActionResponse, Action
from config.logger import setup_logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.connection import ConnectionHandler

TAG = __name__
logger = setup_logging()

prompts = {
    "门诊导诊": """我是{{assistant_name}}，医院门诊的智能导诊助手，像一位经验丰富、和蔼可亲的导诊护士。
我的任务是：根据您描述的症状推荐合适的就诊科室，介绍挂号、缴费、取药等就诊流程，指引科室位置。
我一次只问一个问题，说话简短、通俗、温和。
我不是医生，不做诊断、不推荐用药；如果出现胸痛、呼吸困难、大出血、意识不清等危急情况，我会第一时间建议去急诊或拨打120。""",
    "急诊分诊": """我是{{assistant_name}}，急诊分诊引导助手，说话冷静、简洁、有条理。
我的任务是：快速了解患者的主要症状和发生时间，判断是否属于急危重症，并引导家属保持冷静、配合分诊。
遇到剧烈胸痛、呼吸困难、大出血、意识不清、抽搐、中毒、严重外伤等情况，我会立刻引导直接进入急诊抢救流程或拨打120，不做多余的寒暄。
我不是医生，不做最终诊断，一切以急诊医护人员的判断为准。""",
    "健康宣教": """我是{{assistant_name}}，健康宣教助手，像一位亲切的社区健康讲师。
我的任务是：用通俗易懂的语言讲解常见慢病（高血压、糖尿病等）的日常管理、体检注意事项、饮食运动建议等健康知识。
我讲内容时会分小段，先讲重点，再问您要不要继续听。
我提供的是一般性健康知识，不能代替医生的诊疗意见；涉及具体病情，我会建议您到相应科室就诊。""",
    "用药咨询": """我是{{assistant_name}}，用药咨询引导助手，说话严谨又耐心。
我的任务是：讲解取药流程、常见的用药常识（如饭前饭后服用的一般含义、漏服的一般处理原则），提醒按医嘱和药品说明书用药。
我绝不推荐具体药品、不调整剂量、不判断药物相互作用，这些请咨询药师窗口或医生。
遇到疑似药物过敏或用药后严重不适，我会立即建议去急诊或拨打120。""",
}
change_role_function_desc = {
    "type": "function",
    "function": {
        "name": "change_role",
        "description": "当用户想切换导诊服务模式/助手角色时调用,可选的角色有：[门诊导诊,急诊分诊,健康宣教,用药咨询]",
        "parameters": {
            "type": "object",
            "properties": {
                "role_name": {"type": "string", "description": "要切换的角色名字"},
                "role": {"type": "string", "description": "要切换的角色的职业"},
            },
            "required": ["role", "role_name"],
        },
    },
}


@register_function("change_role", change_role_function_desc, ToolType.CHANGE_SYS_PROMPT)
def change_role(conn: "ConnectionHandler", role: str, role_name: str):
    """切换角色"""
    if role not in prompts:
        return ActionResponse(
            action=Action.RESPONSE, result="切换角色失败", response="不支持的角色"
        )
    new_prompt = prompts[role].replace("{{assistant_name}}", role_name)
    conn.change_system_prompt(new_prompt)
    logger.bind(tag=TAG).info(f"准备切换角色:{role},角色名字:{role_name}")
    res = f"切换角色成功,我是{role}{role_name}"
    return ActionResponse(action=Action.RESPONSE, result="切换角色已处理", response=res)
