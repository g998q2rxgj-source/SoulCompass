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

def call_coze_stream(user_input, user_name, birth_info):
    """
    使用流式 (Stream) 请求
    ✅ 彻底修复 'str object has no attribute get' 报错
    ✅ 实现真正的打字机效果
    """
    headers = {
        "Authorization": f"Bearer {COZE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    full_prompt = f"我是{user_name}，出生于{birth_info}。我的问题是：{user_input}。请结合塔罗、星盘和易经为我进行深度解读。"

    data = {
        "bot_id": BOT_ID,
        "user_id": "user_123456",
        "stream": True,  # <--- 开启流式传输，修复的关键！
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
        # 开启 stream=True 后，我们需要用 iter_lines 来逐行读取
        response = requests.post(COZE_API_URL, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        # 这是一个生成器，它会一点点把文字“吐”出来给界面
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data:"):
                    json_str = decoded_line[5:] # 去掉开头的 "data:"
                    try:
                        event_data = json.loads(json_str)
                        # 只有当类型是 answer 时，才是我们要的回复内容
                        if event_data.get("type") == "answer" and "content" in event_data:
                            yield event_data["content"]
                    except:
                        pass
    except Exception as e:
        yield f"⚠️ 连接中断: {str(e)}"

# --- 侧边栏 ---
with st.sidebar:
    st.title("🔮 开启命运仪式")
    st.markdown("---")
    
    st.header("Step 1: 你的信息")
    name = st.text_input("你的名字 / Nickname", key="name")
    
    col1, col2, col3 = st.columns(3)
    with col1: birth_year = st.number_input("年", 1950, 2010, 1995)
    with col2: birth_month = st.number_input("月", 1, 12, 1)
    with col3: birth_day = st.number_input("日", 1, 31, 1)
        
    st.markdown("---")
    st.header("Step 2: 潜意识链接")
    st.info("默念问题，凭直觉调整灵数。")
    n1 = st.slider("灵数一", 0, 77, 7)
    n2 = st.slider("灵数二", 0, 77, 22)
    n3 = st.slider("灵数三", 0, 77, 45)

# --- 主页面 ---
st.title("🌌 SoulCompass 全息命运指引")
st.markdown("*连接东方易理与西方星象，为你显化当下的能量图景。*")

user_question = st.text_area("Step 3: 你想问宇宙什么问题？", height=100, placeholder="请输入你想占卜的具体问题...")
start_button = st.button("✨ 启动全息推演 ✨", type="primary", use_container_width=True)

if start_button:
    if not user_question:
        st.error("请先输入你的问题...")
    else:
        # 1. 翻牌仪式感 (先展示视觉，让后台先连一连)
        st.subheader("🎴 塔罗牌阵 (能量显化)")
        t1, t2, t3 = st.columns(3)
        card_back = load_image("assets/tarot/card_back.jpg")
        
        cards = [
            {"file": "assets/tarot/the_fool.jpg", "name": "愚人"},
            {"file": "assets/tarot/death.jpg", "name": "死神"},
            {"file": "assets/tarot/the_sun.jpg", "name": "太阳"}
        ]
        random_cards = random.sample(cards, 3)

        # 简单的翻牌动画
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

        # 2. 宗师解读 (使用 write_stream 实现真·打字机)
        st.subheader("🧙‍♂️ 宗师深度解读")
        st.markdown("---")
        
        # 准备用户信息
        birth_info = f"{birth_year}年{birth_month}月{birth_day}日"
        user_name_str = name if name else "探求者"
        
        # 这里直接调用流式函数，Streamlit 会自动把 yield 出来的内容像打字一样显示
        with st.spinner("正在接收宇宙信号..."):
            st.write_stream(call_coze_stream(user_question, user_name_str, birth_info))
        
        st.markdown("---")