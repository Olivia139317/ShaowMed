# ShadowMe 随影

身份感知城市生活管家，面向美团 2026 AI Hackathon 命题赛道 01：基于 OpenClaw 的本地生活「全天候私人管家」。

## 项目亮点

- **身份感知**：LiHua 根据用户状态自动切换 commuter、dater、explorer、rescue、solo 五种模式。
- **三场景闭环**：餐饮推荐、排队监控、出行叫车、娱乐活动和天气/路况联动。
- **7x24 自主协同**：OpenClaw heartbeat 每分钟检查排队、闪惠、通知、天气和主动提醒。
- **动态沙盒**：Flask mock backend 持续生成 14 类随机事件，数据不是静态 JSON。
- **隐私合规**：用户画像为模拟数据或用户显式输入，只保存短期偏好关键词，不采集真实隐私。

## 架构

```text
Telegram/WebChat -> OpenClaw Gateway -> LiHua Agent
                                      -> exec + chat.sh
                                      -> Flask Mock Backend :5000
                                      -> restaurants / activities / weather / traffic / queue monitor
```

## 目录

- `agents/main/SOUL.md`：LiHua 人设、工作流和约束规则。
- `agents/main/agent.json`：Agent 配置和 5 个 Skill。
- `agents/main/skills/`：OpenClaw Skill 文档和对应实现。
- `mock-backend/server.py`：动态 mock 后端，23 个接口。
- `demo/demo-script.md`：7 个演示场景。
- `demo/test-cases.md`：功能、集成、沙盒和主动提醒测试用例。
- `docs/submission/`：比赛提交材料草稿。

## 快速启动

Windows PowerShell:

```powershell
.\scripts\start-backend.ps1
```

Linux/macOS:

```bash
sh scripts/start-backend.sh
```

手动启动:

```bash
cd mock-backend
python -m pip install -r requirements.txt
python server.py
```

## 验证

启动后运行 smoke test。

Windows PowerShell:

```powershell
.\scripts\smoke-test.ps1
```

Linux/macOS:

```bash
sh scripts/smoke-test.sh
```

核心接口:

- `GET /health`
- `POST /api/chat`
- `POST /api/queue-monitor/start`
- `GET /api/monitors/check-all`
- `POST /api/ride-hailing`
- `POST /api/proactive-check`
- `POST /api/proactive-feedback`
- `GET /api/sandbox/status`

## OpenClaw 部署

1. 在 `openclaw.json` 中填入 DeepSeek API Key 和 Telegram Bot Token。
2. 按 `AGENTS.md` 中的 Docker 部署命令同步 `agents/main`、`openclaw.json` 和 `chat.sh`。
3. 启动 mock backend，确认 `http://localhost:5000/health` 返回 `version: 2.2.5`。
4. 重启 OpenClaw 容器并通过 WebChat 或 Telegram 验证。

## 提交表单建议

截图中的表单字段可参考 `docs/submission/SUBMISSION_FORM.md`。

## 比赛提交材料

实名提交材料不放入公开仓库。公开仓库仅保留可运行工程代码、演示脚本和复现说明。
