import streamlit as st
import time
import os
import requests
import json
import random

# ==================================================
# ✅ 你的配置 (已保留)
# ==================================================
COZE_API_TOKEN = "pat_e9JyWvouJgeY2MqCDbuYdYWl7DR6wzL9T0qJ8w5HIGplBQVbjzNI07I2TCImLGD7"
BOT_ID = "7595634139391983669"
# ==================================================

COZE_API_URL = "https://api.coze.com/v3/chat"

st.set_page_config(
    page_title="灵犀占星 SoulCompass",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS 样式：增强仪式感 ---
st.markdown("""
<style>
    .stButton>button {
        background: linear-gradient(to right, #2c3e50, #4ca1af);
        color: white;
        border: none;
        border-radius: 12px;
        height: 55px;
        font-size: 20px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(76, 161, 175, 0.4);
    }
    .iching-coin {
        font-size: 40px;
        animation: spin 1s infinite;
        display: inline-block;
        margin: 0 10px;
    }
    .iching-line-yang {
        color: #e67e22;
        font-family: monospace;
        font-size: 30px;
        font-weight: 900;
        text-shadow: 0 0 5px rgba(230, 126, 34, 0.5);
    }
    .iching-line-yin {
        color: #7f8c8d;
        font-family: monospace;
        font-size: 30px;
        font-weight: 900;
    }
</style>
""", unsafe_allow_html=True)

# --- 工具：构建 78 张塔罗牌 (Sacred Texts 稳定图源) ---
def get_card_by_index(index):
    """
    根据 0-77 的数字，返回对应的塔罗牌信息
    图源使用 Sacred Texts Archive (Rider-Waite)
    """
    base_url = "https://www.sacred-texts.com/tarot/pkt/img"
    
    # 1. 大阿卡纳 (0-21)
    majors = [
        "愚人", "魔术师", "女祭司", "皇后", "皇帝", "教皇", "恋人", "战车",
        "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制",
        "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"
    ]
    
    # 2. 小阿卡纳 (22-77)
    # 顺序：权杖(Wands) -> 圣杯(Cups) -> 宝剑(Swords) -> 星币(Pentacles)
    suits = [
        {"code": "wa", "name": "权杖"},
        {"code": "cu", "name": "圣杯"},
        {"code": "sw", "name": "宝剑"},
        {"code": "pe", "name": "星币"}
    ]
    
    # 如果是 0-21，直接返回大阿卡纳
    if 0 <= index <= 21:
        return {
            "name": f"{majors[index]} (大阿卡纳)",
            "url": f"{base_url}/ar{index:02d}.jpg"
        }
    
    # 如果是 22-77，计算小阿卡纳
    minor_index = index - 22
    suit_idx = minor_index // 14 # 0-3 (决定花色)
    card_val = minor_index % 14 + 1 # 1-14 (决定点数)
    
    current_suit = suits[suit_idx]
    
    # 处理文件名后缀
    if card_val == 1: suffix = "ac"; val_name = "王牌 (Ace)"
    elif 2 <= card_val <= 10: suffix = f"{card_val:02d}"; val_name = str(card_val)
    elif card_val == 11: suffix = "pa"; val_name = "侍从 (Page)"
    elif card_val == 12: suffix = "kn"; val_name = "骑士 (Knight)"
    elif card_val == 13: suffix = "qu"; val_name = "王后 (Queen)"
    elif card_val == 14: suffix = "ki"; val_name = "国王 (King)"
    
    return {
        "name": f"{current_suit['name']} {val_name}",
        "url": f"{base_url}/{current_suit['code']}{suffix}.jpg"
    }

def call_coze_stream(user_input, user_name, birth_info, spirit_numbers, tarot_cards, hexagram_name):
    headers = {
        "Authorization": f"Bearer {COZE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    cards_str = "、".join([c['name'] for c in tarot_cards])
    
    full_prompt = (
        f"【角色设定】\n"
        f"你叫'灵犀'，一位隐居深山的玄学宗师。语气温暖、睿智、像老朋友。严禁使用列表(1.2.3.)，严禁复读。\n\n"
        f"【现场起卦数据】\n"
        f"👤 缘主：{user_name} ({birth_info})\n"
        f"🔢 灵数：{spirit_numbers}\n"
        f"🎴 抽得塔罗：{cards_str}\n"
        f"☯️ 易经卦象：{hexagram_name}\n\n"
        f"❓ 困惑：{user_input}\n\n"
        f"【回答结构】\n"
        f"第一段：寒暄，叫他的名字，建立连接。\n"
        f"第二段（塔罗解析）：结合{cards_str}，深度解析潜意识。\n"
        f"第三段（易经指引）：结合{hexagram_name}，分析吉凶时运。\n"
        f"第四段（紫微奇门）：给出具体行动建议（方位/贵人/时间）。\n"
        f"第五段（寄语）：一句简短有力的祝福，然后结束。\n"
    )

    data = {
        "bot_id": BOT_ID,
        "user_id": f"user_{int(time.time())}", 
        "stream": True, 
        "auto_save_history": True,
        "additional_messages": [{"role": "user", "content": full_prompt, "content_type": "text"}]
    }

    try:
        response = requests.post(COZE_API_URL, headers=headers, json=data, stream=True)
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data:"):
                    json_str = decoded_line[5:]
                    try:
                        event_data = json.loads(json_str)
                        if event_data.get("type") == "answer" and "content" in event_data:
                            yield event_data["content"]
                    except:
                        pass
    except Exception as e:
        yield f"⚠️ 宗师正在闭关... ({str(e)})"

# --- 侧边栏 ---
with st.sidebar:
    st.title("🔮 开启命运仪式")
    st.markdown("---")
    name = st.text_input("你的名字 / Nickname", key="name")
    gender = st.radio("性别", ["男", "女"], horizontal=True)
    col1, col2, col3 = st.columns(3)
    with col1: birth_year = st.number_input("年", 1950, 2010, 1995)
    with col2: birth_month = st.number_input("月", 1, 12, 1)
    with col3: birth_day = st.number_input("日", 1, 31, 1)
    
    birth_hour = st.selectbox("时辰", ["未知", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"])
    
    st.markdown("---")
    st.info("🔮 调整灵数，共振宇宙 (0-78)")
    # ✅ 修复：范围改成 0-78，完全对应 78 张牌
    n1 = st.slider("灵数一 (过去)", 0, 77, 0)
    n2 = st.slider("灵数二 (现在)", 0, 77, 21)
    n3 = st.slider("灵数三 (未来)", 0, 77, 77)

# --- 主页面 ---
st.title("🌌 SoulCompass 全息命运指引")
st.markdown("*“万物皆有灵，数字即钥匙。”*")

user_question = st.text_area("", height=100, placeholder="在此写下你的困惑，向宇宙发问...")
start_button = st.button("✨ 启动全息推演 (含古法仪式) ✨", type="primary", use_container_width=True)

if start_button:
    if not user_question:
        st.error("请先写下你的问题，心诚则灵。")
    else:
        # === 1. 塔罗牌 (从 Sacred Texts 获取) ===
        st.subheader("🎴 塔罗·潜意识投影")
        
        # 根据用户输入的灵数，直接获取对应的牌
        c1 = get_card_by_index(n1)
        c2 = get_card_by_index(n2)
        c3 = get_card_by_index(n3)
        selected_cards = [c1, c2, c3]
        
        t1, t2, t3 = st.columns(3)
        with t1: st.image(c1["url"], caption=f"过去：{c1['name']}", use_container_width=True)
        with t2: st.image(c2["url"], caption=f"现在：{c2['name']}", use_container_width=True)
        with t3: st.image(c3["url"], caption=f"未来：{c3['name']}", use_container_width=True)
        
        st.divider()

        # === 2. 易经·真·掷铜钱动画 ===
        st.subheader("☯️ 易经·古法六爻起卦")
        
        status_text = st.empty()
        hexagram_container = st.empty()
        final_lines_html = []
        
        # 设定随机种子
        random.seed(n1 + n2 + n3 + int(time.time()))
        
        # 模拟 6 次掷币过程 (从下往上)
        for i in range(6):
            # 1. 动画阶段：显示正在掷币
            status_text.markdown(f"**正在掷第 {i+1} 爻...** 🪙 🪙 🪙 (哗啦啦...)")
            time.sleep(0.5)
            
            # 2. 计算结果：模拟3枚硬币 (0=背面/字, 1=正面/花)
            # 规则：
            # 1个背 -> 阳爻
            # 2个背 -> 阴爻
            # 3个背 -> 老阳 (动爻) -> 这里简化为阳
            # 0个背 -> 老阴 (动爻) -> 这里简化为阴
            
            coins = [random.randint(0, 1) for _ in range(3)]
            back_count = coins.count(0) # 计算背面数量
            
            is_yang = False
            if back_count == 1 or back_count == 3:
                is_yang = True
            
            # 3. 显示结果
            if is_yang:
                line_html = "<div class='iching-line-yang'>━━━━━━━ (阳)</div>"
                status_text.markdown(f"第 {i+1} 爻结果：**阳** (🌕)")
            else:
                line_html = "<div class='iching-line-yin'>━━　　━━ (阴)</div>"
                status_text.markdown(f"第 {i+1} 爻结果：**阴** (🌑)")
            
            time.sleep(0.3)
            
            # 插入到最前面 (因为是从下往上画)
            final_lines_html.insert(0, line_html)
            hexagram_container.markdown("".join(final_lines_html), unsafe_allow_html=True)
            
        status_text.success("✅ 六爻卦象已成！")
        
        # 简单判断卦名传给 AI (这里为了简化，传给AI让它根据灵数去深算，这里只做视觉展示)
        hex_name = "根据灵数生成的专属本命卦" 

        st.divider()

        # === 3. 宗师解读 ===
        st.subheader("🧙‍♂️ 灵犀宗师的家书")
        st.markdown("---")
        
        full_birth_info = f"性别{gender}，{birth_year}年{birth_month}月{birth_day}日 {birth_hour}时"
        user_name_str = name if name else "有缘人"
        spirit_nums_str = f"{n1}, {n2}, {n3}"
        
        with st.spinner("宗师正在观察卦象，为您书写判词..."):
            st.write_stream(call_coze_stream(user_question, user_name_str, full_birth_info, spirit_nums_str, selected_cards, hex_name))
            
        st.markdown("---")
