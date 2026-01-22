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

# --- 页面配置 ---
st.set_page_config(
    page_title="灵犀占星 SoulCompass",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 工具函数 ---
def load_image(path):
    """加载本地图片，防止报错"""
    if os.path.exists(path):
        return Image.open(path)
    return None

def call_coze_ai(user_input, user_name, birth_info):
    """调用 Coze AI 获取真实解读"""
    headers = {
        "Authorization": f"Bearer {COZE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 构造发给 AI 的完整提示词
    full_prompt = f"我是{user_name}，出生于{birth_info}。我的问题是：{user_input}。请结合塔罗、星盘和易经为我进行深度解读。"

    data = {
        "bot_id": BOT_ID,
        "user_id": "user_123456",
        "stream": False, 
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
        response = requests.post(COZE_API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        response_data = response.json()
        
        # 提取 AI 的回答 (解析 Coze V3 格式)
        if "data" in response_data:
            for msg in reversed(response_data["data"]):
                if msg.get("type") == "answer":
                    return msg.get("content")
        
        return "🔮 宇宙信号连接微弱，请重试..."
        
    except Exception as e:
        return f"⚠️ 连接失败，错误信息: {str(e)}"

def stream_text(text):
    """打字机效果"""
    for word in text.split():
        yield word + " "
        time.sleep(0.05)

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

# --- 核心逻辑 ---
if start_button:
    if not user_question:
        st.error("请先输入你的问题...")
    else:
        # 1. 仪式感：显示进度条
        progress_text = "正在连接阿卡西记录... 正在请求宗师解读..."
        my_bar = st.progress(0, text=progress_text)
        
        # 2. 真实调用 AI
        birth_info = f"{birth_year}年{birth_month}月{birth_day}日"
        ai_reply = call_coze_ai(user_question, name if name else "探求者", birth_info)
        
        # 3. 进度条跑完
        my_bar.progress(100, text="能量图景已显化！")
        time.sleep(0.5)
        my_bar.empty()
        
        st.success("命运指引已送达。")
        st.divider()

        # 4. 视觉呈现 (翻牌动画)
        st.subheader("🎴 塔罗牌阵 (能量显化)")
        t1, t2, t3 = st.columns(3)
        card_back = load_image("assets/tarot/card_back.jpg")
        
        # 确保你有这些图片，否则会显示找不到
        cards = [
            {"file": "assets/tarot/the_fool.jpg", "name": "愚人"},
            {"file": "assets/tarot/death.jpg", "name": "死神"},
            {"file": "assets/tarot/the_sun.jpg", "name": "太阳"}
        ]
        # 随机排序以增加神秘感
        random_cards = random.sample(cards, 3)

        if card_back:
            # 先显示背面
            with t1: p1 = st.empty(); p1.image(card_back, use_container_width=True)
            with t2: p2 = st.empty(); p2.image(card_back, use_container_width=True)
            with t3: p3 = st.empty(); p3.image(card_back, use_container_width=True)
            
            # 依次翻开
            time.sleep(0.8)
            p1.image(load_image(random_cards[0]["file"]), caption=f"过去：{random_cards[0]['name']}", use_container_width=True)
            
            time.sleep(0.8)
            p2.image(load_image(random_cards[1]["file"]), caption=f"现在：{random_cards[1]['name']}", use_container_width=True)
            
            time.sleep(0.8)
            p3.image(load_image(random_cards[2]["file"]), caption=f"未来：{random_cards[2]['name']}", use_container_width=True)
        else:
            # 如果没有背面图，直接显示正面
            st.warning("提示：assets/tarot/card_back.jpg 未找到，跳过动画")
            t1.image(load_image(random_cards[0]["file"]), caption="过去", use_container_width=True)
            t2.image(load_image(random_cards[1]["file"]), caption="现在", use_container_width=True)
            t3.image(load_image(random_cards[2]["file"]), caption="未来", use_container_width=True)

        st.divider()

        # 5. 展示 AI 真实回答
        st.subheader("🧙‍♂️ 宗师深度解读")
        st.markdown("---")
        st.write_stream(stream_text(ai_reply))
        st.markdown("---")