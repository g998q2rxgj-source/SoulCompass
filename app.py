import streamlit as st
import time
import os
import requests
import json
from PIL import Image
import random

# ==================================================
# ✅ 你的配置已自动填好 (切勿修改)
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
    V6.0: 
    1. 将灵数 (n1, n2, n3) 发送给 AI，防止 AI 重复提问。
    2. 强制 AI 按照五术全息结构回答，解决内容缺失和重复问题。
    """
    headers = {
        "Authorization": f"Bearer {COZE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # === 核心修改：构建超详细的 Prompt 指令 ===
    full_prompt = (
        f"【用户信息】\n"
        f"姓名：{user_name}\n"
        f"背景：{birth_info}\n"
        f"用户抽取的三个灵数是：{spirit_numbers} (请直接基于这三个数起卦，不要再问用户要数字)。\n\n"
        f"【用户问题】\n{user_input}\n\n"
        f"【回答要求】\n"
        f"请做一名精通东西方术数的宗师，严格按照以下结构进行全息解读，严禁内容重复，严禁废话：\n\n"
        f"1. 🔮 **【塔罗指引】**：根据灵数映射的塔罗牌意，解读潜意识现状。\n"
        f"2. ☯️ **【易经卦象】**：利用三个灵数起卦（上卦/下卦/变爻），解析当下的时运吉凶。\n"
        f"3. 📜 **【紫微斗数】**：根据提供的生辰时辰，分析命宫主星与流年运势的能量流动。\n"
        f"4. 🧭 **【奇门遁甲】**：分析当下的时空局势（开门/生门/休门方位），给出具体的行动策略。\n"
        f"5. 💡 **【宗师综合建议】**：结合以上四种术数，给出最终的定论和行动指南。\n"
        f"（注意：直接输出深度分析结果，不要打招呼，不要重复相同段落。）"
    )

    data = {
        "bot_id": BOT_ID,
        "user_id": "user_123456",
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
        yield f"⚠️ 连接中断: {str(e)}"

# --- 侧边栏：用户输入区 ---
with st.sidebar:
    st.title("🔮 开启命运仪式")
    st.markdown("---")
    
    st.header("Step 1: 你的信息")
    name = st.text_input("你的名字 / Nickname", key="name")
    
    # 性别
    gender = st.radio("性别 (排盘必要)", ["男", "女"], horizontal=True)
    
    # 出生日期
    col1, col2, col3 = st.columns(3)
    with col1: birth_year = st.number_input("出生年", 1950, 2010, 1995)
    with col2: birth_month = st.number_input("月", 1, 12, 1)
    with col3: birth_day = st.number_input("日", 1, 31, 1)
    
    # 出生时辰
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
    # 这里获取的 n1, n2, n3 之前没有发给 AI，现在修正了
    n1 = st.slider("灵数一", 0, 99, 7)
    n2 = st.slider("灵数二", 0, 99, 22)
    n3 = st.slider("灵数三", 0, 99, 45)

# --- 主页面 ---
st.title("🌌 SoulCompass 全息命运指引")
st.markdown("*连接东方易理与西方星象，为你显化当下的能量图景。*")

user_question = st.text_area("Step 3: 你想问宇宙什么问题？", height=100, placeholder="例如：我未来的事业运势如何？这段感情会有结果吗？")
start_button = st.button("✨ 启动全息推演 ✨", type="primary", use_container_width=True)

if start_button:
    if not user_question:
        st.error("请先输入你的问题...")
    else:
        # 1. 视觉展示 (卡牌动画)
        st.subheader("🎴 塔罗牌阵 (能量显化)")
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

        st.subheader("🧙‍♂️ 宗师深度解读")
        st.markdown("---")
        
        # === V6.0: 数据打包 ===
        # 1. 准备完整的出生信息
        full_birth_info = f"性别{gender}，出生于{birth_year}年{birth_month}月{birth_day}日，时辰为{birth_hour}"
        user_name_str = name if name else "探求者"
        
        # 2. 准备灵数信息 (这步是解决'一直问数字'的关键)
        spirit_nums_str = f"{n1}, {n2}, {n3}"
        
        # 3. 发送给 AI
        with st.spinner("正在排盘紫微斗数... 正在起卦易经..."):
            st.write_stream(call_coze_stream(user_question, user_name_str, full_birth_info, spirit_nums_str))
        
        st.markdown("---")