import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
import base64
import calendar

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

# ========== 周期配置 ==========
# 定义月份和周次的映射
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

# 月份按钮组
months = list(WEEKLY_PERIODS.keys())
for month in months:
    if st.sidebar.button(
        month, 
        key=f"month_{month}",
        use_container_width=True,
        type="primary" if month == st.session_state.selected_month else "secondary"
    ):
        st.session_state.selected_month = month
        # 切换月份时，重置到该月第一个有数据的周
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

# 导出HTML按钮
st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 导出报告")
if st.sidebar.button("导出HTML报告"):
    st.sidebar.info("请在浏览器中按 Ctrl+P (Windows) 或 Cmd+P (Mac) 保存为HTML")

# 主标题
st.title("🎮 光遇内容推广周报")
st.markdown(f"**周期：{selected_month}{selected_week}** ({week_start.strftime('%m/%d')} ~ {week_end.strftime('%m/%d')})")
st.markdown("---")

# 加载数据函数
@st.cache_data
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

# 计算本周/上周数据
def calc_weekly_metrics(data, week_start, week_end):
    """计算周度指标"""
    metrics = {}
    
    # 本周/上周日期
    week_start_str = week_start.strftime('%Y-%m-%d')
    week_end_str = week_end.strftime('%Y-%m-%d')
    
    # 上周日期（往前推7天）
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_end - timedelta(days=7)
    last_week_start_str = last_week_start.strftime('%Y-%m-%d')
    last_week_end_str = last_week_end.strftime('%Y-%m-%d')
    
    # 抖音数据
    if '抖音视频' in data:
        df = data['抖音视频']
        df['指标日期'] = df['指标日期'].astype(str)
        
        本周 = df[(df['指标日期'] >= week_start_str) & (df['指标日期'] <= week_end_str)]
        上周 = df[(df['指标日期'] >= last_week_start_str) & (df['指标日期'] <= last_week_end_str)]
        
        metrics['抖音投稿UV'] = {
            '本周': 本周['游戏投稿UV'].sum(),
            '上周': 上周['游戏投稿UV'].sum()
        }
        metrics['抖音播放'] = {
            '本周': 本周['大盘作者贡献播放次数'].sum(),
            '上周': 上周['大盘作者贡献播放次数'].sum()
        }
    
    if '抖音直播' in data:
        df = data['抖音直播']
        df['指标日期'] = df['指标日期'].astype(str)
        
        本周 = df[(df['指标日期'] >= week_start_str) & (df['指标日期'] <= week_end_str)]
        上周 = df[(df['指标日期'] >= last_week_start_str) & (df['指标日期'] <= last_week_end_str)]
        
        metrics['抖音开播'] = {
            '本周': 本周['大盘主播开播人数'].sum(),
            '上周': 上周['大盘主播开播人数'].sum()
        }
        metrics['抖音看播'] = {
            '本周': 本周['大盘主播贡献看播人数'].sum(),
            '上周': 上周['大盘主播贡献看播人数'].sum()
        }
    
    # 小红书数据
    if '小红书' in data:
        df = data['小红书']
        df['时间'] = df['时间'].astype(str)
        
        # 转换日期格式
        week_start_num = week_start.strftime('%Y%m%d')
        week_end_num = week_end.strftime('%Y%m%d')
        last_week_start_num = last_week_start.strftime('%Y%m%d')
        last_week_end_num = last_week_end.strftime('%Y%m%d')
        
        本周 = df[(df['时间'] >= week_start_num) & (df['时间'] <= week_end_num)]
        上周 = df[(df['时间'] >= last_week_start_num) & (df['时间'] <= last_week_end_num)]
        
        metrics['小红书笔记数'] = {
            '本周': 本周['当日笔记数'].sum(),
            '上周': 上周['当日笔记数'].sum()
        }
        metrics['小红书互动数'] = {
            '本周': 本周['当日互动数'].sum(),
            '上周': 上周['当日互动数'].sum()
        }
    
    # B站数据
    if 'B站内容' in data:
        df = data['B站内容']
        df['日期'] = df['日期'].astype(str)
        
        本周 = df[(df['日期'] >= week_start_str) & (df['日期'] <= week_end_str)]
        上周 = df[(df['日期'] >= last_week_start_str) & (df['日期'] <= last_week_end_str)]
        
        metrics['B站内容指数'] = {
            '本周': 本周['内容指数'].mean(),
            '上周': 上周['内容指数'].mean()
        }
        metrics['B站播放指数'] = {
            '本周': 本周['播放量指数'].mean(),
            '上周': 上周['播放量指数'].mean()
        }
    
    # 小喇叭数据
    if '小喇叭W1' in data and '小喇叭W2' in data:
        w1 = data['小喇叭W1'][data['小喇叭W1']['活动类型'] == '汇总'].iloc[0]
        w2 = data['小喇叭W2'][data['小喇叭W2']['活动类型'] == '汇总'].iloc[0]
        
        metrics['小喇叭投稿'] = {
            '本周': w2['总发布/交付内容条数'],
            '上周': w1['总发布/交付内容条数']
        }
        metrics['小喇叭播放'] = {
            '本周': w2['总播放/曝光/阅读量'],
            '上周': w1['总播放/曝光/阅读量']
        }
        metrics['小喇叭互动'] = {
            '本周': w2['总互动量'],
            '上周': w1['总互动量']
        }
    
    return metrics

metrics = calc_weekly_metrics(data, week_start, week_end)

# 计算环比
def calc_qoq(current, last):
    if last == 0:
        return 0
    return (current - last) / last * 100

# ========== 一、大盘概览 ==========
st.header("一、大盘数据情况")

# 大盘指标卡片
col1, col2, col3 = st.columns(3)

with col1:
    if '小喇叭投稿' in metrics:
        本周 = metrics['小喇叭投稿']['本周']
        上周 = metrics['小喇叭投稿']['上周']
        环比 = calc_qoq(本周, 上周)
        st.metric("总投稿量", f"{int(本周):,}", f"{环比:+.1f}%")
    else:
        st.metric("总投稿量", "-", "-")

with col2:
    if '抖音播放' in metrics and '小喇叭播放' in metrics:
        本周 = metrics['抖音播放']['本周'] + metrics['小喇叭播放']['本周']
        上周 = metrics['抖音播放']['上周'] + metrics['小喇叭播放']['上周']
        环比 = calc_qoq(本周, 上周)
        st.metric("总播放量", f"{int(本周):,}", f"{环比:+.1f}%")
    else:
        st.metric("总播放量", "-", "-")

with col3:
    if '小喇叭互动' in metrics:
        本周 = metrics['小喇叭互动']['本周']
        上周 = metrics['小喇叭互动']['上周']
        环比 = calc_qoq(本周, 上周)
        st.metric("总互动量", f"{int(本周):,}", f"{环比:+.1f}%")
    else:
        st.metric("总互动量", "-", "-")

st.markdown("---")

# ========== 1.1 抖音 ==========
with st.expander("📱 1.1 抖音", expanded=True):
    if '抖音视频' in data and '抖音直播' in data:
        # 指标卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if '抖音投稿UV' in metrics:
                本周 = metrics['抖音投稿UV']['本周']
                上周 = metrics['抖音投稿UV']['上周']
                环比 = calc_qoq(本周, 上周)
                st.metric("视频投稿人数", f"{int(本周):,}", f"{环比:+.1f}%")
        
        with col2:
            if '抖音播放' in metrics:
                本周 = metrics['抖音播放']['本周']
                上周 = metrics['抖音播放']['上周']
                环比 = calc_qoq(本周, 上周)
                st.metric("视频播放次数", f"{int(本周):,}", f"{环比:+.1f}%")
        
        with col3:
            if '抖音开播' in metrics:
                本周 = metrics['抖音开播']['本周']
                上周 = metrics['抖音开播']['上周']
                环比 = calc_qoq(本周, 上周)
                st.metric("直播开播人数", f"{int(本周):,}", f"{环比:+.1f}%")
        
        with col4:
            if '抖音看播' in metrics:
                本周 = metrics['抖音看播']['本周']
                上周 = metrics['抖音看播']['上周']
                环比 = calc_qoq(本周, 上周)
                st.metric("直播看播人数", f"{int(本周):,}", f"{环比:+.1f}%")
        
        # 趋势图
        df_video = data['抖音视频'].copy()
        df_video['指标日期'] = pd.to_datetime(df_video['指标日期'])
        
        fig = make_subplots(rows=2, cols=1, subplot_titles=('视频投稿UV趋势', '视频播放趋势'))
        
        fig.add_trace(
            go.Scatter(x=df_video['指标日期'], y=df_video['游戏投稿UV'], 
                      mode='lines+markers', name='投稿UV', line=dict(color='#FF6B6B')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df_video['指标日期'], y=df_video['大盘作者贡献播放次数'], 
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
            
            # 过滤本周
            本周top = df_top[
                (df_top['视频发布日期'] >= pd.Timestamp(week_start)) & 
                (df_top['视频发布日期'] <= pd.Timestamp(week_end))
            ]
            
            # 过滤有效播放数据
            有效视频 = 本周top[本周top['视频播放次数'] != '非推广挂载'].copy()
            有效视频['视频播放次数'] = pd.to_numeric(有效视频['视频播放次数'], errors='coerce')
            有效视频 = 有效视频.dropna(subset=['视频播放次数']).sort_values('视频播放次数', ascending=False).head(10)
            
            if not 有效视频.empty:
                有效视频['排名'] = range(1, len(有效视频) + 1)
                st.dataframe(
                    有效视频[['排名', '作者昵称', '视频标题', '视频播放次数', '活跃玩家播放次数']].rename(columns={
                        '作者昵称': '作者',
                        '视频标题': '标题',
                        '视频播放次数': '播放量',
                        '活跃玩家播放次数': '活跃玩家播放'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.info("暂无抖音数据，请上传数据文件")

# ========== 1.2 小红书 ==========
with st.expander("📕 1.2 小红书", expanded=True):
    if '小红书' in data:
        # 指标卡片
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if '小红书笔记数' in metrics:
                本周 = metrics['小红书笔记数']['本周']
                上周 = metrics['小红书笔记数']['上周']
                环比 = calc_qoq(本周, 上周)
                st.metric("品牌相关笔记数", f"{int(本周):,}", f"{环比:+.1f}%")
        
        with col2:
            if '小红书互动数' in metrics:
                本周 = metrics['小红书互动数']['本周']
                上周 = metrics['小红书互动数']['上周']
                环比 = calc_qoq(本周, 上周)
                st.metric("品牌相关互动数", f"{int(本周):,}", f"{环比:+.1f}%")
        
        with col3:
            # 点赞数
            df = data['小红书']
            df['时间'] = df['时间'].astype(str)
            week_start_num = week_start.strftime('%Y%m%d')
            week_end_num = week_end.strftime('%Y%m%d')
            last_week_start_num = (week_start - timedelta(days=7)).strftime('%Y%m%d')
            last_week_end_num = (week_end - timedelta(days=7)).strftime('%Y%m%d')
            
            本周 = df[(df['时间'] >= week_start_num) & (df['时间'] <= week_end_num)]
            上周 = df[(df['时间'] >= last_week_start_num) & (df['时间'] <= last_week_end_num)]
            
            本周点赞 = 本周['当日点赞数'].sum()
            上周点赞 = 上周['当日点赞数'].sum()
            环比 = calc_qoq(本周点赞, 上周点赞)
            st.metric("品牌相关点赞量", f"{int(本周点赞):,}", f"{环比:+.1f}%")
        
        # 趋势图
        df_xhs = data['小红书'].copy()
        df_xhs['日期'] = pd.to_datetime(df_xhs['时间'], format='%Y%m%d')
        
        fig = make_subplots(rows=2, cols=1, subplot_titles=('笔记数趋势', '互动数趋势'))
        
        fig.add_trace(
            go.Scatter(x=df_xhs['日期'], y=df_xhs['当日笔记数'], 
                      mode='lines+markers', name='笔记数', line=dict(color='#FF6B6B')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df_xhs['日期'], y=df_xhs['当日互动数'], 
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
                本周top['排名'] = range(1, len(本周top) + 1)
                st.dataframe(
                    本周top[['排名', '达人昵称', '笔记标题', '互动量', '点赞', '收藏']].rename(columns={
                        '达人昵称': '作者',
                        '笔记标题': '标题'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.info("暂无小红书数据，请上传数据文件")

# ========== 1.3 B站 ==========
with st.expander("📺 1.3 B站", expanded=True):
    if 'B站内容' in data:
        # 指标卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'B站内容指数' in metrics:
                本周 = metrics['B站内容指数']['本周']
                上周 = metrics['B站内容指数']['上周']
                环比 = calc_qoq(本周, 上周)
                st.metric("内容指数", f"{本周:.2f}", f"{环比:+.1f}%")
        
        with col2:
            if 'B站播放指数' in metrics:
                本周 = metrics['B站播放指数']['本周']
                上周 = metrics['B站播放指数']['上周']
                环比 = calc_qoq(本周, 上周)
                st.metric("播放指数", f"{本周:.2f}", f"{环比:+.1f}%")
        
        with col3:
            df = data['B站内容']
            df['日期'] = df['日期'].astype(str)
            week_start_str = week_start.strftime('%Y-%m-%d')
            week_end_str = week_end.strftime('%Y-%m-%d')
            last_week_start_str = (week_start - timedelta(days=7)).strftime('%Y-%m-%d')
            last_week_end_str = (week_end - timedelta(days=7)).strftime('%Y-%m-%d')
            
            本周 = df[(df['日期'] >= week_start_str) & (df['日期'] <= week_end_str)]
            上周 = df[(df['日期'] >= last_week_start_str) & (df['日期'] <= last_week_end_str)]
            
            本周互动 = 本周['互动量指数'].mean()
            上周互动 = 上周['互动量指数'].mean()
            环比 = calc_qoq(本周互动, 上周互动)
            st.metric("互动指数", f"{本周互动:.2f}", f"{环比:+.1f}%")
        
        with col4:
            本周搜索 = 本周['搜索量指数'].mean()
            上周搜索 = 上周['搜索量指数'].mean()
            环比 = calc_qoq(本周搜索, 上周搜索)
            st.metric("搜索指数", f"{本周搜索:.2f}", f"{环比:+.1f}%")
        
        # 趋势图
        df_b站 = data['B站内容'].copy()
        df_b站['日期_dt'] = pd.to_datetime(df_b站['日期'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_b站['日期_dt'], y=df_b站['内容指数'], 
                                mode='lines+markers', name='内容指数', line=dict(color='#FF6B6B')))
        fig.add_trace(go.Scatter(x=df_b站['日期_dt'], y=df_b站['播放量指数'], 
                                mode='lines+markers', name='播放指数', line=dict(color='#4ECDC4')))
        fig.add_trace(go.Scatter(x=df_b站['日期_dt'], y=df_b站['互动量指数'], 
                                mode='lines+markers', name='互动指数', line=dict(color='#45B7D1')))
        
        fig.update_layout(title="B站花火指数趋势", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 爆款内容
        if 'B站爆款' in data:
            st.markdown("#### 本周爆款内容TOP10")
            df_top = data['B站爆款'].sort_values('新增播放量', ascending=False).head(10)
            df_top['排名'] = range(1, len(df_top) + 1)
            st.dataframe(
                df_top[['排名', 'UP主名称', '稿件标题', '新增播放量', '新增互动量', '互动率（新增互动量/新增播放量）']].rename(columns={
                    'UP主名称': '作者',
                    '稿件标题': '标题',
                    '新增播放量': '播放量',
                    '新增互动量': '互动量',
                    '互动率（新增互动量/新增播放量）': '互动率'
                }),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("暂无B站数据，请上传数据文件")

# ========== 1.4 快手 ==========
with st.expander("⚡ 1.4 快手", expanded=False):
    st.info("暂无快手数据（集瓜账号未开通）")

# ========== 二、达人投放情况 ==========
with st.expander("💰 二、达人投放情况", expanded=False):
    st.info("暂无投放数据")

# ========== 三、小喇叭数据情况 ==========
with st.expander("📢 三、小喇叭数据情况", expanded=True):
    if '小喇叭W1' in data and '小喇叭W2' in data:
        w1 = data['小喇叭W1'][data['小喇叭W1']['活动类型'] == '汇总'].iloc[0]
        w2 = data['小喇叭W2'][data['小喇叭W2']['活动类型'] == '汇总'].iloc[0]
        
        # 指标卡片
        col1, col2, col3 = st.columns(3)
        
        with col1:
            本周 = w2['总发布/交付内容条数']
            上周 = w1['总发布/交付内容条数']
            环比 = calc_qoq(本周, 上周)
            st.metric("总投稿量", f"{int(本周):,}", f"{环比:+.1f}%")
        
        with col2:
            本周 = w2['总播放/曝光/阅读量']
            上周 = w1['总播放/曝光/阅读量']
            环比 = calc_qoq(本周, 上周)
            st.metric("总播放量", f"{int(本周):,}", f"{环比:+.1f}%")
        
        with col3:
            本周 = w2['总互动量']
            上周 = w1['总互动量']
            环比 = calc_qoq(本周, 上周)
            st.metric("总互动量", f"{int(本周):,}", f"{环比:+.1f}%")
        
        # 分平台数据
        st.markdown("#### 分平台数据")
        
        # 草根小喇叭分平台
        w2_platform = data['小喇叭W2'][
            (data['小喇叭W2']['活动类型'] == '草根小喇叭') & 
            (data['小喇叭W2']['主要合作平台'] != '汇总')
        ]
        w1_platform = data['小喇叭W1'][
            (data['小喇叭W1']['活动类型'] == '草根小喇叭') & 
            (data['小喇叭W1']['主要合作平台'] != '汇总')
        ]
        
        platform_data = []
        for platform in ['抖音', '快手', '小红书']:
            w2_p = w2_platform[w2_platform['主要合作平台'] == platform]
            w1_p = w1_platform[w1_platform['主要合作平台'] == platform]
            
            if not w2_p.empty and not w1_p.empty:
                w2_row = w2_p.iloc[0]
                w1_row = w1_p.iloc[0]
                
                platform_data.append({
                    '平台': platform,
                    '投稿量': f"{int(w2_row['总发布/交付内容条数']):,}",
                    '环比': f"{calc_qoq(w2_row['总发布/交付内容条数'], w1_row['总发布/交付内容条数']):+.1f}%",
                    '播放量': f"{int(w2_row['总播放/曝光/阅读量']):,}",
                    '播放环比': f"{calc_qoq(w2_row['总播放/曝光/阅读量'], w1_row['总播放/曝光/阅读量']):+.1f}%",
                    '互动量': f"{int(w2_row['总互动量']):,}",
                    '互动环比': f"{calc_qoq(w2_row['总互动量'], w1_row['总互动量']):+.1f}%"
                })
        
        if platform_data:
            st.dataframe(pd.DataFrame(platform_data), use_container_width=True, hide_index=True)
        
        # 小结
        st.markdown("#### 小结 & 优化方向")
        st.markdown("""
        - **亮点**：投稿量环比 +158.2%，播放量 +158.8%，互动量 +172.3%，清明假期带动内容爆发
        - **异常**：无
        - **优化方向**：下周关注假期后回落情况，保持内容激励节奏
        """)
    else:
        st.info("暂无小喇叭数据，请上传数据文件")

# 页脚
st.markdown("---")
st.markdown("*数据更新时间：{}*".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
