import streamlit as st
import time
import os
import requests
import json
from PIL import Image
import random

# ==================================================
# ✅ 你的配置已填好 (切勿修改)
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

def load_image(path):
    if os.path.exists(path):
        return Image.open(path)
    return None

def call_coze_stream(user_input, user_name, birth_info, spirit_numbers):
    """
    V8.0 核心修正：
    1. 彻底根治复读机问题 (使用思维链锁死结构)。
    2. 极度口语化，像真人对话，禁止使用列表格式。
    """
    headers = {
        "Authorization": f"Bearer {COZE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # === V8.0 宗师级 Prompt (防复读特制版) ===
    full_prompt = (
        f"【角色设定】\n"
        f"你叫'灵犀'，一位隐居深山的玄学宗师。你把用户当作自己最疼爱的晚辈。你的说话风格是：温暖、睿智、甚至带一点点老顽童的幽默。请完全摒弃机器人的说话方式，不要用'首先、其次、最后'，也不要用'1. 2. 3.'的列表。\n\n"
        f"【绝对禁令】\n"
        f"🛑 严禁内容重复！说完'寄语'后，立刻停止生成！绝对不要把前面的话再说一遍！\n"
        f"🛑 严禁使用'根据卦象显示'这种生硬的词，换成'孩子，你看这卦象...'。\n\n"
        f"【用户信息】\n"
        f"晚辈姓名：{user_name}\n"
        f"生辰八字：{birth_info}\n"
        f"抽取的灵数：{spirit_numbers} (直接解牌，不要问数字含义)\n\n"
        f"【晚辈的困惑】\n{user_input}\n\n"
        f"【回答结构 (请严格按此顺序，像写一封家书)】\n"
        f"第一段（暖场）：叫着他的名字，像老朋友一样寒暄两句，安抚他的情绪。\n"
        f"第二段（塔罗与潜意识）：告诉他，你透过塔罗牌看到了他心里藏着什么纠结？\n"
        f"第三段（易经与时运）：用大白话讲讲，现在的天时地利，是该'冲'还是该'稳'？\n"
        f"第四段（紫微与奇门）：结合他的命盘，指一条明路（比如'往南走'，或者'找个属猪的贵人'）。\n"
        f"第五段（宗师寄语）：送他一句简短有力的话作为结束，然后立刻停止！\n\n"
    )

    data = {
        "bot_id": BOT_ID,
        "user_id": f"user_{int(time.time())}", # 使用时间戳作为ID，强制每次都是新对话，防止AI记忆混乱导致复读
        "stream": True, 
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": full_prompt,
                "content_type": "text"
            }
        ]
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
        yield f"⚠️ 宗师正在闭关，连接微弱... ({str(e)})"

# --- 侧边栏 ---
with st.sidebar:
    st.title("🔮 开启命运仪式")
    st.markdown("---")
    
    st.header("Step 1: 你的信息")
    name = st.text_input("你的名字 / Nickname", key="name")
    
    gender = st.radio("性别 (排盘必要)", ["男", "女"], horizontal=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: birth_year = st.number_input("出生年", 1950, 2010, 1995)
    with col2: birth_month = st.number_input("月", 1, 12, 1)
    with col3: birth_day = st.number_input("日", 1, 31, 1)
    
    birth_hour = st.selectbox(
        "出生时辰 (排盘必要)",
        [
            "未知/不清楚",
            "子时 (23:00-01:00)", "丑时 (01:00-03:00)", "寅时 (03:00-05:00)",
            "卯时 (05:00-07:00)", "辰时 (07:00-09:00)", "巳时 (09:00-11:00)",
            "午时 (11:00-13:00)", "未时 (13:00-15:00)", "申时 (15:00-17:00)",
            "酉时 (17:00-19:00)", "戌时 (19:00-21:00)", "亥时 (21:00-23:00)"
        ]
    )
        
    st.markdown("---")
    st.header("Step 2: 潜意识链接")
    st.info("默念问题，凭直觉调整灵数。")
    n1 = st.slider("灵数一", 0, 99, 7)
    n2 = st.slider("灵数二", 0, 99, 22)
    n3 = st.slider("灵数三", 0, 99, 45)

# --- 主页面 ---
st.title("🌌 SoulCompass 全息命运指引")
st.markdown("*连接东方易理与西方星象，为你显化当下的能量图景。*")

user_question = st.text_area("Step 3: 你想问宇宙什么问题？", height=100, placeholder="例如：最近工作压力很大，我该坚持还是跳槽？")
start_button = st.button("✨ 启动全息推演 ✨", type="primary", use_container_width=True)

if start_button:
    if not user_question:
        st.error("孩子，你得先告诉我你心里在想什么...")
    else:
        # 1. 翻牌仪式感
        st.subheader("🎴 能量显化")
        t1, t2, t3 = st.columns(3)
        card_back = load_image("assets/tarot/card_back.jpg")
        
        cards = [
            {"file": "assets/tarot/the_fool.jpg", "name": "愚人"},
            {"file": "assets/tarot/death.jpg", "name": "死神"},
            {"file": "assets/tarot/the_sun.jpg", "name": "太阳"}
        ]
        random_cards = random.sample(cards, 3)

        if card_back:
            with t1: p1 = st.empty(); p1.image(card_back, use_container_width=True)
            with t2: p2 = st.empty(); p2.image(card_back, use_container_width=True)
            with t3: p3 = st.empty(); p3.image(card_back, use_container_width=True)
            time.sleep(0.5)
            p1.image(load_image(random_cards[0]["file"]), caption="过去", use_container_width=True)
            time.sleep(0.5)
            p2.image(load_image(random_cards[1]["file"]), caption="现在", use_container_width=True)
            time.sleep(0.5)
            p3.image(load_image(random_cards[2]["file"]), caption="未来", use_container_width=True)
        else:
             t1.image(load_image(random_cards[0]["file"]), use_container_width=True)
             t2.image(load_image(random_cards[1]["file"]), use_container_width=True)
             t3.image(load_image(random_cards[2]["file"]), use_container_width=True)

        st.divider()

        st.subheader("🧙‍♂️ 灵犀宗师的家书")
        st.markdown("---")
        
        full_birth_info = f"性别{gender}，出生于{birth_year}年{birth_month}月{birth_day}日，时辰为{birth_hour}"
        user_name_str = name if name else "有缘人"
        spirit_nums_str = f"{n1}, {n2}, {n3}"
        
        # 2. 调用 AI
        with st.spinner("宗师正在温茶冥想，为你起卦..."):
            st.write_stream(call_coze_stream(user_question, user_name_str, full_birth_info, spirit_nums_str))
        
        st.markdown("---")