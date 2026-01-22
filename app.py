import streamlit as st
import time
import os
from PIL import Image

# --- 1. 配置区域 ---
# ⚠️ 替换成你自己的 Token 和 Bot ID
COZE_API_TOKEN = "你的pat_开头的token" 
BOT_ID = "你的bot_id数字"
COZE_API_URL = "https://api.coze.com/v3/chat" 

# --- 页面基础设置 ---
st.set_page_config(
    page_title="灵犀占星 SoulCompass",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 工具函数：加载本地图片 ---
def load_image(path):
    """尝试加载本地图片，如果找不到则返回None"""
    if os.path.exists(path):
        return Image.open(path)
    else:
        return None

# --- 辅助函数：打字机文字效果 ---
def stream_text(text):
    """让文字像打字机一样一个字一个字蹦出来"""
    for word in text.split():
        yield word + " "
        time.sleep(0.05)

# --- 侧边栏：用户输入区 ---
with st.sidebar:
    st.title("🔮 开启命运仪式")
    st.markdown("---")
    
    st.header("Step 1: 你的信息")
    name = st.text_input("你的名字 / Nickname", key="name")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        birth_year = st.number_input("出生年", 1950, 2010, 1995)
    with col2:
        birth_month = st.number_input("月", 1, 12, 1)
    with col3:
        birth_day = st.number_input("日", 1, 31, 1)
        
    st.markdown("---")
    st.header("Step 2: 潜意识链接")
    st.info("深呼吸，默念你的问题，凭直觉输入 3 个数字。它们将决定你的塔罗牌阵。")
    n1 = st.slider("灵数一 (根源)", 0, 77, 7)
    n2 = st.slider("灵数二 (当下)", 0, 77, 22)
    n3 = st.slider("灵数三 (指引)", 0, 77, 45)

# --- 主页面区域 ---
st.title("🌌 SoulCompass 全息命运指引")
st.markdown("*连接东方易理与西方星象，为你显化当下的能量图景。*")

# 问题输入框
user_question = st.text_area("Step 3: 你想问宇宙什么问题？", height=100, placeholder="例如：我未来的事业发展方向在哪里？这段感情会有结果吗？")

# 开始按钮
start_button = st.button("✨ 启动全息推演 ✨", type="primary", use_container_width=True)

# --- 核心逻辑区 ---
if start_button:
    if not user_question:
        st.error("请先告诉宇宙你想问什么问题...")
    else:
        # ==========================
        # 1. 启动仪式：进度条加载
        # ==========================
        progress_text = "正在连接阿卡西记录... 正在校准星盘数据..."
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.02) # 模拟连接耗时
            my_bar.progress(percent_complete + 1, text=progress_text)
        
        my_bar.empty() # 加载条消失
        
        # ==========================
        # 2. 准备数据 (模拟 API 返回)
        # ==========================
        # 这里为了演示翻牌，我们手动指定了三张牌
        # 你的 assets/tarot/ 文件夹里必须有这些图片才能看到效果
        mock_coze_response = {
            "tarot_cards": [
                {"name": "The Fool", "file": "assets/tarot/the_fool.jpg", "desc": "过去：愚人 (The Fool)"},
                {"name": "Death", "file": "assets/tarot/death.jpg", "desc": "现在：死神 (Death)"},
                {"name": "The Sun", "file": "assets/tarot/the_sun.jpg", "desc": "未来：太阳 (The Sun)"}
            ],
            "yijing_file": "assets/yijing/qian.jpg",
            "zodiac_file": "assets/zodiac/capricorn.jpg",
            "full_text_reply": "亲爱的探求者，牌面显示你正处于一个巨大的转变期。愚人代表你刚刚开始一段未知的旅程，心中充满天真与勇气；死神并不代表终结，而是彻底的蜕变与重生..."
        }
        
        st.success("能量通道已建立，命运牌阵即将揭晓...")
        st.divider()

        # ==========================
        # 3. 🎴 动态翻牌特效 (核心)
        # ==========================
        st.subheader("🎴 塔罗牌阵 (潜意识投射)")
        
        # 布局三个位置
        t1, t2, t3 = st.columns(3)
        
        # 尝试加载牌背图片
        card_back = load_image("assets/tarot/card_back.jpg")
        
        # --- 阶段 A: 发牌 (全部显示背面) ---
        if card_back:
            # 创建三个空的占位符，先把牌背放上去
            with t1:
                p1 = st.empty()
                p1.image(card_back, caption="抽取中...", use_container_width=True)
            with t2:
                p2 = st.empty()
                p2.image(card_back, caption="抽取中...", use_container_width=True)
            with t3:
                p3 = st.empty()
                p3.image(card_back, caption="抽取中...", use_container_width=True)
            
            # 制造悬念
            time.sleep(1.0) 
            
            # --- 阶段 B: 翻牌 (一张张揭晓) ---
            
            # 翻开第一张
            img1 = load_image(mock_coze_response["tarot_cards"][0]["file"])
            if img1:
                p1.image(img1, caption=mock_coze_response["tarot_cards"][0]["desc"], use_container_width=True)
            else:
                p1.warning("图片缺失")
            
            time.sleep(0.8) # 停顿
            
            # 翻开第二张
            img2 = load_image(mock_coze_response["tarot_cards"][1]["file"])
            if img2:
                p2.image(img2, caption=mock_coze_response["tarot_cards"][1]["desc"], use_container_width=True)
            else:
                p2.warning("图片缺失")
                
            time.sleep(0.8) # 停顿
            
            # 翻开第三张
            img3 = load_image(mock_coze_response["tarot_cards"][2]["file"])
            if img3:
                p3.image(img3, caption=mock_coze_response["tarot_cards"][2]["desc"], use_container_width=True)
            else:
                p3.warning("图片缺失")
                
        else:
            # 如果没有 card_back.jpg，就直接显示结果，不搞动画了
            st.warning("提示：请在 assets/tarot/ 下放入 card_back.jpg 以启用翻牌动画")
            with t1:
                st.image(load_image(mock_coze_response["tarot_cards"][0]["file"]), caption="过去", use_container_width=True)
            with t2:
                st.image(load_image(mock_coze_response["tarot_cards"][1]["file"]), caption="现在", use_container_width=True)
            with t3:
                st.image(load_image(mock_coze_response["tarot_cards"][2]["file"]), caption="未来", use_container_width=True)

        st.divider()

        # ==========================
        # 4. 展示其他命理图
        # ==========================
        
        # 第一排：星盘 + 易经
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🪐 星盘能量")
            zodiac_img = load_image(mock_coze_response["zodiac_file"])
            if zodiac_img:
                st.image(zodiac_img, caption="本命星盘背景", use_container_width=True)
            else:
                st.info("星盘图未加载")
        
        with c2:
            st.subheader("☯️ 易经指引")
            gua_img = load_image(mock_coze_response["yijing_file"])
            if gua_img:
                st.image(gua_img, width=150, caption="乾为天")
            else:
                st.info("易经卦图未加载")

        # 第二排：紫微 + 奇门
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("📜 紫微斗数")
            ziwei_bg = load_image("assets/atmosphere/ziwei_bg.jpg")
            if ziwei_bg:
                st.image(ziwei_bg, caption="紫微命盘", use_container_width=True)
            else:
                st.info("紫微图未加载")
        
        with c4:
            st.subheader("🧭 奇门遁甲")
            qimen_bg = load_image("assets/atmosphere/qimen_bg.jpg")
            if qimen_bg:
                st.image(qimen_bg, caption="奇门时空盘", use_container_width=True)
            else:
                st.info("奇门图未加载")

        st.divider()

        # ==========================
        # 5. 文字报告 (打字机效果)
        # ==========================
        st.subheader("🧙‍♂️ 宗师深度解读报告")
        # 使用 write_stream 实现打字机效果
        st.write_stream(stream_text(mock_coze_response["full_text_reply"]))