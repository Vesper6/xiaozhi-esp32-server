# AI智能医疗导诊系统改造指南

本项目已在 xiaozhi-esp32-server 的基础上完成【AI智能医疗导诊】场景改造：设备端参考固件 [Vesper6/xiaozhi-esp32](https://github.com/Vesper6/xiaozhi-esp32)，服务端（本仓库）将提示词、技能插件（SKILL）、MCP、知识库、交互钩子（Hooks）与管理界面全部医疗化。

> ⚠️ 重要合规声明：本系统仅提供**导诊引导**（科室推荐、就诊流程、医院信息、健康宣教），不构成医疗诊断或治疗建议。所有提示词均内置了"不诊断、不开药、急危重症立即引导急诊/120"的安全底线。上线前请结合本院实际情况和当地法规审核所有话术。

## 一、整体架构

```
[xiaozhi-esp32 导诊设备]  ←Websocket/MQTT→  [xiaozhi-server 导诊服务]
                                              ├── 提示词：agent-base-prompt.txt + 角色prompt
                                              ├── SKILL插件：recommend_department / get_hospital_info 等
                                              ├── MCP：HIS挂号、专家排班、药品信息、院内导航
                                              └── 知识库：RAGFlow 医院知识库
[manager-web 导诊管理台] → [manager-api] → MySQL（医疗导诊智能体模板）
```

## 二、提示词（Prompts）

| 位置 | 内容 |
| --- | --- |
| `main/xiaozhi-server/agent-base-prompt.txt` | 导诊基础提示词模板：导诊护士人设、`<medical_safety>` 医疗安全规则（不诊断、红旗症状急诊引导、隐私保护）、一次只问一个问题、TTS口语化约束 |
| `main/xiaozhi-server/config.yaml` 的 `prompt` | 默认角色"小安"——门诊智能导诊助手 |
| `config.yaml` 的 `system_error_response` / `end_prompt` | 系统错误提示与导诊结束语（提醒带就诊卡、祝早日康复） |
| `main/manager-api/.../db/changelog/202607261400.sql` | 智控台默认智能体模板：门诊导诊、急诊分诊、儿科导诊、体检咨询、用药咨询、健康宣教 六个医疗角色 |

使用智控台（manager-api/manager-web）部署时，新建智能体会自动使用"门诊导诊"模板；也可以在模板管理里选择其他医疗角色。

## 三、SKILL 技能插件

新增插件 `main/xiaozhi-server/plugins_func/functions/hospital_guide.py`，注册两个函数（已默认加入 `config.yaml` 的 `Intent.function_call.functions`）：

1. **recommend_department** —— 症状分诊与科室推荐
   - 内置本地分诊知识库（症状关键词 → 科室映射）
   - 内置急危重症红旗词检测（胸痛、呼吸困难、大出血、意识不清、中毒、临产等），命中后立即引导急诊/120，不再走普通导诊流程
   - 支持人群修正：儿童 → 儿科、孕妇 → 产科
2. **get_hospital_info** —— 医院信息查询
   - 门诊时间、挂号方式、医保报销、科室楼层位置、急诊位置、人工导诊台位置

医院本地数据在 `config.yaml` 的 `plugins.hospital_guide` 下配置（医院名称、22个示例科室的楼层分布、门诊时间、挂号/医保说明），请按本院实际情况修改。

另外，角色切换插件 `change_role.py` 也已医疗化，支持语音切换四种服务模式：门诊导诊 / 急诊分诊 / 健康宣教 / 用药咨询。

## 四、MCP 接入

`main/xiaozhi-server/mcp_server_settings.json` 提供了医疗场景的 MCP 服务接入示例（复制到 `data/.mcp_server_settings.json` 后修改为实际地址）：

- `his-registration`：医院 HIS 挂号系统（号源查询、预约挂号、退号改约）
- `doctor-schedule`：专家出诊排班查询
- `medicine-info`：药房位置、取药叫号、药品库存查询
- `health-checkup`：体检套餐查询与预约
- `hospital-navigation`：院内导航路线指引

MCP 接入点的开启方式参见 [mcp-endpoint-integration.md](./mcp-endpoint-integration.md)。

## 五、知识库

推荐使用 RAGFlow 建立本院医疗知识库，并开启 `search_from_ragflow` 插件（`config.yaml` 中取消注释即可）：

1. 按 [ragflow-integration.md](./ragflow-integration.md) 部署 RAGFlow 并获取 api_key、dataset_ids
2. 建议入库的资料：科室与专家介绍、出诊排班、检查检验注意事项（空腹、憋尿等）、体检套餐说明、就诊/医保流程制度、常见病健康宣教资料
3. `plugins.search_from_ragflow.description` 已改写为医疗知识库描述，大模型会在患者询问相关问题时自动检索

轻量场景无需 RAGFlow：`plugins.hospital_guide` 下的科室/流程配置本身就是一份内置的本地导诊知识库。

## 六、交互钩子（Hooks）

导诊场景相关的会话钩子均在 `config.yaml` 中配置：

- **唤醒词**：新增"你好小安"、"你好小医"（`wakeup_words`），需与固件端唤醒词配置配合，参见 [Vesper6/xiaozhi-esp32](https://github.com/Vesper6/xiaozhi-esp32) 的固件编译文档
- **开场问候**：`enable_greeting: true`，设备唤醒后自动播报问候
- **退出钩子**：`exit_commands` 新增"结束咨询"；`handle_exit_intent` 工具在患者道别时触发导诊结束语
- **结束语钩子**：`end_prompt` 会在会话结束时提醒患者带好就诊卡并祝早日康复
- **无声超时**：`close_connection_no_voice_time`（默认120秒）自动结束会话，适合导诊台公共设备的人流轮换

## 七、管理界面（UI）

- 浏览器标题/描述改为"AI智能医疗导诊管理台"（`main/manager-web/.env`）
- 登录、注册、首页欢迎语等品牌文案已医疗化（`main/manager-web/src/i18n/` 各语言文件）
- 智能体模板管理默认编码改为"小安"

## 八、上线前检查清单

- [ ] 将 `plugins.hospital_guide` 中的示例医院/科室数据替换为本院真实数据
- [ ] 审核所有提示词与模板话术是否符合本院管理规定与当地法规
- [ ] 替换 `mcp_server_settings.json` 中的占位地址为真实 MCP 服务
- [ ] 建立 RAGFlow 医院知识库并开启 `search_from_ragflow`
- [ ] 用真实设备完整走查：普通导诊、急危重症引导、儿科/孕产人群、医院信息问答
