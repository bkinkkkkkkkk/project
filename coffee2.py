# streamlit_coffee_health.py

import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# ------------------------
# 1️⃣ 页面标题
# ------------------------
st.set_page_config(page_title="Global Coffee Health Analysis", layout="wide")
st.title("☕ Global Coffee Health 数据分析可视化")
st.markdown("分析咖啡消费对睡眠、压力和健康的影响")

# ------------------------
# 2️⃣ 数据加载
# ------------------------
@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(r"synthetic_coffee_health_10000.csv")
    return df

data = load_data()

# ------------------------
# 3️⃣ 侧边栏筛选
# ------------------------
st.sidebar.header("筛选条件")
countries = st.sidebar.multiselect("选择国家", options=data['Country'].unique(), default=data['Country'].unique())
genders = st.sidebar.multiselect("选择性别", options=data['Gender'].unique(), default=data['Gender'].unique())
age_range = st.sidebar.slider("选择年龄范围", int(data['Age'].min()), int(data['Age'].max()), (20, 60))

filtered_data = data[(data['Country'].isin(countries)) &
                     (data['Gender'].isin(genders)) &
                     (data['Age'] >= age_range[0]) &
                     (data['Age'] <= age_range[1])]

# ⚠️ 防空判断
if filtered_data.empty:
    st.warning("⚠️ 当前筛选条件下没有数据，请调整条件。")
    st.stop()

# 复制一份避免覆盖
filtered_data = filtered_data.copy()
stress_level_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
filtered_data['Stress_Index'] = filtered_data['Stress_Level'].map(stress_level_mapping)

# ------------------------
# 4️⃣ 标签页布局
# ------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 KPI 概览", "🔍 健康分析", "🌍 全球地图", "📦 分类分析", "📈 深度探索"])

# ------------------------
# 📊 KPI 概览
# ------------------------
with tab1:
    st.subheader("关键指标 (KPI)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("平均咖啡摄入量 (cups/day)", round(filtered_data['Coffee_Intake'].mean(), 2))
    col2.metric("平均睡眠时长 (hours/day)", round(filtered_data['Sleep_Hours'].mean(), 2))
    col3.metric("平均压力指数", round(filtered_data['Stress_Index'].mean(), 2))
    col4.metric("平均 BMI", round(filtered_data['BMI'].mean(), 2))

# ------------------------
# 🔍 健康分析（改进版散点图）
# ------------------------
with tab2:
    st.subheader("咖啡摄入 vs 健康指标")

    health_metric = st.selectbox(
        "选择健康指标", 
        ['Sleep_Hours', 'Stress_Index', 'Heart_Rate', 'BMI']
    )

    # 绘制散点图
    fig_scatter = px.scatter(
        filtered_data,
        x='Coffee_Intake',
        y=health_metric,
        color='Gender',          # 用性别区分颜色
        size='Age',              # 用年龄映射点大小
        size_max=8,              # 最大点大小，避免重叠太大
        hover_data=['Country', 'Occupation'],
    )

    # 设置点透明度，减少重叠视觉干扰
    fig_scatter.update_traces(marker=dict(opacity=0.6))

    # 设置标题和布局
    fig_scatter.update_layout(
        title=f"咖啡摄入量 vs {health_metric}",
        xaxis_title="每日咖啡摄入量 (cups/day)",
        yaxis_title=health_metric,
        legend_title="性别"
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------
# 🌍 全球地图
# ------------------------
with tab3:
    st.subheader("全球平均咖啡消费热力图")
    country_avg = filtered_data.groupby('Country')['Coffee_Intake'].mean().reset_index()
    data_list = [
    {"name": row['Country'], "value": round(row['Coffee_Intake'], 2)}
    for _, row in country_avg.iterrows()
]
    
    # ECharts 配置
    option = {
    "tooltip": {"trigger": "item"},
    "visualMap": {
        "min": min(country_avg['Coffee_Intake']),
        "max": max(country_avg['Coffee_Intake']),
        "text": ["High", "Low"],
        "realtime": False,
        "calculable": True,
        "inRange": {"color": ["#FFE0B2", "#FF5722"]}
    },
    "series": [{
        "name": "平均咖啡摄入量",
        "type": "map",
        "map": "world",
        "roam": True,
        "emphasis": {"label": {"show": True}},
        "data": data_list
    }]
}

    #渲染地图
    st_echarts(option, height="600px")

# 📦 分类分析
# ------------------------
with tab4:
    # ------------------------
    # 7️⃣ 职业与咖啡摄入分布（改进版）
    # ------------------------
    st.subheader("职业与咖啡摄入对比")

    # 分组柱状图：更直观，展示均值
    occupation_avg = filtered_data.groupby(['Occupation', 'Gender'])['Coffee_Intake'].mean().reset_index()
    fig_bar = px.bar(
        occupation_avg,
        x='Occupation',
        y='Coffee_Intake',
        color='Gender',
        barmode='group',
        text_auto='.2f'
    )
    fig_bar.update_layout(
        xaxis_title="职业",
        yaxis_title="平均每日咖啡摄入量 (cups/day)"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # 可选：小提琴图（学术型，展示分布 + 箱线）
    with st.expander("展开查看：职业与咖啡摄入分布（小提琴图）"):
        fig_violin = px.violin(
            filtered_data,
            x='Occupation',
            y='Coffee_Intake',
            color='Gender',
            box=True,
            points="all"
        )
        fig_violin.update_layout(
            xaxis_title="职业",
            yaxis_title="每日咖啡摄入量分布"
        )
        st.plotly_chart(fig_violin, use_container_width=True)

    # ------------------------
    # 8️⃣ 咖啡与生活习惯分析（小提琴图版）
    # ------------------------
    st.subheader("咖啡与生活习惯分析")

    habit = st.selectbox(
        "选择生活习惯指标",
        ['Smoking', 'Alcohol_Consumption', 'Physical_Activity_Hours']
    )

    # 如果是连续变量 Physical_Activity_Hours，可以分箱处理，让小提琴图更好看
    if habit == 'Physical_Activity_Hours':
        filtered_data['Activity_Bins'] = pd.cut(
            filtered_data['Physical_Activity_Hours'],
            bins=[0, 2, 4, 6, 24],
            labels=["0-2h", "2-4h", "4-6h", "6h+"]
        )
        x_var = 'Activity_Bins'
    else:
        x_var = habit

    fig_habit = px.violin(
        filtered_data,
        x=x_var,
        y='Coffee_Intake',
        color='Gender',
        box=True,        # 显示箱线图
        points="all"     # 显示所有散点
    )
    fig_habit.update_layout(
        xaxis_title=habit if habit != 'Physical_Activity_Hours' else "每日运动时长区间",
        yaxis_title="每日咖啡摄入量 (cups/day)"
    )
    st.plotly_chart(fig_habit, use_container_width=True)

# ------------------------
# 📈 深度探索
# ------------------------
with tab5:
    st.subheader("健康指标相关性热力图")
    corr = filtered_data[['Coffee_Intake','Sleep_Hours','Stress_Index','Heart_Rate','BMI']].corr()
    fig_corr, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap="YlGnBu", ax=ax)
    st.pyplot(fig_corr)

    st.subheader("不同年龄段咖啡摄入与睡眠趋势")
    age_trend = filtered_data.groupby('Age')[['Coffee_Intake','Sleep_Hours']].mean().reset_index()
    fig_line = px.line(age_trend, x='Age', y=['Coffee_Intake','Sleep_Hours'])
    fig_line.update_layout(title="不同年龄段咖啡摄入与睡眠趋势")
    st.plotly_chart(fig_line, use_container_width=True)

# ------------------------
# 底部
# ------------------------
st.markdown("---")
st.markdown("数据来源：Global Coffee Health Dataset (Synthetic)")
st.markdown("作者： Name")



