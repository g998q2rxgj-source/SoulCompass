import streamlit as st
import time
import os
import requests
import json
import random

# ==================================================
# ✅ 配置区 (已保留你的 Key)
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

# --- CSS 样式优化 ---
st.markdown("""
<style>
    .stButton>button {
        background-color: #2c1e3e;
        color: white;
        border-radius: 8px;
        height: 50px;
        font-size: 18px;
        border: 1px solid #4a3b5e;
    }
    .stButton>button:hover {
        background-color: #4a3b5e;
        border-color: #ffd700;
        color: #ffd700;
    }
    .iching-line {
        font-family: 'Courier New', monospace;
        font-size: 28px;
        text-align: center;
        line-height: 1.2;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 工具：构建 78 张完整塔罗牌库 ---
def get_full_tarot_deck():
    """
    使用开源的 Rider-Waite 图源，自动生成 78 张牌的数据
    """
    base_url = "https://raw.githubusercontent.com/shadovo/tarot-json/master/images"
    deck = []

    # 1. 大阿卡纳 (Major Arcana) - m00 到 m21
    majors = [
        "愚人", "魔术师", "女祭司", "皇后", "皇帝", "教皇", "恋人", "战车",
        "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制",
        "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"
    ]
    for i, name in enumerate(majors):
        file_code = f"m{i:02d}" # m00, m01...
        deck.append({"name": f"{name} (大阿卡纳)", "url": f"{base_url}/{file_code}.jpg"})

    # 2. 小阿卡纳 (Minor Arcana) - w/c/s/p + 01-14
    # w=Wands(权杖), c=Cups(圣杯), s=Swords(宝剑), p=Pentacles(星币)
    suits = {
        "w": "权杖",
        "c": "圣杯",
        "s": "宝剑",
        "p": "星币"
    }
    
    for code, suit_name in suits.items():
        for i in range(1, 15):
            # 转换数字为名称
            if i == 1: val = "王牌 (Ace)"
            elif i <= 10: val = str(i)
            elif i == 11: val = "侍从 (Page)"
            elif i == 12: val = "骑士 (Knight)"
            elif i == 13: val = "王后 (Queen)"
            elif i == 14: val = "国王 (King)"
            
            file_code = f"{code}{i:02d}" # w01, w02...
            deck.append({"name": f"{suit_name}{val}", "url": f"{base_url}/{file_code}.jpg"})
            
    return deck

def call_coze_stream(user_input, user_name, birth_info, spirit_numbers, tarot_cards):
    headers = {
        "Authorization": f"Bearer {COZE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 把抽到的牌名加入 Prompt，让 AI 针对这 3 张牌解读
    cards_str = f"{tarot_cards[0]['name']}, {tarot_cards[1]['name']}, {tarot_cards[2]['name']}"

    full_prompt = (
        f"【角色设定】\n"
        f"你叫'灵犀'，一位隐居深山的玄学宗师。把用户当晚辈，语气温暖、口语化。严禁使用列表(1.2.3.)，严禁复读。\n\n"
        f"【用户信息】\n"
        f"姓名：{user_name}\n"
        f"八字：{birth_info}\n"
        f"灵数：{spirit_numbers}\n\n"
        f"【现场卦象】\n"
        f"🎴 刚才他抽到的三张塔罗牌是：{cards_str} (请重点解读这三张牌的组合)\n"
        f"❓ 他的困惑：{user_input}\n\n"
        f"【回答结构】\n"
        f"第一段：寒暄，叫他的名字，安抚情绪。\n"
        f"第二段（塔罗解析）：结合{cards_str}，分析他现在的处境和潜意识。\n"
        f"第三段（易经与时运）：分析当下的时机。\n"
        f"第四段（紫微与奇门）：给出具体的方向指引。\n"
        f"第五段（宗师寄语）：一句简短有力的祝福，然后结束。\n"
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
    st.info("默念问题，调整灵数")
    n1 = st.slider("灵数一 (天)", 1, 9, 7)
    n2 = st.slider("灵数二 (地)", 1, 9, 2)
    n3 = st.slider("灵数三 (人)", 1, 6, 5)

# --- 主页面 ---
st.title("🌌 SoulCompass 全息命运指引")
st.markdown("*连接东方易理与西方星象，为你显化当下的能量图景。*")

user_question = st.text_area("", height=100, placeholder="在此写下你的困惑，向宇宙发问...")
start_button = st.button("✨ 启动全息推演 ✨", type="primary", use_container_width=True)

if start_button:
    if not user_question:
        st.error("请先写下你的问题，心诚则灵。")
    else:
        # === 1. 塔罗牌抽牌 (从78张牌库中抽取) ===
        st.subheader("🎴 塔罗·潜意识投影")
        
        # 获取完整牌库
        full_deck = get_full_tarot_deck()
        
        # 随机抽取 3 张
        selected_cards = random.sample(full_deck, 3) 
        
        t1, t2, t3 = st.columns(3)
        # 显示图片，并标注牌名
        with t1: 
            st.image(selected_cards[0]["url"], caption=f"过去：{selected_cards[0]['name']}", use_container_width=True)
        with t2: 
            st.image(selected_cards[1]["url"], caption=f"现在：{selected_cards[1]['name']}", use_container_width=True)
        with t3: 
            st.image(selected_cards[2]["url"], caption=f"未来：{selected_cards[2]['name']}", use_container_width=True)
        
        st.divider()

        # === 2. 易经起卦动画 (视觉优化版) ===
        st.subheader("☯️ 易经·六爻起卦")
        
        iching_container = st.empty()
        hexagram_lines = []
        random.seed(n1 + n2 + n3 + int(time.time())) # 加入时间戳，让每次起卦都略有不同
        
        # 动画循环
        for i in range(6):
            time.sleep(0.3) 
            coin_toss = random.randint(0, 1)
            
            # 视觉符号优化
            if coin_toss == 1:
                line_html = "<div style='color:#e67e22' class='iching-line'>━━━━━━━ (阳)</div>"
            else:
                line_html = "<div style='color:#7f8c8d' class='iching-line'>━━　　━━ (阴)</div>"
                
            # 易经是从下往上画，所以用 insert(0)
            hexagram_lines.insert(0, line_html)
            iching_container.markdown("".join(hexagram_lines), unsafe_allow_html=True)
        
        st.caption("注：卦象已成，初爻居下，上爻居上。")
        st.divider()

        # === 3. 宗师解读 ===
        st.subheader("🧙‍♂️ 灵犀宗师的家书")
        st.markdown("---")
        
        full_birth_info = f"性别{gender}，{birth_year}年{birth_month}月{birth_day}日 {birth_hour}时"
        user_name_str = name if name else "有缘人"
        spirit_nums_str = f"{n1}, {n2}, {n3}"
        
        with st.spinner("宗师正在温茶冥想，为您解开这 78 张牌的奥秘..."):
            # 将抽到的牌传给 AI，保证 AI 解读的和屏幕显示的一致
            st.write_stream(call_coze_stream(user_question, user_name_str, full_birth_info, spirit_nums_str, selected_cards))
            
        st.markdown("---")
