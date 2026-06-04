# TOOLS.md — 本地工具约定

## API 调用方式

- **唯一工具**: `exec` + `curl`
- **禁止**: `web_fetch`, `web_search`, `browser`（访问内部地址会被安全策略拦截）
- **Mock Backend 基地址**: `http://host.docker.internal:5000`

## 一步式数据管道

```bash
bash /home/node/.openclaw/workspace/chat.sh "<用户消息>"
```

封装了对 `/api/chat` 的 POST 请求，返回 identity_mode + recommendations + activities + weather。

## 辅助命令

| 任务 | 命令 |
|------|------|
| 健康检查 | `curl http://host.docker.internal:5000/health` |
| 排队监控 | `curl POST /api/queue-monitor/start` |
| 检查监控 | `curl GET /api/monitors/check-all` |
| 一键叫车 | `curl POST /api/ride-hailing` |
| 主动提醒 | `curl POST /api/proactive-check` |
| 闪惠查询 | `curl GET /api/flash-deals` |
| 待发通知 | `curl GET /api/notifications/pending` |
| 事件日志 | `curl GET /api/events?limit=3` |
| 对话记忆 | `curl POST /api/memory/save` / `curl GET /api/memory/recall` |

## 约束

- 不编造数据，所有推荐必须来自 API 返回
- 不使用"您"或"尊敬的用户"
- 不暴露 AI 身份
- 每次回复最多 1 个问题
- 推荐要么 3 个，要么不给
