// identity-switcher skill implementation
// 身份识别与切换逻辑

const IDENTITY_PATTERNS = {
  rescue: {
    keywords: ['急', '快', '来不及', '怎么办', '帮我', '忘了', '紧急', '马上', '立刻'],
    priority: 5,
    style: '冷静，快，直接给结果，不解释'
  },
  dater: {
    keywords: ['约会', '聚餐', '朋友', '闺蜜', '同学', '生日', '见面', '约', '请客', '聚会'],
    priority: 4,
    style: '有温度，帮对方想周全，像懂行的朋友推荐'
  },
  explorer: {
    keywords: ['想去', '没去过', '周末去哪', '打卡', '推荐', '探索', '新地方', '逛逛', '玩什么'],
    priority: 3,
    style: '像朋友推荐，带点兴奋感，结合天气和状态'
  },
  commuter: {
    keywords: ['上班', '地铁', '赶时间', '堵车', '早饭', '到家', '下班', '通勤', '路上', '公交'],
    priority: 2,
    style: '简洁直接，不废话，30字内给结论'
  },
  solo: {
    keywords: ['一个人', '宅', '不想动', '夜宵', '累了', '躺着', '失眠', '无聊', '发呆'],
    priority: 1,
    style: '轻松陪伴，不打扰，治愈感'
  }
};

function detectIdentity(userMessage) {
  const message = userMessage.toLowerCase();
  let detectedMode = 'solo'; // 默认独处状态
  let maxPriority = 0;

  // 关键词匹配
  for (const [mode, config] of Object.entries(IDENTITY_PATTERNS)) {
    const matched = config.keywords.some(keyword => message.includes(keyword));
    if (matched && config.priority > maxPriority) {
      detectedMode = mode;
      maxPriority = config.priority;
    }
  }

  return {
    identity_mode: detectedMode,
    style_hint: IDENTITY_PATTERNS[detectedMode].style,
    confidence: maxPriority > 0 ? 'high' : 'low'
  };
}

module.exports = { detectIdentity, IDENTITY_PATTERNS };
