# ShadowMe (随影) - Test Cases

## 测试用例设计

### 1. 身份识别测试

#### 测试用例 1.1: 通勤状态识别
```
输入: "上班快迟到了"
期望输出:
  - identity_mode: commuter
  - style_hint: 简洁直接，不废话，30字内给结论
  - 推荐: 距离<500m, 出餐<15分钟
```

#### 测试用例 1.2: 约聚状态识别
```
输入: "周末约朋友吃饭"
期望输出:
  - identity_mode: dater
  - style_hint: 有温度，帮对方想周全
  - 推荐: 评分>4.5, 有包间, 环境好
```

#### 测试用例 1.3: 独处状态识别
```
输入: "一个人在家不想动"
期望输出:
  - identity_mode: solo
  - style_hint: 轻松陪伴，不打扰，治愈感
  - 推荐: 一人食友好, 可外卖, 舒适
```

#### 测试用例 1.4: 探索状态识别
```
输入: "周末想去没去过的地方"
期望输出:
  - identity_mode: explorer
  - style_hint: 像朋友推荐，带点兴奋感
  - 推荐: 特色店铺, 新开业, 结合天气
```

#### 测试用例 1.5: 急救状态识别
```
输入: "急！现在哪里还营业"
期望输出:
  - identity_mode: rescue
  - style_hint: 冷静，快，直接给结果
  - 推荐: 最近, 确定营业, 立刻可达
```

#### 测试用例 1.6: 优先级测试
```
输入: "急！约朋友吃饭来不及了"
期望输出:
  - identity_mode: rescue (优先级最高)
  - 不是 dater
```

### 2. 推荐逻辑测试

#### 测试用例 2.1: 通勤模式推荐
```
场景: 早上8点，用户在地铁站
输入: "地铁口有啥能吃的"
期望输出:
  - 推荐1: 云南米线 (150m, 8分钟)
  - 推荐2: 老张烧饼 (200m, 5分钟)
  - 不推荐: 花间堂 (800m, 30分钟准备)
```

#### 测试用例 2.2: 约聚模式推荐
```
场景: 周五晚上，约朋友
输入: "找个安静的地方聚餐"
期望输出:
  - 推荐1: 花间堂私房菜 (4.8分, 有包间)
  - 推荐2: 山间野味 (4.9分, 艺术氛围)
  - 不推荐: 老张烧饼 (快餐, 不适合聚会)
```

#### 测试用例 2.3: 独处模式推荐
```
场景: 深夜23点，一个人
输入: "有点饿但不想出门"
期望输出:
  - 推荐1: 深夜食堂 (营业到凌晨2点, 可外卖)
  - 推荐2: 24小时便利餐厅 (300m, 24小时)
  - 不推荐: 花间堂 (已关门)
```

#### 测试用例 2.4: 探索模式推荐
```
场景: 周末，天气晴朗
输入: "想去新地方玩"
期望输出:
  - 推荐1: 山间野味 (新开业, 网红店)
  - 推荐2: 798艺术区 (特色, 适合拍照)
  - 结合天气: "今天天气不错，适合..."
```

#### 测试用例 2.5: 急救模式推荐
```
场景: 任意时间，紧急
输入: "急！现在哪里能吃饭"
期望输出:
  - 推荐1: 24小时便利餐厅 (300m, 确定营业)
  - 推荐2: 云南米线 (150m, 营业中)
  - 只考虑距离和营业状态
```

### 3. 主动提醒测试

#### 测试用例 3.1: 常规提醒
```
场景: 工作日 11:30
期望输出:
  - should_notify: true
  - notification_type: routine_reminder
  - message: "快到午饭时间了"
```

#### 测试用例 3.2: 天气提醒
```
场景: 下午有雨，用户未带伞
期望输出:
  - should_notify: true
  - notification_type: weather_alert
  - message: "下午有雨，记得带伞"
  - priority: high
```

#### 测试用例 3.3: 周末建议
```
场景: 周五 17:00
期望输出:
  - should_notify: true
  - notification_type: proactive_suggestion
  - message: "周五了，周末想去哪玩？"
```

#### 测试用例 3.4: 静默时段
```
场景: 凌晨 2:00
期望输出:
  - should_notify: false
  - reason: quiet_hours
```

#### 测试用例 3.5: 每日限制
```
场景: 已发送3次提醒
期望输出:
  - should_notify: false
  - reason: daily_limit
```

#### 测试用例 3.6: 用户忙碌
```
场景: 用户处于rescue模式
状态: 服务端已实现（/api/proactive-check 返回 user_busy）
期望输出:
  - should_notify: false
  - reason: user_busy
```

#### 测试用例 3.7: 拒绝冷却
```
场景: 用户12小时前拒绝了周末建议
状态: 服务端已实现（/api/proactive-feedback 记录拒绝，24小时内 /api/proactive-check 返回 recently_rejected）
期望输出:
  - should_notify: false
  - reason: recently_rejected
```

### 4. 回复风格测试

#### 测试用例 4.1: 通勤风格
```
输入: "上班路上吃啥"
期望风格:
  - 字数: ≤30字
  - 格式: 直接给结论
  - 示例: "云南米线，A口50米，8分钟。"
```

#### 测试用例 4.2: 约聚风格
```
输入: "约朋友吃饭"
期望风格:
  - 字数: 适中
  - 格式: 详细介绍
  - 示例: "推荐花间堂私房菜，环境安静雅致，有包间可预订..."
```

#### 测试用例 4.3: 独处风格
```
输入: "一个人有点饿"
期望风格:
  - 语气: 温暖陪伴
  - 格式: 理解情绪
  - 示例: "深夜食堂小酒馆，治愈系，一人食很舒服。"
```

#### 测试用例 4.4: 探索风格
```
输入: "周末去哪玩"
期望风格:
  - 语气: 带点兴奋
  - 格式: 结合天气
  - 示例: "今天天气不错，推荐798艺术区..."
```

#### 测试用例 4.5: 急救风格
```
输入: "急！哪里能吃饭"
期望风格:
  - 字数: 极简
  - 格式: 直接答案
  - 示例: "24小时便利餐厅，300米，现在营业。"
```

### 5. 边界情况测试

#### 测试用例 5.1: 模糊输入
```
输入: "吃饭"
期望输出:
  - 根据时间判断状态
  - 早上8点 → 通勤模式
  - 晚上8点 → 独处模式
```

#### 测试用例 5.2: 多重意图
```
输入: "想找个安静的地方一个人吃饭"
期望输出:
  - identity_mode: solo (独处优先)
  - 推荐: 安静 + 一人食友好
```

#### 测试用例 5.3: 无匹配结果
```
输入: "想吃法国菜"
期望输出:
  - 诚实告知: "附近没找到法国菜，推荐其他的吗？"
  - 不编造数据
```

#### 测试用例 5.4: 用户偏好冲突
```
场景: 用户不吃香菜，但推荐的店主打香菜
期望输出:
  - 过滤掉该店
  - 或标注: "这家店香菜比较多，可以要求不加"
```

#### 测试用例 5.5: 实时信息过期
```
场景: 推荐的店已关门
期望输出:
  - 检查营业状态
  - 只推荐营业中的店
  - 或标注: "明天营业"
```

### 6. 用户画像测试

#### 测试用例 6.1: 记住偏好
```
第一次: "我不吃香菜"
第二次: "推荐川菜"
期望输出:
  - 推荐的川菜店不含香菜
  - 或标注可以不加香菜
```

#### 测试用例 6.2: 记住常去地点
```
用户多次去花间堂
期望输出:
  - 识别为常去地点
  - 有优惠时主动提醒
```

#### 测试用例 6.3: 学习消费习惯
```
用户多次选择人均100-150的店
期望输出:
  - 优先推荐该价位
  - 不推荐过贵或过便宜的
```

### 7. 性能测试

#### 测试用例 7.1: 响应时间
```
要求: 身份识别 < 100ms
要求: 推荐生成 < 500ms
要求: 总响应时间 < 1s
```

#### 测试用例 7.2: 并发处理
```
场景: 100个用户同时请求
期望: 所有请求正常响应
期望: 响应时间不超过2s
```

#### 测试用例 7.3: 数据量测试
```
场景: 1000+餐厅数据
期望: 筛选和排序正常
期望: 响应时间不明显增加
```

### 8. 集成测试

#### 测试用例 8.1: 完整流程
```
1. 用户输入 → 身份识别
2. 身份识别 → 推荐引擎
3. 推荐引擎 → API调用
4. API调用 → 结果筛选
5. 结果筛选 → 风格转换
6. 风格转换 → 用户输出
```

#### 测试用例 8.2: 多轮对话
```
第1轮: "推荐餐厅" → 给出推荐
第2轮: "第一个太远了" → 调整推荐
第3轮: "有没有便宜点的" → 再次调整
```

#### 测试用例 8.3: 状态切换
```
早上8点: 通勤模式 → 简洁推荐
晚上8点: 独处模式 → 温暖推荐
同一用户，不同时间，不同风格
```

## 测试执行计划

### 阶段1: 单元测试 (1天)
- [ ] 身份识别准确性
- [ ] 推荐逻辑正确性
- [ ] 主动提醒触发条件

### 阶段2: 集成测试 (1天)
- [ ] 完整流程测试
- [ ] 多轮对话测试
- [ ] 状态切换测试

### 阶段3: 用户测试 (1天)
- [ ] 5-10个真实用户
- [ ] 收集反馈
- [ ] 优化调整

### 阶段4: 压力测试 (半天)
- [ ] 并发测试
- [ ] 性能测试
- [ ] 稳定性测试

## 测试通过标准

### 功能性
- [ ] 身份识别准确率 > 85%
- [ ] 推荐相关性 > 80%
- [ ] 主动提醒准确性 > 90%

### 性能
- [ ] 响应时间 < 1s
- [ ] 并发支持 > 100
- [ ] 系统稳定性 > 99%

### 用户体验
- [ ] 用户满意度 > 4.0/5.0
- [ ] 推荐接受率 > 60%
- [ ] 主动提醒接受率 > 40%

## 后续优化方向

### 可继续增强的方向
1. 身份识别在模糊输入时准确率下降
2. 主动提醒时机需要更多用户数据优化
3. 多轮对话的上下文保持有待加强

### 优化计划
1. 增加更多训练数据提升识别准确率
2. 引入用户反馈机制持续优化
3. 增强上下文记忆能力

---

## v2.0 新增测试 (End-to-End + Activities + Pipeline)

### 8. 活动推荐测试

#### 测试用例 8.1: Explorer 模式活动推荐
```
输入: "周末想去没去过的地方"
期望输出:
  - /api/chat 返回包含 activities 字段（≤2个）
  - 活动含 name, category, distance, price, highlight
  - 活动根据天气适宜度筛选
```

#### 测试用例 8.2: Dater 模式活动推荐
```
输入: "约朋友周末聚一下"
期望输出:
  - activities 偏向娱乐/艺术类别
  - 活动 features 包含 group/team/photography
  - 评分 ≥ 4.3
```

#### 测试用例 8.3: Solo 模式活动推荐
```
输入: "一个人想找个安静的地方待着"
期望输出:
  - activities 偏向文化/休闲/购物类别
  - 安静、单人友好
```

#### 测试用例 8.4: Commuter/Rescue 模式无活动
```
输入: "快迟到了"
期望输出:
  - activities 字段为空数组 []
  - 原因: 赶时间不需要活动推荐
```

### 9. 7x24 自主协同管道测试

#### 测试用例 9.1: 完整监控管道
```
步骤:
1. 用户: "帮我盯着海底捞中关村店，排到5桌叫我"
2. 调用 POST /api/queue-monitor/start → 获取 task_id，当前 >5 桌
3. 等待沙盒降低排队数（或手动修改）
4. 调用 GET /api/monitors/check-all → any_triggered: true
5. LiHua 主动提醒用户
6. 用户: "帮我叫车"
7. 调用 POST /api/ride-hailing → 返回司机信息 + 路况 + 预估价格

验证:
- task_id 正确创建
- 排队数变化能被检测到
- any_triggered 正确标记
- 叫车接口返回完整信息
```

#### 测试用例 9.2: Heartbeat Push 验证
```
场景: 用户有活跃的排队监控
curl -s http://host.docker.internal:5000/api/monitors/check-all

期望返回:
{
  "any_triggered": false/true,
  "monitors": [...],
  "triggered": [...]
}

如果 any_triggered 为 true，triggered 列表中的每个条目都有:
- restaurant_name
- current_count
- target_count
- task_id
```

#### 测试用例 9.3: 闪惠推送链路
```
场景: 沙盒生成闪惠事件

步骤:
1. 等待或触发 flash_deal 事件
2. curl /api/flash-deals → 获取活跃闪惠
3. heartbeat 检测到闪惠 → 推送用户

验证:
- /api/flash-deals 返回折扣信息（restaurant, discount, deal_price, expires_in_minutes）
- heartbeat 能正确识别活跃闪惠
```

### 10. 动态沙盒事件验证

#### 测试用例 10.1: 所有事件类型覆盖
```
访问: GET /api/sandbox/status

验证的指标:
- restaurants: 16 家，检查 open_status, queue_count, wait_time
- activities: 10 项，检查 crowd_level
- weather: temperature, condition, humidity
- traffic: condition, delay_minutes, congested_areas
- flash_deals: 活跃数量
- events: 最近事件日志

访问: GET /api/events?limit=20

验证事件类型覆盖:
- peak_surge, sudden_full, sudden_empty
- flash_deal, closure, reopen
- activity_full, activity_discount  ← v2.1 new
- traffic, traffic_surge  ← v2.1 new
- rain_start, rain_stop, weather_clear  ← v2.1 new
- temp_change
```

#### 测试用例 10.2: 路况感知叫车
```
步骤:
1. 触发 traffic_surge 事件（等待或模拟）
2. 用户: "帮我叫车去XX"
3. 调用 POST /api/ride-hailing

验证:
- 返回包含 traffic_condition 和 delay_minutes
- 推荐绕行路线或替代出行方式（地铁）
```

### 11. Proactive Scheduler 自动化测试

#### 测试用例 11.1: 定时提醒触发
```
curl -s -X POST http://host.docker.internal:5000/api/proactive-check \
  -H "Content-Type: application/json" \
  -d '{"hour":7,"weekday":2}'

期望: should_notify: true, type: routine_reminder (早餐提醒)
```

#### 测试用例 11.2: 静默时段
```
curl -s -X POST http://host.docker.internal:5000/api/proactive-check \
  -H "Content-Type: application/json" \
  -d '{"hour":2,"weekday":2}'

期望: should_notify: false, reason: quiet_hours
```

#### 测试用例 11.3: 每日上限
```
curl -s -X POST http://host.docker.internal:5000/api/proactive-check \
  -H "Content-Type: application/json" \
  -d '{"hour":12,"weekday":2}'

期望: should_notify: false, reason: daily_limit
```

### 12. 全流程集成测试 (v2.0 Smoke Test)

```bash
# 1. Health check
curl http://localhost:5000/health

# 2. One-shot chat (identity + restaurants + activities + weather)
curl -s -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"周末想和朋友出去玩，有什么推荐"}' | python -m json.tool

# 3. Verify activities field present
curl -s -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"周末想和朋友出去玩，有什么推荐"}' | python -c "import sys,json; d=json.load(sys.stdin); print('activities:', len(d['data'].get('activities',[])))"

# 4. Start queue monitor
curl -s -X POST http://localhost:5000/api/queue-monitor/start \
  -H "Content-Type: application/json" \
  -d '{"restaurant_name":"海底捞","target_count":5}'

# 5. Check all monitors
curl -s http://localhost:5000/api/monitors/check-all

# 6. Flash deals
curl -s http://localhost:5000/api/flash-deals

# 7. Traffic
curl -s http://localhost:5000/api/traffic

# 8. Sandbox status
curl -s http://localhost:5000/api/sandbox/status | python -c "import sys,json; d=json.load(sys.stdin); print('Events:', len(d['data']['recent_events']), 'Flash deals:', d['data']['active_flash_deals'])"

# 9. Events log
curl -s "http://localhost:5000/api/events?limit=10" | python -c "import sys,json; d=json.load(sys.stdin); [print(e['type'], e['message'][:60]) for e in d['data']]"
```
