# Mock Backend Server
# ShadowMe (随影) - 模拟美团API数据服务
# 为 OpenClaw Skills 提供动态数据

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import sys
import threading
import time
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_json_file(filename):
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"FATAL: Failed to load {filepath}: {e}")
        sys.exit(1)

DB = {
    'restaurants': load_json_file('restaurants.json')['restaurants'],
    'activities': load_json_file('activities.json')['activities'],
    'weather': load_json_file('weather.json')['weather']
}

# --- Identity Detection (from identity-switcher logic) ---
IDENTITY_PATTERNS = {
    'rescue': {
        'keywords': ['急', '快', '来不及', '怎么办', '帮我', '忘了', '紧急', '马上', '立刻'],
        'priority': 5,
        'style': '冷静，快，直接给结果，不解释'
    },
    'dater': {
        'keywords': ['约会', '聚餐', '朋友', '闺蜜', '同学', '生日', '见面', '约', '请客', '聚会'],
        'priority': 4,
        'style': '有温度，帮对方想周全，像懂行的朋友推荐'
    },
    'explorer': {
        'keywords': ['想去', '没去过', '周末去哪', '打卡', '推荐', '探索', '新地方', '逛逛', '玩什么'],
        'priority': 3,
        'style': '像朋友推荐，带点兴奋感，结合天气和状态'
    },
    'commuter': {
        'keywords': ['上班', '地铁', '赶时间', '堵车', '早饭', '到家', '下班', '通勤', '路上', '公交'],
        'priority': 2,
        'style': '简洁直接，不废话，30字内给结论'
    },
    'solo': {
        'keywords': ['一个人', '宅', '不想动', '夜宵', '累了', '躺着', '失眠', '无聊', '发呆'],
        'priority': 1,
        'style': '轻松陪伴，不打扰，治愈感'
    }
}

RECOMMENDATION_STRATEGIES = {
    'commuter': {'maxDistance': 500, 'maxWaitTime': 5, 'maxPrepTime': 15, 'sortBy': 'distance'},
    'dater': {'minRating': 4.5, 'features': ['private_room', 'quiet', 'romantic', 'group_friendly'], 'sortBy': 'rating'},
    'solo': {'features': ['solo_friendly', 'delivery_available', 'comfortable'], 'sortBy': 'comfort_score'},
    'explorer': {'features': ['unique', 'new', 'popular', 'instagram_worthy'], 'minRating': 4.0, 'sortBy': 'novelty_score'},
    'rescue': {'maxDistance': 1000, 'mustBeOpen': True, 'sortBy': 'distance'}
}

ACTIVITY_STRATEGIES = {
    'dater': {
        'max_count': 2,
        'prefer_categories': ['娱乐', '艺术', '音乐'],
        'prefer_features': ['group', 'exciting', 'photography'],
        'min_rating': 4.3,
        'max_distance': 10000
    },
    'explorer': {
        'max_count': 2,
        'prefer_categories': ['艺术', '户外', '文化', '音乐', '运动'],
        'prefer_features': ['photography', 'scenic', 'trendy'],
        'min_rating': 4.2,
        'max_distance': 20000
    },
    'solo': {
        'max_count': 2,
        'prefer_categories': ['文化', '休闲', '购物', '音乐'],
        'prefer_features': ['quiet', 'cultural', 'relaxing', 'comfortable'],
        'min_rating': 4.0,
        'max_distance': 8000
    },
    'commuter': {'max_count': 0},
    'rescue': {'max_count': 0}
}

# --- Active monitoring tasks ---
monitoring_tasks = {}

# --- Conversation memory (multi-turn) ---
conversation_memory = {
    'context': [],        # Last 5 conversation turns
    'last_mode': None,    # Last detected identity mode
    'last_topic': None,   # Last conversation topic
    'preferences_mentioned': []  # Preferences surfaced in conversation
}

# --- Proactive reminder tracking (server-side) ---
reminders_sent_today = 0
last_reminder_date = None
last_proactive_rejection_at = None
PROACTIVE_REJECTION_COOLDOWN_SECONDS = 24 * 60 * 60

# --- Event log for demo visibility ---
sandbox_events = []  # Keep last 100 events
MAX_EVENTS = 100
MAX_QUEUE = 30  # Upper bound for realistic queue simulation

def log_event(event_type, message):
    sandbox_events.append({
        'type': event_type,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })
    if len(sandbox_events) > MAX_EVENTS:
        sandbox_events.pop(0)

# --- Traffic state (dynamic) ---
traffic_state = {
    'condition': 'good',
    'speed': 'normal',
    'delay_minutes': 0,
    'congested_areas': []
}

# --- Flash deals ---
flash_deals = []

# --- Dynamic Sandbox ---
def dynamic_sandbox_worker():
    tick = 0
    while True:
        time.sleep(10)
        tick += 1
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=Mon, 6=Sun
        is_weekend = weekday >= 5
        is_lunch_rush = 11 <= hour < 13
        is_dinner_rush = 17 <= hour < 19
        is_peak = is_lunch_rush or is_dinner_rush

        for r in DB['restaurants']:
            # Reopen previously closed restaurants (MUST be before continue)
            if not r.get('open_status'):
                if random.random() < 0.1:
                    r['open_status'] = True
                    log_event('reopen', f"{r['name']}已恢复营业！")
                continue

            # ---- Peak hour surge ----
            if is_peak and random.random() < 0.5:
                surge = random.randint(2, 8)
                qc = r.get('queue_count', 0)
                r['queue_count'] = min(MAX_QUEUE, qc + surge)
                r['wait_time'] = r['queue_count'] * 3
                if random.random() < 0.05:
                    log_event('peak_surge', f"{'午餐' if is_lunch_rush else '晚餐'}高峰！{r['name']}排队暴增{surge}桌")

            # ---- Normal queue fluctuation ----
            if random.random() < 0.3:
                change = random.choice([-2, -1, 1, 2, 3])
                qc = r.get('queue_count', 0)
                r['queue_count'] = min(MAX_QUEUE, max(0, qc + change))
                r['wait_time'] = r['queue_count'] * 3

            # ---- 10分钟从有空变满座 (competition requirement) ----
            if random.random() < 0.04:
                if r.get('queue_count', 0) <= 2 and r.get('open_status'):
                    r['queue_count'] = random.randint(10, min(25, MAX_QUEUE))
                    r['wait_time'] = r['queue_count'] * 3
                    log_event('sudden_full', f"10分钟内！{r['name']}从有空变为爆满，排队{r['queue_count']}桌！")

            # ---- 满座突然有位 ----
            if random.random() < 0.04:
                if r.get('queue_count', 0) > 10:
                    r['queue_count'] = random.randint(0, 3)
                    r['wait_time'] = r['queue_count'] * 3
                    log_event('sudden_empty', f"好消息！{r['name']}突然有位了，只剩{r['queue_count']}桌排队！")

            # ---- Flash deal ----
            if random.random() < 0.03:
                discount = random.choice([20, 30, 40, 50])
                expires_min = random.choice([15, 30, 45, 60])
                deal = {
                    'restaurant': r['name'],
                    'discount': discount,
                    'original_price': r['price'],
                    'deal_price': int(r['price'] * (100 - discount) / 100),
                    'expires_in_minutes': expires_min,
                    'created_at': time.time(),
                    'message': f"闪惠！{r['name']}限时{discount}% off，原价{r['price']}元现仅{r['price']*(100-discount)//100}元！{expires_min}分钟内有效！"
                }
                flash_deals.append(deal)
                if len(flash_deals) > 10:
                    flash_deals.pop(0)
                log_event('flash_deal', deal['message'])

            # ---- Sudden closure ----
            if random.random() < 0.015:
                r['open_status'] = False
                log_event('closure', f"{r['name']}因厨房设备故障临时关闭，预计30分钟后恢复")

        # ---- Activity dynamics ----
        for a in DB['activities']:
            if random.random() < 0.04:
                old_crowd = a.get('crowd_level', '')
                levels = ['较少', '中等', '较多', '需预约', '已满员']
                new_crowd = random.choice(levels)
                if old_crowd != new_crowd:
                    a['crowd_level'] = new_crowd
                    if new_crowd == '已满员':
                        log_event('activity_full', f"{a['name']}已满员！需要提前预约")

            # Activity discount
            if random.random() < 0.03:
                discount = random.choice([15, 20, 30, 40])
                log_event('activity_discount', f"活动优惠！{a['name']}限时{discount}% off，原价{a['price']}元，现在只需{int(a['price']*(100-discount)/100)}元！")

        # ---- Traffic changes ----
        if random.random() < 0.08:
            conditions = ['good', 'slow', 'congested']
            traffic_state['condition'] = random.choice(conditions)
            if traffic_state['condition'] == 'congested':
                traffic_state['delay_minutes'] = random.randint(10, 30)
                traffic_state['congested_areas'] = random.sample(['中关村', '五道口', '学院路', '西二旗'], 2)
                log_event('traffic', f"交通拥堵！{','.join(traffic_state['congested_areas'])}附近延误{traffic_state['delay_minutes']}分钟")
            elif traffic_state['condition'] == 'slow':
                traffic_state['delay_minutes'] = random.randint(3, 10)
                traffic_state['congested_areas'] = []
            else:
                traffic_state['delay_minutes'] = 0
                traffic_state['congested_areas'] = []

        # Traffic surge on specific routes
        if random.random() < 0.05:
            routes = ['五道口→中关村', '学院路→西二旗', '知春路→五道口', '中关村大街']
            route = random.choice(routes)
            delay = random.randint(10, 25)
            log_event('traffic_surge', f"路段拥堵预警！{route}方向突发拥堵，预计延误{delay}分钟，建议绕行或使用地铁")

        # ---- Weather changes ----
        if random.random() < 0.08:
            current = DB['weather']['current']['temperature']
            new_temp = current + random.choice([-3, -2, -1, 1, 2, 3])
            DB['weather']['current']['temperature'] = max(-10, min(42, new_temp))

        if random.random() < 0.04:
            old_cond = DB['weather']['current']['condition']
            conditions = ['晴', '多云', '阴', '小雨', '阵雨']
            weights = [0.35, 0.3, 0.15, 0.12, 0.08]
            new_cond = random.choices(conditions, weights=weights)[0]
            if old_cond != new_cond:
                DB['weather']['current']['condition'] = new_cond
                if '雨' in new_cond and '雨' not in old_cond:
                    log_event('rain_start', f"天气变化！开始下雨了（{new_cond}），记得带伞！室内活动推荐优先")
                elif '雨' not in new_cond and '雨' in old_cond:
                    log_event('rain_stop', f"雨停了！现在是{new_cond}，适合外出活动")

        # Sudden clearing (good for outdoor)
        if random.random() < 0.02 and DB['weather']['current']['condition'] in ['多云', '阴']:
            DB['weather']['current']['condition'] = '晴'
            log_event('weather_clear', f"天气放晴了！云开雾散，现在非常适合户外活动！")

        # ---- Temperature alert ----
        if random.random() < 0.03:
            temp_change = random.choice([-8, -6, 6, 8, 10])
            new_temp = DB['weather']['current']['temperature'] + temp_change
            new_temp = max(-10, min(42, new_temp))
            DB['weather']['current']['temperature'] = new_temp
            log_event('temp_change', f"气温骤变{'+' if temp_change>0 else ''}{temp_change}°C！当前{new_temp}°C，注意增减衣物")

        # ---- Clear expired flash deals ----
        now = time.time()
        flash_deals[:] = [d for d in flash_deals if now - d.get('created_at', 0) < d['expires_in_minutes'] * 60]

        # ---- Check monitoring tasks ----
        for task_id, task in list(monitoring_tasks.items()):
            if task['status'] == 'active':
                for r in DB['restaurants']:
                    if task['restaurant_name'] in r['name']:
                        if r.get('queue_count', 999) <= task['target_count']:
                            task['triggered'] = True
                            task['current_queue'] = r['queue_count']
                            task['message'] = f"{r['name']}现在只剩{r['queue_count']}桌了，准备出发吧！要不要帮你叫个车？"

sandbox_thread = threading.Thread(target=dynamic_sandbox_worker, daemon=True)
sandbox_thread.start()

# --- API Routes ---

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    name = request.args.get('name')
    cuisine = request.args.get('cuisine')
    max_distance = request.args.get('max_distance', type=int)
    min_rating = request.args.get('min_rating', type=float)
    open_now = request.args.get('open_now')

    restaurants = DB['restaurants']

    if name:
        restaurants = [r for r in restaurants if name in r['name']]
    if cuisine:
        restaurants = [r for r in restaurants if r['cuisine'] == cuisine]
    if max_distance:
        restaurants = [r for r in restaurants if r['distance'] <= max_distance]
    if min_rating:
        restaurants = [r for r in restaurants if r['rating'] >= min_rating]
    if open_now and open_now.lower() == 'true':
        restaurants = [r for r in restaurants if r['open_status']]

    return jsonify({'success': True, 'data': restaurants, 'count': len(restaurants)})

@app.route('/api/activities', methods=['GET'])
def get_activities():
    category = request.args.get('category')
    weather = request.args.get('weather')

    activities = DB['activities']
    if category:
        activities = [a for a in activities if a['category'] == category]
    if weather:
        activities = [a for a in activities if any(w in weather or weather in w for w in a.get('weather_suitable', []))]

    return jsonify({'success': True, 'data': activities, 'count': len(activities)})

@app.route('/api/weather', methods=['GET'])
def get_weather():
    return jsonify({'success': True, 'data': DB['weather']})

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    return jsonify({
        'success': True,
        'data': {
            'user_id': 'demo_user_001',
            'commute_time': '08:30',
            'lunch_time': '12:00',
            'favorite_cuisines': ['川菜', '日料', '江浙菜', '火锅'],
            'dietary_restrictions': ['不吃香菜'],
            'spending_habit': 'medium',
            'frequent_locations': [
                {'name': '公司', 'address': '中关村软件园'},
                {'name': '家', 'address': '五道口'}
            ]
        }
    })

# --- NEW: Identity Detection API ---
@app.route('/api/identity', methods=['POST'])
def detect_identity():
    data = request.get_json() or {}
    user_message = data.get('message', '')

    detected_mode = 'solo'
    max_priority = 0
    matched_keywords = []

    for mode, config in IDENTITY_PATTERNS.items():
        for kw in config['keywords']:
            if kw in user_message:
                matched_keywords.append(kw)
                if config['priority'] > max_priority:
                    detected_mode = mode
                    max_priority = config['priority']

    return jsonify({
        'success': True,
        'data': {
            'identity_mode': detected_mode,
            'style_hint': IDENTITY_PATTERNS[detected_mode]['style'],
            'confidence': 'high' if max_priority > 0 else 'low',
            'matched_keywords': matched_keywords,
            'priority': max_priority
        }
    })

# --- ENHANCED: Smart Recommendations ---

# NEW: One-shot endpoint - detects identity AND returns recommendations
@app.route('/api/chat', methods=['POST'])
def chat_recommendations():
    """One-shot: detect identity from message + return recommendations + weather in one call."""
    data = request.get_json() or {}
    user_message = data.get('message', '')

    # Auto-detect identity
    detected_mode = 'solo'
    max_priority = 0
    matched_keywords = []

    for mode, config in IDENTITY_PATTERNS.items():
        for kw in config['keywords']:
            if kw in user_message:
                matched_keywords.append(kw)
                if config['priority'] > max_priority:
                    detected_mode = mode
                    max_priority = config['priority']

    # If the user rejects proactive nudges in normal conversation, start cooldown.
    rejection_keywords = ['不用提醒', '别提醒', '不要提醒', '先不用', '不用了', '别推送']
    if any(kw in user_message for kw in rejection_keywords):
        global last_proactive_rejection_at
        last_proactive_rejection_at = time.time()

    # Get recommendations
    cuisine = data.get('cuisine')
    max_price = data.get('max_price')
    if max_price is not None:
        try:
            max_price = int(max_price)
        except (ValueError, TypeError):
            max_price = None

    strategy = RECOMMENDATION_STRATEGIES.get(detected_mode, RECOMMENDATION_STRATEGIES['solo'])
    restaurants = list(DB['restaurants'])

    if 'maxDistance' in strategy:
        restaurants = [r for r in restaurants if r['distance'] <= strategy['maxDistance']]
    if 'mustBeOpen' in strategy and strategy['mustBeOpen']:
        restaurants = [r for r in restaurants if r['open_status']]
    if 'minRating' in strategy:
        restaurants = [r for r in restaurants if r['rating'] >= strategy['minRating']]
    if 'maxWaitTime' in strategy:
        restaurants = [r for r in restaurants if r.get('wait_time', 0) <= strategy['maxWaitTime']]
    if 'maxPrepTime' in strategy:
        restaurants = [r for r in restaurants if r.get('prep_time', 0) <= strategy['maxPrepTime']]
    if cuisine:
        restaurants = [r for r in restaurants if r['cuisine'] == cuisine]
    if max_price is not None:
        restaurants = [r for r in restaurants if r['price'] <= max_price]
    if 'features' in strategy:
        restaurants = [r for r in restaurants if any(f in r.get('features', []) for f in strategy['features'])]

    sort_by = strategy.get('sortBy', 'distance')
    sort_keys = {
        'distance': lambda r: r['distance'],
        'rating': lambda r: -r['rating'],
        'comfort_score': lambda r: -r.get('comfort_score', 0),
        'novelty_score': lambda r: -r.get('novelty_score', 0)
    }
    restaurants.sort(key=sort_keys.get(sort_by, sort_keys['distance']))

    highlight_templates = {
        'commuter': lambda r: f"{r['distance']}m - {r.get('prep_time', '?')}分钟出餐",
        'dater': lambda r: f"{r['rating']}分 - {r.get('atmosphere', '')}",
        'solo': lambda r: f"一人食 - {r.get('comfort_level', '')}",
        'explorer': lambda r: f"{r.get('specialty', '')} - {r.get('unique_feature', '')}",
        'rescue': lambda r: f"最近 - {'营业中' if r['open_status'] else '已关门'}"
    }
    get_highlight = highlight_templates.get(detected_mode, highlight_templates['solo'])

    top3 = restaurants[:3]
    recommendations = []
    for r in top3:
        recommendations.append({
            'name': r['name'],
            'cuisine': r['cuisine'],
            'address': r['address'],
            'distance': r['distance'],
            'rating': r['rating'],
            'price': r['price'],
            'wait_time': r.get('wait_time', 0),
            'queue_count': r.get('queue_count', 0),
            'open_status': r['open_status'],
            'open_hours': r.get('open_hours', ''),
            'highlight': get_highlight(r),
            'tags': r.get('tags', [])
        })

    weather_info = {
        'condition': DB['weather']['current']['condition'],
        'temperature': DB['weather']['current']['temperature'],
        'humidity': DB['weather']['current'].get('humidity', 'N/A')
    }

    # Activity recommendations
    activity_recs = []
    act_strategy = ACTIVITY_STRATEGIES.get(detected_mode, {'max_count': 0})
    if act_strategy.get('max_count', 0) > 0:
        acts = list(DB['activities'])
        # Filter by category preference
        prefer_cats = act_strategy.get('prefer_categories', [])
        if prefer_cats:
            scored = []
            # Hard filters
            min_rating = act_strategy.get('min_rating', 0)
            max_dist = act_strategy.get('max_distance', 99999)
            acts = [a for a in acts if a['rating'] >= min_rating and a['distance'] <= max_dist]

            for a in acts:
                score = 0
                if a['category'] in prefer_cats:
                    score += 3
                for feat in act_strategy.get('prefer_features', []):
                    if feat in a.get('features', []) or feat in a.get('tags', []):
                        score += 2
                current_weather = DB['weather']['current']['condition']
                if any(w in current_weather for w in a.get('weather_suitable', [])):
                    score += 1
                if score > 0:
                    scored.append((score, a))
            scored.sort(key=lambda x: -x[0])
            activity_recs = [dict(a) for _, a in scored[:act_strategy['max_count']]]
            for a in activity_recs:
                a['highlight'] = f"{a['category']} - {a['description']}"

    # Update conversation memory
    conversation_memory['context'].append({
        'user_message': user_message,
        'mode': detected_mode,
        'timestamp': datetime.now().isoformat()
    })
    if len(conversation_memory['context']) > 5:
        conversation_memory['context'].pop(0)
    conversation_memory['last_mode'] = detected_mode
    conversation_memory['last_topic'] = user_message[:30]

    return jsonify({
        'success': True,
        'data': {
            'identity_mode': detected_mode,
            'style_hint': IDENTITY_PATTERNS[detected_mode]['style'],
            'confidence': 'high' if max_priority > 0 else 'low',
            'recommendations': recommendations,
            'activities': activity_recs,
            'weather': weather_info,
            'memory': {
                'last_mode': conversation_memory.get('last_mode'),
                'last_topic': conversation_memory.get('last_topic'),
                'turn_count': len(conversation_memory.get('context', []))
            },
            'timestamp': datetime.now().isoformat()
        }
    })

# Legacy: identity-aware recommendations (requires pre-detected mode)
@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json() or {}
    identity_mode = data.get('identity_mode', 'solo')
    cuisine = data.get('cuisine')
    max_price = data.get('max_price')
    if max_price is not None:
        try:
            max_price = int(max_price)
        except (ValueError, TypeError):
            max_price = None

    strategy = RECOMMENDATION_STRATEGIES.get(identity_mode, RECOMMENDATION_STRATEGIES['solo'])
    restaurants = list(DB['restaurants'])

    # Apply strategy filters
    if 'maxDistance' in strategy:
        restaurants = [r for r in restaurants if r['distance'] <= strategy['maxDistance']]
    if 'mustBeOpen' in strategy and strategy['mustBeOpen']:
        restaurants = [r for r in restaurants if r['open_status']]
    if 'minRating' in strategy:
        restaurants = [r for r in restaurants if r['rating'] >= strategy['minRating']]
    if 'maxWaitTime' in strategy:
        restaurants = [r for r in restaurants if r.get('wait_time', 0) <= strategy['maxWaitTime']]
    if 'maxPrepTime' in strategy:
        restaurants = [r for r in restaurants if r.get('prep_time', 0) <= strategy['maxPrepTime']]

    # User filters
    if cuisine:
        restaurants = [r for r in restaurants if r['cuisine'] == cuisine]
    if max_price is not None:
        restaurants = [r for r in restaurants if r['price'] <= max_price]
    if 'features' in strategy:
        restaurants = [r for r in restaurants if any(f in r.get('features', []) for f in strategy['features'])]

    # Sort
    sort_by = strategy.get('sortBy', 'distance')
    sort_keys = {
        'distance': lambda r: r['distance'],
        'rating': lambda r: -r['rating'],
        'comfort_score': lambda r: -r.get('comfort_score', 0),
        'novelty_score': lambda r: -r.get('novelty_score', 0)
    }
    restaurants.sort(key=sort_keys.get(sort_by, sort_keys['distance']))

    # Highlights per mode
    highlight_templates = {
        'commuter': lambda r: f"{r['distance']}m - {r.get('prep_time', '?')}分钟出餐",
        'dater': lambda r: f"{r['rating']}分 - {r.get('atmosphere', '')}",
        'solo': lambda r: f"一人食 - {r.get('comfort_level', '')}",
        'explorer': lambda r: f"{r.get('specialty', '')} - {r.get('unique_feature', '')}",
        'rescue': lambda r: f"最近 - {'营业中' if r['open_status'] else '即将关门'}"
    }
    get_highlight = highlight_templates.get(identity_mode, highlight_templates['solo'])

    top3 = restaurants[:3]
    result = []
    for r in top3:
        result.append({
            'name': r['name'],
            'cuisine': r['cuisine'],
            'address': r['address'],
            'distance': r['distance'],
            'rating': r['rating'],
            'price': r['price'],
            'wait_time': r.get('wait_time', 0),
            'queue_count': r.get('queue_count', 0),
            'open_status': r['open_status'],
            'open_hours': r.get('open_hours', ''),
            'highlight': get_highlight(r),
            'tags': r.get('tags', [])
        })

    return jsonify({
        'success': True,
        'data': {
            'recommendations': result,
            'identity_mode': identity_mode,
            'real_time_info': {
                'weather': f"{DB['weather']['current']['condition']} {DB['weather']['current']['temperature']}C",
                'humidity': str(DB['weather']['current'].get('humidity', 'N/A'))
            },
            'timestamp': datetime.now().isoformat()
        }
    })

# --- NEW: Ride Hailing API ---
@app.route('/api/ride-hailing', methods=['POST'])
def ride_hailing():
    data = request.get_json() or {}
    destination = data.get('destination', '')
    if not destination:
        return jsonify({'success': False, 'error': '目的地不能为空'}), 400
    origin = data.get('origin', '当前位置')
    car_type = data.get('car_type', '快车')

    wait_time = random.randint(1, 5) + traffic_state['delay_minutes'] // 5
    price = random.randint(15, 35)
    plates = ['京A88888', '京N66666', '京Q12345', '京B99999']

    route_duration = random.randint(10, 30) + traffic_state['delay_minutes']
    traffic_note = ''
    if traffic_state['condition'] != 'good':
        traffic_note = f"，注意{'拥堵' if traffic_state['condition'] == 'congested' else '行驶缓慢'}可能增加{traffic_state['delay_minutes']}分钟"

    return jsonify({
        'success': True,
        'data': {
            'status': 'success',
            'message': f"已经帮你叫好{car_type}了，司机大概{wait_time}分钟后到{origin}。去{destination}预估{price}元{traffic_note}。",
            'driver_info': {
                'plate': random.choice(plates),
                'car': '白色 丰田卡罗拉',
                'wait_time_minutes': wait_time
            },
            'estimated_price': price,
            'route': {
                'distance': f'{random.uniform(2, 8):.1f}km',
                'duration': f'{route_duration}分钟'
            },
            'traffic': {
                'condition': traffic_state['condition'],
                'delay_minutes': traffic_state['delay_minutes']
            }
        }
    })

# --- NEW: Queue Monitor API ---
@app.route('/api/queue-monitor/start', methods=['POST'])
def start_queue_monitor():
    data = request.get_json() or {}
    restaurant_name = data.get('restaurant_name', '')
    target_count = data.get('target_count', 5)

    task_id = f"queue_{int(time.time())}"
    monitoring_tasks[task_id] = {
        'restaurant_name': restaurant_name,
        'target_count': target_count,
        'status': 'active',
        'triggered': False,
        'current_queue': None,
        'message': '',
        'started_at': datetime.now().isoformat()
    }

    # Find current queue
    for r in DB['restaurants']:
        if restaurant_name in r['name']:
            current = r.get('queue_count', 0)
            break
    else:
        current = '未知'

    return jsonify({
        'success': True,
        'data': {
            'task_id': task_id,
            'status': 'monitoring_started',
            'message': f"已开始监控{restaurant_name}，当前排队{current}桌，到剩{target_count}桌时提醒你。",
            'current_queue': current
        }
    })

@app.route('/api/queue-monitor/check/<task_id>', methods=['GET'])
def check_queue_monitor(task_id):
    task = monitoring_tasks.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404

    # Refresh from DB
    for r in DB['restaurants']:
        if task['restaurant_name'] in r['name']:
            task['current_queue'] = r.get('queue_count', 0)
            if task['current_queue'] <= task['target_count']:
                task['triggered'] = True
                task['message'] = f"{r['name']}现在只剩{task['current_queue']}桌了！要帮你叫车吗？"
            break

    return jsonify({
        'success': True,
        'data': {
            'task_id': task_id,
            'status': task['status'],
            'triggered': task['triggered'],
            'current_queue': task['current_queue'],
            'target_count': task['target_count'],
            'message': task['message']
        }
    })

@app.route('/api/queue-monitor/stop/<task_id>', methods=['POST'])
def stop_queue_monitor(task_id):
    task = monitoring_tasks.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    task['status'] = 'stopped'
    return jsonify({'success': True, 'data': {'message': '监控已停止'}})

# --- NEW: Check all active monitors ---
@app.route('/api/monitors/check-all', methods=['GET'])
def check_all_monitors():
    """Check all active monitors and return any triggered alerts."""
    triggered = []
    active_count = 0

    for task_id, task in list(monitoring_tasks.items()):
        if task['status'] != 'active':
            continue
        active_count += 1

        # Refresh from DB
        for r in DB['restaurants']:
            if task['restaurant_name'] in r['name']:
                task['current_queue'] = r.get('queue_count', 0)
                if task['current_queue'] <= task['target_count']:
                    task['triggered'] = True
                    task['message'] = f"{r['name']}现在只剩{task['current_queue']}桌了！要帮你叫车吗？"
                break

        if task.get('triggered'):
            triggered.append({
                'task_id': task_id,
                'restaurant_name': task['restaurant_name'],
                'current_queue': task['current_queue'],
                'target_count': task['target_count'],
                'message': task['message']
            })

    return jsonify({
        'success': True,
        'data': {
            'active_monitors': active_count,
            'triggered': triggered,
            'any_triggered': len(triggered) > 0
        }
    })

# Notification queue for proactive alerts
pending_notifications = []

@app.route('/api/notifications/pending', methods=['GET'])
def get_pending_notifications():
    """Get and clear pending proactive notifications."""
    global pending_notifications
    result = list(pending_notifications)
    pending_notifications = []
    return jsonify({
        'success': True,
        'data': {
            'notifications': result,
            'count': len(result)
        }
    })

@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    """Queue a notification to be delivered to the user."""
    data = request.get_json() or {}
    msg = data.get('message', '')
    ntype = data.get('type', 'info')
    pending_notifications.append({
        'type': ntype,
        'message': msg,
        'timestamp': datetime.now().isoformat()
    })
    return jsonify({'success': True, 'data': {'queued': True}})

# --- Conversation Memory API ---
@app.route('/api/memory/save', methods=['POST'])
def memory_save():
    """Save a conversation turn to short-term memory."""
    data = request.get_json() or {}
    user_msg = data.get('user_message', '')
    assistant_msg = data.get('assistant_message', '')
    identity_mode = data.get('identity_mode', 'solo')
    topic = data.get('topic', '')

    turn = {
        'user': user_msg,
        'assistant': assistant_msg[:200],  # Truncate for storage
        'mode': identity_mode,
        'topic': topic,
        'timestamp': datetime.now().isoformat()
    }
    conversation_memory['context'].append(turn)
    if len(conversation_memory['context']) > 5:
        conversation_memory['context'].pop(0)

    if identity_mode:
        conversation_memory['last_mode'] = identity_mode
    if topic:
        conversation_memory['last_topic'] = topic

    # Detect and record preference keywords
    pref_keywords = ['不吃', '喜欢', '爱吃', '忌口', '过敏', '素食', '辣', '香菜', '海鲜', '牛肉', '羊肉', '清淡', '甜', '酸', '麻']
    for kw in pref_keywords:
        if kw in user_msg or kw in assistant_msg:
            if kw not in conversation_memory['preferences_mentioned']:
                conversation_memory['preferences_mentioned'].append(kw)

    return jsonify({'success': True, 'data': {'turns_stored': len(conversation_memory['context'])}})

@app.route('/api/memory/recall', methods=['GET'])
def memory_recall():
    """Recall recent conversation context."""
    return jsonify({
        'success': True,
        'data': {
            'recent_turns': conversation_memory['context'],
            'last_mode': conversation_memory['last_mode'],
            'last_topic': conversation_memory['last_topic'],
            'turn_count': len(conversation_memory['context']),
            'preferences_mentioned': conversation_memory.get('preferences_mentioned', [])
        }
    })

# --- NEW: Proactive check API ---
@app.route('/api/proactive-check', methods=['POST'])
def proactive_check():
    global reminders_sent_today, last_reminder_date

    data = request.get_json() or {}
    current_hour = data.get('hour', datetime.now().hour)
    current_weekday = data.get('weekday', datetime.now().weekday())
    identity_mode = data.get('identity_mode') or conversation_memory.get('last_mode')
    user_busy = bool(data.get('user_busy')) or identity_mode == 'rescue'
    weather_condition = DB['weather']['current']['condition']

    # Reset counter on new day
    today = datetime.now().date()
    if last_reminder_date != today:
        reminders_sent_today = 0
        last_reminder_date = today

    notifications = []

    # Quiet hours check
    if current_hour >= 23 or current_hour < 7:
        return jsonify({'success': True, 'data': {'should_notify': False, 'reason': 'quiet_hours'}})

    # Do not interrupt rescue mode or explicitly busy users.
    if user_busy:
        return jsonify({'success': True, 'data': {'should_notify': False, 'reason': 'user_busy', 'identity_mode': identity_mode}})

    # Respect rejection cooldown.
    if last_proactive_rejection_at and time.time() - last_proactive_rejection_at < PROACTIVE_REJECTION_COOLDOWN_SECONDS:
        remaining = int((PROACTIVE_REJECTION_COOLDOWN_SECONDS - (time.time() - last_proactive_rejection_at)) // 60)
        return jsonify({
            'success': True,
            'data': {
                'should_notify': False,
                'reason': 'recently_rejected',
                'cooldown_remaining_minutes': remaining
            }
        })

    # Daily limit check (server-side counter)
    if reminders_sent_today >= 3:
        return jsonify({'success': True, 'data': {'should_notify': False, 'reason': 'daily_limit', 'reminders_today': reminders_sent_today}})

    # Routine reminders
    if current_hour == 7 and current_weekday < 5:
        notifications.append({'type': 'routine', 'message': '早上好！早餐想吃啥？', 'priority': 'low'})
    elif current_hour == 7 and current_weekday >= 5:
        notifications.append({'type': 'routine', 'message': '周末早上好！睡个好觉起来吃点啥？', 'priority': 'low'})
    elif current_hour == 11 and current_weekday < 5:
        notifications.append({'type': 'routine', 'message': '快到午饭时间了，今天想吃什么？', 'priority': 'low'})
    elif current_hour == 11 and current_weekday >= 5:
        notifications.append({'type': 'routine', 'message': '周末中午了！要不要出去搓一顿？', 'priority': 'low'})
    elif current_hour == 18 and current_weekday < 5:
        notifications.append({'type': 'routine', 'message': '下班了，路上想吃点什么？', 'priority': 'low'})
    elif current_hour == 18 and current_weekday >= 5:
        notifications.append({'type': 'routine', 'message': '周末晚上最适合探店了，想吃什么？', 'priority': 'low'})
    elif current_hour == 17 and current_weekday == 4:
        notifications.append({'type': 'proactive', 'message': '周五了！周末想去哪玩？', 'priority': 'medium'})

    # Weather alerts
    if '雨' in weather_condition:
        notifications.append({'type': 'weather', 'message': f"天气{weather_condition}，出门记得带伞", 'priority': 'high'})

    if notifications:
        reminders_sent_today += 1
        return jsonify({
            'success': True,
            'data': {
                'should_notify': True,
                'notifications': notifications,
                'weather': f"{weather_condition} {DB['weather']['current']['temperature']}C",
                'reminders_today': reminders_sent_today
            }
        })

    return jsonify({'success': True, 'data': {'should_notify': False, 'reminders_today': reminders_sent_today}})

@app.route('/api/proactive-feedback', methods=['POST'])
def proactive_feedback():
    """Record user feedback on proactive reminders, especially rejection cooldown."""
    global last_proactive_rejection_at
    data = request.get_json() or {}
    action = data.get('action', '')

    if action in ['reject', 'dismiss', 'stop']:
        last_proactive_rejection_at = time.time()
        return jsonify({
            'success': True,
            'data': {
                'recorded': True,
                'cooldown_hours': 24,
                'reason': 'recently_rejected'
            }
        })

    return jsonify({'success': True, 'data': {'recorded': False}})

# --- NEW: Sandbox event log ---
@app.route('/api/events', methods=['GET'])
def get_events():
    """Get recent sandbox events for demo visibility."""
    limit = request.args.get('limit', 20, type=int)
    event_type = request.args.get('type')
    events = sandbox_events
    if event_type:
        events = [e for e in events if e['type'] == event_type]
    return jsonify({
        'success': True,
        'data': {
            'events': events[-limit:],
            'total': len(events),
            'active_flash_deals': len(flash_deals),
            'traffic_condition': traffic_state['condition'],
            'current_time': datetime.now().isoformat()
        }
    })

# --- NEW: Flash deals ---
@app.route('/api/flash-deals', methods=['GET'])
def get_flash_deals():
    """Get active flash deals."""
    return jsonify({
        'success': True,
        'data': {
            'deals': flash_deals,
            'count': len(flash_deals)
        }
    })

# --- NEW: Traffic info ---
@app.route('/api/traffic', methods=['GET'])
def get_traffic():
    """Get current traffic conditions."""
    return jsonify({
        'success': True,
        'data': traffic_state
    })

# --- NEW: Sandbox status overview ---
@app.route('/api/sandbox/status', methods=['GET'])
def sandbox_status():
    """Comprehensive sandbox status for demo dashboard."""
    now = datetime.now()
    hour = now.hour
    return jsonify({
        'success': True,
        'data': {
            'time': now.isoformat(),
            'hour': hour,
            'weekday': now.weekday(),
            'is_lunch_rush': 11 <= hour < 13,
            'is_dinner_rush': 17 <= hour < 19,
            'is_weekend': now.weekday() >= 5,
            'weather': {
                'condition': DB['weather']['current']['condition'],
                'temperature': DB['weather']['current']['temperature'],
                'humidity': DB['weather']['current'].get('humidity', 'N/A')
            },
            'traffic': traffic_state,
            'active_monitors': len([t for t in monitoring_tasks.values() if t['status'] == 'active']),
            'active_flash_deals': len(flash_deals),
            'recent_events': sandbox_events[-5:],
            'restaurant_count': len(DB['restaurants']),
            'activity_count': len(DB['activities'])
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'ShadowMe Mock Backend',
        'version': '2.2.5',
        'active_monitors': len(monitoring_tasks),
        'restaurant_count': len(DB['restaurants']),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5000'))
    print("ShadowMe Mock Backend v2.2.5 (Dynamic Sandbox)")
    print("Endpoints (23):")
    print("  GET  /health")
    print("  GET  /api/restaurants")
    print("  GET  /api/activities")
    print("  GET  /api/weather")
    print("  GET  /api/user/profile")
    print("  POST /api/chat")
    print("  POST /api/identity")
    print("  POST /api/recommendations")
    print("  POST /api/ride-hailing")
    print("  POST /api/queue-monitor/start")
    print("  GET  /api/queue-monitor/check/<id>")
    print("  POST /api/queue-monitor/stop/<id>")
    print("  POST /api/proactive-check")
    print("  POST /api/proactive-feedback")
    print("  GET  /api/events")
    print("  GET  /api/sandbox/status")
    print("  GET  /api/flash-deals")
    print("  GET  /api/traffic")
    print("  GET  /api/monitors/check-all")
    print("  POST /api/notifications/send")
    print("  GET  /api/notifications/pending")
    print("  POST /api/memory/save")
    print("  GET  /api/memory/recall")
    print(f"Running on http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
