import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
import base64
import math

# 页面配置
st.set_page_config(
    page_title="光遇内容推广周报看板",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 数据目录
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ========== 抖音搜索指数数据（从截图模糊读取）==========
# 根据截图y轴刻度（200k-800k）模糊读取每天值
DOUYIN_SEARCH_INDEX = {
    "2026-03-15": 420000, "2026-03-16": 380000, "2026-03-17": 350000,
    "2026-03-18": 320000, "2026-03-19": 340000, "2026-03-20": 380000,
    "2026-03-21": 450000, "2026-03-22": 520000, "2026-03-23": 480000,
    "2026-03-24": 420000, "2026-03-25": 380000, "2026-03-26": 400000,
    "2026-03-27": 450000, "2026-03-28": 520000, "2026-03-29": 580000,
    "2026-03-30": 550000, "2026-03-31": 480000, "2026-04-01": 620000,
    "2026-04-02": 680000, "2026-04-03": 720000, "2026-04-04": 780000,
    "2026-04-05": 850000, "2026-04-06": 820000, "2026-04-07": 680000,
    "2026-04-08": 580000, "2026-04-09": 520000, "2026-04-10": 480000,
    "2026-04-11": 450000, "2026-04-12": 420000, "2026-04-13": 380000,
    "2026-04-14": 350000, "2026-04-15": 320000,
}

# ========== 周期配置 ==========
WEEKLY_PERIODS = {
    "4月": {
        "第一周": {"start": datetime(2026, 4, 1), "end": datetime(2026, 4, 4), "has_data": False},
        "第二周": {"start": datetime(2026, 4, 5), "end": datetime(2026, 4, 11), "has_data": True},
        "第三周": {"start": datetime(2026, 4, 12), "end": datetime(2026, 4, 18), "has_data": True},
        "第四周": {"start": datetime(2026, 4, 19), "end": datetime(2026, 4, 25), "has_data": False},
        "第五周": {"start": datetime(2026, 4, 26), "end": datetime(2026, 4, 30), "has_data": False},
    },
    "5月": {
        "第一周": {"start": datetime(2026, 5, 1), "end": datetime(2026, 5, 2), "has_data": False},
        "第二周": {"start": datetime(2026, 5, 3), "end": datetime(2026, 5, 9), "has_data": False},
        "第三周": {"start": datetime(2026, 5, 10), "end": datetime(2026, 5, 16), "has_data": False},
        "第四周": {"start": datetime(2026, 5, 17), "end": datetime(2026, 5, 23), "has_data": False},
        "第五周": {"start": datetime(2026, 5, 24), "end": datetime(2026, 5, 31), "has_data": False},
    }
}

# 侧边栏
st.sidebar.title("🎮 光遇周报看板")
st.sidebar.markdown("---")

# 初始化 session state
if "selected_month" not in st.session_state:
    st.session_state.selected_month = "4月"
if "selected_week" not in st.session_state:
    st.session_state.selected_week = "第二周"

# 周期选择 - 一级：月份
st.sidebar.markdown("### 📅 周期选择")

months = list(WEEKLY_PERIODS.keys())
for month in months:
    if st.sidebar.button(
        month, 
        key=f"month_{month}",
        use_container_width=True,
        type="primary" if month == st.session_state.selected_month else "secondary"
    ):
        st.session_state.selected_month = month
        for week in WEEKLY_PERIODS[month]:
            if WEEKLY_PERIODS[month][week]["has_data"]:
                st.session_state.selected_week = week
                break
        else:
            st.session_state.selected_week = list(WEEKLY_PERIODS[month].keys())[0]

selected_month = st.session_state.selected_month

# 二级：周次按钮组
st.sidebar.markdown("**选择周次**")
weeks = list(WEEKLY_PERIODS[selected_month].keys())

cols = st.sidebar.columns(3)
for i, week in enumerate(weeks):
    week_info = WEEKLY_PERIODS[selected_month][week]
    btn_label = week
    if not week_info["has_data"]:
        btn_label = f"{week} (空)"
    
    col_idx = i % 3
    if cols[col_idx].button(
        btn_label, 
        key=f"week_{selected_month}_{week}",
        use_container_width=True,
        type="primary" if week == st.session_state.selected_week else "secondary"
    ):
        st.session_state.selected_week = week

selected_week = st.session_state.selected_week

# 获取选中周期的日期范围
week_info = WEEKLY_PERIODS[selected_month][selected_week]
week_start = week_info["start"]
week_end = week_info["end"]

# 显示当前周期
st.sidebar.markdown("---")
st.sidebar.markdown(f"**当前周期：**{selected_month}{selected_week}")
st.sidebar.markdown(f"📅 {week_start.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}")

# 数据上传
st.sidebar.markdown("### 📤 数据上传")
uploaded_files = st.sidebar.file_uploader(
    "上传数据文件", 
    type=['csv', 'xlsx', 'xls'],
    accept_multiple_files=True,
    help="支持抖音、B站、小红书、小喇叭数据文件"
)

if uploaded_files:
    for file in uploaded_files:
        file_path = os.path.join(DATA_DIR, file.name)
        with open(file_path, 'wb') as f:
            f.write(file.getbuffer())
    st.sidebar.success(f"已上传 {len(uploaded_files)} 个文件")

# 主标题
st.title("🎮 光遇内容推广周报")
st.markdown(f"**周期：{selected_month}{selected_week}** ({week_start.strftime('%m/%d')} ~ {week_end.strftime('%m/%d')})")
st.markdown("---")

# 加载数据函数
def load_data():
    data = {}
    
    # 抖音视频作者数据
    video_file = [f for f in os.listdir(DATA_DIR) if '视频-作者分析' in f and f.endswith('.csv')]
    if video_file:
        data['抖音视频'] = pd.read_csv(os.path.join(DATA_DIR, video_file[0]))
    
    # 抖音直播数据
    live_file = [f for f in os.listdir(DATA_DIR) if '直播-主播分析' in f and f.endswith('.csv')]
    if live_file:
        data['抖音直播'] = pd.read_csv(os.path.join(DATA_DIR, live_file[0]))
    
    # 抖音视频榜单
    video_top_file = [f for f in os.listdir(DATA_DIR) if '视频榜单' in f and f.endswith('.csv')]
    if video_top_file:
        data['抖音爆款'] = pd.read_csv(os.path.join(DATA_DIR, video_top_file[0]))
    
    # B站花火品牌趋势
    b站品牌_file = [f for f in os.listdir(DATA_DIR) if '花火品牌趋势' in f and f.endswith('.csv')]
    if b站品牌_file:
        data['B站品牌'] = pd.read_csv(os.path.join(DATA_DIR, b站品牌_file[0]))
    
    # B站花火内容趋势
    b站内容_file = [f for f in os.listdir(DATA_DIR) if '花火-内容趋势' in f and f.endswith('.csv')]
    if b站内容_file:
        data['B站内容'] = pd.read_csv(os.path.join(DATA_DIR, b站内容_file[0]))
    
    # B站关联稿件
    b站稿件_file = [f for f in os.listdir(DATA_DIR) if '内容关联稿件' in f and f.endswith('.csv')]
    if b站稿件_file:
        data['B站爆款'] = pd.read_csv(os.path.join(DATA_DIR, b站稿件_file[0]))
    
    # 小红书千瓜数据
    xhs_file = [f for f in os.listdir(DATA_DIR) if '千瓜' in f and 'sky' in f and (f.endswith('.xls') or f.endswith('.xlsx'))]
    if xhs_file:
        data['小红书'] = pd.read_excel(os.path.join(DATA_DIR, xhs_file[0]))
    
    # 小红书爆款
    xhs_top_file = [f for f in os.listdir(DATA_DIR) if '千瓜top10' in f and (f.endswith('.xls') or f.endswith('.xlsx'))]
    if xhs_top_file:
        data['小红书爆款'] = pd.read_excel(os.path.join(DATA_DIR, xhs_top_file[0]))
    
    # 小喇叭数据
    小喇叭_files = [f for f in os.listdir(DATA_DIR) if '小喇叭' in f and (f.endswith('.xls') or f.endswith('.xlsx'))]
    for f in 小喇叭_files:
        if '第一周' in f:
            data['小喇叭W1'] = pd.read_excel(os.path.join(DATA_DIR, f))
        elif '第二周' in f:
            data['小喇叭W2'] = pd.read_excel(os.path.join(DATA_DIR, f))
    
    return data

# 加载数据
data = load_data()

# 计算环比
def calc_qoq(current, last):
    if pd.isna(current) or pd.isna(last):
        return None
    if last == 0:
        if current > 0:
            return 100.0  # 从0增长
        return 0.0
    return (current - last) / last * 100

# 计算抖音搜索指数周度数据
def calc_search_index(week_start, week_end):
    """计算本周和上周的搜索指数"""
    dates = []
    current = week_start
    while current <= week_end:
        dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    # 本周搜索指数总和
    本周指数 = sum(DOUYIN_SEARCH_INDEX.get(d, 0) for d in dates)
    
    # 上周日期
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_end - timedelta(days=7)
    last_dates = []
    current = last_week_start
    while current <= last_week_end:
        last_dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    上周指数 = sum(DOUYIN_SEARCH_INDEX.get(d, 0) for d in last_dates)
    
    return 本周指数, 上周指数

# ========== 一、大盘概览 ==========
st.header("一、大盘数据情况")

# 大盘指标卡片
col1, col2, col3, col4 = st.columns(4)

with col1:
    # 抖音搜索指数
    本周指数, 上周指数 = calc_search_index(week_start, week_end)
    环比 = calc_qoq(本周指数, 上周指数)
    环比_str = f"{环比:+.1f}%" if 环比 is not None else "-"
    st.metric("抖音搜索指数(周)", f"{int(本周指数/10000):,}万", 环比_str)

with col2:
    # 小喇叭投稿
    if '小喇叭W1' in data and '小喇叭W2' in data:
        w1_row = data['小喇叭W1'][data['小喇叭W1']['活动类型'] == '汇总']
        w2_row = data['小喇叭W2'][data['小喇叭W2']['活动类型'] == '汇总']
        if not w1_row.empty and not w2_row.empty:
            本周 = w2_row.iloc[0]['总发布/交付内容条数']
            上周 = w1_row.iloc[0]['总发布/交付内容条数']
            环比 = calc_qoq(本周, 上周)
            环比_str = f"{环比:+.1f}%" if 环比 is not None else "-"
            st.metric("总投稿量", f"{int(本周):,}", 环比_str)
        else:
            st.metric("总投稿量", "-", "-")
    else:
        st.metric("总投稿量", "-", "-")

with col3:
    # 小喇叭播放
    if '小喇叭W1' in data and '小喇叭W2' in data:
        w1_row = data['小喇叭W1'][data['小喇叭W1']['活动类型'] == '汇总']
        w2_row = data['小喇叭W2'][data['小喇叭W2']['活动类型'] == '汇总']
        if not w1_row.empty and not w2_row.empty:
            本周 = w2_row.iloc[0]['总播放/曝光/阅读量']
            上周 = w1_row.iloc[0]['总播放/曝光/阅读量']
            环比 = calc_qoq(本周, 上周)
            环比_str = f"{环比:+.1f}%" if 环比 is not None else "-"
            st.metric("总播放量", f"{int(本周/10000):,}万", 环比_str)
        else:
            st.metric("总播放量", "-", "-")
    else:
        st.metric("总播放量", "-", "-")

with col4:
    # 小喇叭互动
    if '小喇叭W1' in data and '小喇叭W2' in data:
        w1_row = data['小喇叭W1'][data['小喇叭W1']['活动类型'] == '汇总']
        w2_row = data['小喇叭W2'][data['小喇叭W2']['活动类型'] == '汇总']
        if not w1_row.empty and not w2_row.empty:
            本周 = w2_row.iloc[0]['总互动量']
            上周 = w1_row.iloc[0]['总互动量']
            环比 = calc_qoq(本周, 上周)
            环比_str = f"{环比:+.1f}%" if 环比 is not None else "-"
            st.metric("总互动量", f"{int(本周):,}", 环比_str)
        else:
            st.metric("总互动量", "-", "-")
    else:
        st.metric("总互动量", "-", "-")

st.markdown("---")

# ========== 1.1 抖音 ==========
with st.expander("📱 1.1 抖音", expanded=True):
    if '抖音视频' in data and '抖音直播' in data:
        # 指标卡片
        col1, col2, col3, col4 = st.columns(4)
        
        # 计算周度数据
        week_start_str = week_start.strftime('%Y-%m-%d')
        week_end_str = week_end.strftime('%Y-%m-%d')
        last_week_start = week_start - timedelta(days=7)
        last_week_end = week_end - timedelta(days=7)
        last_week_start_str = last_week_start.strftime('%Y-%m-%d')
        last_week_end_str = last_week_end.strftime('%Y-%m-%d')
        
        df_video = data['抖音视频'].copy()
        df_video['指标日期'] = df_video['指标日期'].astype(str)
        
        本周v = df_video[(df_video['指标日期'] >= week_start_str) & (df_video['指标日期'] <= week_end_str)]
        上周v = df_video[(df_video['指标日期'] >= last_week_start_str) & (df_video['指标日期'] <= last_week_end_str)]
        
        with col1:
            本周 = 本周v['游戏投稿UV'].sum()
            上周 = 上周v['游戏投稿UV'].sum()
            环比 = calc_qoq(本周, 上周)
            st.metric("视频投稿人数", f"{int(本周):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        with col2:
            本周 = 本周v['大盘作者贡献播放次数'].sum()
            上周 = 上周v['大盘作者贡献播放次数'].sum()
            环比 = calc_qoq(本周, 上周)
            st.metric("视频播放次数", f"{int(本周/10000):,}万", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        df_live = data['抖音直播'].copy()
        df_live['指标日期'] = df_live['指标日期'].astype(str)
        
        本周l = df_live[(df_live['指标日期'] >= week_start_str) & (df_live['指标日期'] <= week_end_str)]
        上周l = df_live[(df_live['指标日期'] >= last_week_start_str) & (df_live['指标日期'] <= last_week_end_str)]
        
        with col3:
            本周 = 本周l['大盘主播开播人数'].sum()
            上周 = 上周l['大盘主播开播人数'].sum()
            环比 = calc_qoq(本周, 上周)
            st.metric("直播开播人数", f"{int(本周):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        with col4:
            本周 = 本周l['大盘主播贡献看播人数'].sum()
            上周 = 上周l['大盘主播贡献看播人数'].sum()
            环比 = calc_qoq(本周, 上周)
            st.metric("直播看播人数", f"{int(本周):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        # 趋势图
        df_video['指标日期_dt'] = pd.to_datetime(df_video['指标日期'])
        
        fig = make_subplots(rows=2, cols=1, subplot_titles=('视频投稿UV趋势', '视频播放趋势'))
        
        fig.add_trace(
            go.Scatter(x=df_video['指标日期_dt'], y=df_video['游戏投稿UV'], 
                      mode='lines+markers', name='投稿UV', line=dict(color='#FF6B6B')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df_video['指标日期_dt'], y=df_video['大盘作者贡献播放次数'], 
                      mode='lines+markers', name='播放次数', line=dict(color='#4ECDC4')),
            row=2, col=1
        )
        
        fig.update_layout(height=500, showlegend=True, title_text="抖音数据趋势")
        st.plotly_chart(fig, use_container_width=True)
        
        # 爆款内容
        if '抖音爆款' in data:
            st.markdown("#### 本周爆款内容TOP10")
            df_top = data['抖音爆款'].copy()
            df_top['视频发布日期'] = pd.to_datetime(df_top['视频发布日期'])
            
            本周top = df_top[
                (df_top['视频发布日期'] >= pd.Timestamp(week_start)) & 
                (df_top['视频发布日期'] <= pd.Timestamp(week_end))
            ]
            
            有效视频 = 本周top[本周top['视频播放次数'] != '非推广挂载'].copy()
            有效视频['视频播放次数'] = pd.to_numeric(有效视频['视频播放次数'], errors='coerce')
            有效视频 = 有效视频.dropna(subset=['视频播放次数']).sort_values('视频播放次数', ascending=False).head(10)
            
            if not 有效视频.empty:
                for idx, row in 有效视频.iterrows():
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{row['作者昵称']}** (@{row['作者抖音号']})")
                            st.markdown(f"📝 {row['视频标题'][:50]}...")
                        with col2:
                            st.metric("播放量", f"{int(row['视频播放次数']):,}")
                            st.metric("活跃玩家播放", f"{int(row['活跃玩家播放次数']):,}")
                        
                        # 爆点分析
                        发布日期 = row['视频发布日期'].strftime('%m/%d')
                        标题 = row['视频标题']
                        爆点 = "清明假期/内容质量优秀" if '04-04' <= 发布日期 <= '04-06' else "日常优质内容"
                        if '竞速' in 标题 or '电影' in 标题:
                            爆点 = "竞速圈层/长视频IP"
                        elif '情感' in 标题 or '故事' in 标题:
                            爆点 = "情感共鸣/故事向"
                        st.info(f"🎯 爆点分析：{爆点}")
                        st.markdown("---")
            else:
                st.info("本周暂无有效爆款数据")
    else:
        st.info("暂无抖音数据，请上传数据文件")

# ========== 1.2 小红书 ==========
with st.expander("📕 1.2 小红书", expanded=True):
    if '小红书' in data:
        col1, col2, col3 = st.columns(3)
        
        df = data['小红书'].copy()
        df['时间'] = df['时间'].astype(str)
        
        week_start_num = week_start.strftime('%Y%m%d')
        week_end_num = week_end.strftime('%Y%m%d')
        last_week_start_num = last_week_start.strftime('%Y%m%d')
        last_week_end_num = last_week_end.strftime('%Y%m%d')
        
        本周 = df[(df['时间'] >= week_start_num) & (df['时间'] <= week_end_num)]
        上周 = df[(df['时间'] >= last_week_start_num) & (df['时间'] <= last_week_end_num)]
        
        with col1:
            本周val = 本周['当日笔记数'].sum()
            上周val = 上周['当日笔记数'].sum()
            环比 = calc_qoq(本周val, 上周val)
            st.metric("品牌相关笔记数", f"{int(本周val):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        with col2:
            本周val = 本周['当日互动数'].sum()
            上周val = 上周['当日互动数'].sum()
            环比 = calc_qoq(本周val, 上周val)
            st.metric("品牌相关互动数", f"{int(本周val):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        with col3:
            本周val = 本周['当日点赞数'].sum()
            上周val = 上周['当日点赞数'].sum()
            环比 = calc_qoq(本周val, 上周val)
            st.metric("品牌相关点赞量", f"{int(本周val):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        # 趋势图
        df['日期'] = pd.to_datetime(df['时间'], format='%Y%m%d')
        
        fig = make_subplots(rows=2, cols=1, subplot_titles=('笔记数趋势', '互动数趋势'))
        
        fig.add_trace(
            go.Scatter(x=df['日期'], y=df['当日笔记数'], 
                      mode='lines+markers', name='笔记数', line=dict(color='#FF6B6B')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df['日期'], y=df['当日互动数'], 
                      mode='lines+markers', name='互动数', line=dict(color='#4ECDC4')),
            row=2, col=1
        )
        
        fig.update_layout(height=500, showlegend=True, title_text="小红书数据趋势")
        st.plotly_chart(fig, use_container_width=True)
        
        # 爆款内容
        if '小红书爆款' in data:
            st.markdown("#### 本周爆款内容TOP10")
            df_top = data['小红书爆款'].copy()
            df_top['笔记发布时间'] = pd.to_datetime(df_top['笔记发布时间'])
            
            本周top = df_top[
                (df_top['笔记发布时间'] >= pd.Timestamp(week_start)) & 
                (df_top['笔记发布时间'] <= pd.Timestamp(week_end))
            ].head(10)
            
            if not 本周top.empty:
                for idx, row in 本周top.iterrows():
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{row['达人昵称']}** (粉丝: {int(row['粉丝数']):,})")
                            st.markdown(f"📝 {row['笔记标题']}")
                            st.markdown(f"🔗 [查看笔记]({row['笔记链接']})")
                        with col2:
                            st.metric("互动量", f"{int(row['互动量']):,}")
                            st.metric("点赞", f"{int(row['点赞']):,}")
                        
                        # 爆点分析
                        标题 = row['笔记标题']
                        爆点 = "优质内容"
                        if '竞速' in 标题 or '电影' in 标题:
                            爆点 = "竞速圈层/长视频IP"
                        elif '日常' in 标题 or '记录' in 标题:
                            爆点 = "日常记录/共鸣向"
                        st.info(f"🎯 爆点分析：{爆点}")
                        st.markdown("---")
            else:
                st.info("本周暂无爆款数据")
    else:
        st.info("暂无小红书数据，请上传数据文件")

# ========== 1.3 B站 ==========
with st.expander("📺 1.3 B站", expanded=True):
    if 'B站内容' in data:
        col1, col2, col3, col4 = st.columns(4)
        
        df = data['B站内容'].copy()
        df['日期'] = df['日期'].astype(str)
        
        本周 = df[(df['日期'] >= week_start_str) & (df['日期'] <= week_end_str)]
        上周 = df[(df['日期'] >= last_week_start_str) & (df['日期'] <= last_week_end_str)]
        
        with col1:
            本周val = 本周['内容指数'].mean()
            上周val = 上周['内容指数'].mean()
            环比 = calc_qoq(本周val, 上周val)
            st.metric("内容指数", f"{本周val:.2f}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        with col2:
            本周val = 本周['播放量指数'].mean()
            上周val = 上周['播放量指数'].mean()
            环比 = calc_qoq(本周val, 上周val)
            st.metric("播放指数", f"{本周val:.2f}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        with col3:
            本周val = 本周['互动量指数'].mean()
            上周val = 上周['互动量指数'].mean()
            环比 = calc_qoq(本周val, 上周val)
            st.metric("互动指数", f"{本周val:.2f}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        with col4:
            本周val = 本周['搜索量指数'].mean()
            上周val = 上周['搜索量指数'].mean()
            环比 = calc_qoq(本周val, 上周val)
            st.metric("搜索指数", f"{本周val:.2f}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        # 趋势图
        df['日期_dt'] = pd.to_datetime(df['日期'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['日期_dt'], y=df['内容指数'], 
                                mode='lines+markers', name='内容指数', line=dict(color='#FF6B6B')))
        fig.add_trace(go.Scatter(x=df['日期_dt'], y=df['播放量指数'], 
                                mode='lines+markers', name='播放指数', line=dict(color='#4ECDC4')))
        fig.add_trace(go.Scatter(x=df['日期_dt'], y=df['互动量指数'], 
                                mode='lines+markers', name='互动指数', line=dict(color='#45B7D1')))
        
        fig.update_layout(title="B站花火指数趋势", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 爆款内容
        if 'B站爆款' in data:
            st.markdown("#### 本周爆款内容TOP10")
            df_top = data['B站爆款'].sort_values('新增播放量', ascending=False).head(10)
            
            for idx, row in df_top.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{row['UP主名称']}** (粉丝: {int(row['UP主粉丝量（周期内日均粉丝量）']):,})")
                        st.markdown(f"📝 {row['稿件标题']}")
                        st.markdown(f"🔗 [查看稿件]({row['稿件URL']})")
                    with col2:
                        st.metric("播放量", f"{int(row['新增播放量']):,}")
                        st.metric("互动量", f"{int(row['新增互动量']):,}")
                    
                    # 爆点分析
                    标题 = row['稿件标题']
                    爆点 = "优质内容"
                    if 'Coser' in 标题 or '破防' in 标题:
                        爆点 = "趣味互动/破防向"
                    elif '竞速' in 标题 or '季指' in 标题:
                        爆点 = "竞速圈层/剧情向"
                    st.info(f"🎯 爆点分析：{爆点}")
                    st.markdown("---")
    else:
        st.info("暂无B站数据，请上传数据文件")

# ========== 1.4 快手 ==========
with st.expander("⚡ 1.4 快手", expanded=False):
    st.warning("⚠️ 快手平台无后台权限，仅展示小喇叭快手数据")
    
    # 从小喇叭数据提取快手数据
    if '小喇叭W1' in data and '小喇叭W2' in data:
        w1_ks = data['小喇叭W1'][(data['小喇叭W1']['活动类型'] == '草根小喇叭') & (data['小喇叭W1']['主要合作平台'] == '快手')]
        w2_ks = data['小喇叭W2'][(data['小喇叭W2']['活动类型'] == '草根小喇叭') & (data['小喇叭W2']['主要合作平台'] == '快手')]
        
        if not w1_ks.empty and not w2_ks.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                本周 = w2_ks.iloc[0]['总发布/交付内容条数']
                上周 = w1_ks.iloc[0]['总发布/交付内容条数']
                环比 = calc_qoq(本周, 上周)
                st.metric("小喇叭投稿量", f"{int(本周):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
            
            with col2:
                本周 = w2_ks.iloc[0]['总播放/曝光/阅读量']
                上周 = w1_ks.iloc[0]['总播放/曝光/阅读量']
                环比 = calc_qoq(本周, 上周)
                st.metric("小喇叭播放量", f"{int(本周/10000):,}万", f"{环比:+.1f}%" if 环比 is not None else "-")
            
            with col3:
                本周 = w2_ks.iloc[0]['总互动量']
                上周 = w1_ks.iloc[0]['总互动量']
                环比 = calc_qoq(本周, 上周)
                st.metric("小喇叭互动量", f"{int(本周):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
    else:
        st.info("暂无快手相关数据")

# ========== 二、达人投放情况 ==========
with st.expander("💰 二、达人投放情况", expanded=False):
    st.info("暂无投放数据")

# ========== 三、小喇叭数据情况 ==========
with st.expander("📢 三、小喇叭数据情况", expanded=True):
    if '小喇叭W1' in data and '小喇叭W2' in data:
        w1 = data['小喇叭W1']
        w2 = data['小喇叭W2']
        
        w1_row = w1[w1['活动类型'] == '汇总']
        w2_row = w2[w2['活动类型'] == '汇总']
        
        if not w1_row.empty and not w2_row.empty:
            # 指标卡片
            col1, col2, col3 = st.columns(3)
            
            with col1:
                本周 = w2_row.iloc[0]['总发布/交付内容条数']
                上周 = w1_row.iloc[0]['总发布/交付内容条数']
                环比 = calc_qoq(本周, 上周)
                st.metric("总投稿量", f"{int(本周):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
            
            with col2:
                本周 = w2_row.iloc[0]['总播放/曝光/阅读量']
                上周 = w1_row.iloc[0]['总播放/曝光/阅读量']
                环比 = calc_qoq(本周, 上周)
                st.metric("总播放量", f"{int(本周/10000):,}万", f"{环比:+.1f}%" if 环比 is not None else "-")
            
            with col3:
                本周 = w2_row.iloc[0]['总互动量']
                上周 = w1_row.iloc[0]['总互动量']
                环比 = calc_qoq(本周, 上周)
                st.metric("总互动量", f"{int(本周):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        # 分平台数据
        st.markdown("#### 分平台数据（草根小喇叭）")
        
        w2_platform = w2[(w2['活动类型'] == '草根小喇叭') & (w2['主要合作平台'] != '汇总')]
        w1_platform = w1[(w1['活动类型'] == '草根小喇叭') & (w1['主要合作平台'] != '汇总')]
        
        platform_data = []
        for platform in ['抖音', '快手', '小红书']:
            w2_p = w2_platform[w2_platform['主要合作平台'] == platform]
            w1_p = w1_platform[w1_platform['主要合作平台'] == platform]
            
            if not w2_p.empty:
                w2_row = w2_p.iloc[0]
                w1_row = w1_p.iloc[0] if not w1_p.empty else None
                
                本周投稿 = w2_row['总发布/交付内容条数']
                上周投稿 = w1_row['总发布/交付内容条数'] if w1_row is not None else 0
                投稿环比 = calc_qoq(本周投稿, 上周投稿)
                
                本周播放 = w2_row['总播放/曝光/阅读量']
                上周播放 = w1_row['总播放/曝光/阅读量'] if w1_row is not None else 0
                播放环比 = calc_qoq(本周播放, 上周播放)
                
                本周互动 = w2_row['总互动量']
                上周互动 = w1_row['总互动量'] if w1_row is not None else 0
                互动环比 = calc_qoq(本周互动, 上周互动)
                
                platform_data.append({
                    '平台': platform,
                    '投稿量': f"{int(本周投稿):,}",
                    '环比': f"{投稿环比:+.1f}%" if 投稿环比 is not None else "-",
                    '播放量': f"{int(本周播放/10000):,}万" if pd.notna(本周播放) else "-",
                    '播放环比': f"{播放环比:+.1f}%" if 播放环比 is not None else "-",
                    '互动量': f"{int(本周互动):,}",
                    '互动环比': f"{互动环比:+.1f}%" if 互动环比 is not None else "-"
                })
        
        if platform_data:
            st.dataframe(pd.DataFrame(platform_data), use_container_width=True, hide_index=True)
        
        # 约稿数据
        st.markdown("#### 创作者约稿数据")
        
        w1_yg = w1[w1['活动类型'] == '创作者约稿']
        w2_yg = w2[w2['活动类型'] == '创作者约稿']
        
        w1_yg_sum = w1_yg[w1_yg['主要合作平台'] == '汇总']
        w2_yg_sum = w2_yg[w2_yg['主要合作平台'] == '汇总']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            本周 = w2_yg_sum.iloc[0]['总发布/交付内容条数'] if not w2_yg_sum.empty else 0
            上周 = w1_yg_sum.iloc[0]['总发布/交付内容条数'] if not w1_yg_sum.empty else 0
            本周 = 0 if pd.isna(本周) else 本周
            上周 = 0 if pd.isna(上周) else 上周
            环比 = calc_qoq(本周, 上周)
            st.metric("约稿投稿量", f"{int(本周):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        with col2:
            本周 = w2_yg_sum.iloc[0]['总播放/曝光/阅读量'] if not w2_yg_sum.empty else 0
            上周 = w1_yg_sum.iloc[0]['总播放/曝光/阅读量'] if not w1_yg_sum.empty else 0
            本周 = 0 if pd.isna(本周) else 本周
            上周 = 0 if pd.isna(上周) else 上周
            环比 = calc_qoq(本周, 上周)
            st.metric("约稿播放量", f"{int(本周):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        with col3:
            本周 = w2_yg_sum.iloc[0]['总互动量'] if not w2_yg_sum.empty else 0
            上周 = w1_yg_sum.iloc[0]['总互动量'] if not w1_yg_sum.empty else 0
            本周 = 0 if pd.isna(本周) else 本周
            上周 = 0 if pd.isna(上周) else 上周
            环比 = calc_qoq(本周, 上周)
            st.metric("约稿互动量", f"{int(本周):,}", f"{环比:+.1f}%" if 环比 is not None else "-")
        
        # 小结
        st.markdown("#### 小结 & 优化方向")
        st.markdown("""
        - **亮点**：投稿量环比 +158.2%，播放量 +158.8%，互动量 +172.3%，清明假期带动内容爆发
        - **异常**：约稿投稿量从7条降至0条，需关注约稿活动推进情况
        - **优化方向**：下周关注假期后回落情况，保持内容激励节奏
        """)
    else:
        st.info("暂无小喇叭数据，请上传数据文件")

# 页脚
st.markdown("---")
st.markdown("*数据更新时间：{}*".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
