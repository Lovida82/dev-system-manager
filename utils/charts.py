import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_status_pie(systems):
    """상태별 시스템 분포 파이 차트"""
    if not systems:
        return go.Figure()

    df = pd.DataFrame(systems)
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']

    # 상태별 색상 정의
    color_map = {
        '초기 개발': '#FF6B6B',
        '개발 중': '#4ECDC4',
        '테스트 필요': '#FFE66D',
        '운영 가능': '#95E1D3'
    }

    colors = [color_map.get(s, '#888888') for s in status_counts['status']]

    fig = go.Figure(data=[go.Pie(
        labels=status_counts['status'],
        values=status_counts['count'],
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='outside'
    )])

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(t=20, b=20, l=20, r=20),
        height=350
    )

    return fig


def create_progress_histogram(systems):
    """진행률 분포 히스토그램"""
    if not systems:
        return go.Figure()

    df = pd.DataFrame(systems)
    df['progress_pct'] = df['progress'] * 100

    fig = go.Figure(data=[go.Histogram(
        x=df['progress_pct'],
        nbinsx=10,
        marker_color='#0066CC',
        opacity=0.8
    )])

    fig.update_layout(
        xaxis_title='진행률 (%)',
        yaxis_title='시스템 수',
        bargap=0.1,
        margin=dict(t=20, b=40, l=40, r=20),
        height=350
    )

    fig.update_xaxes(range=[0, 100], dtick=10)

    return fig


def create_dept_bar(dept_distribution):
    """부서별 시스템 수 막대 그래프"""
    if not dept_distribution:
        return go.Figure()

    df = pd.DataFrame([
        {'department': k, 'count': v}
        for k, v in dept_distribution.items()
    ]).sort_values('count', ascending=True)

    fig = go.Figure(data=[go.Bar(
        x=df['count'],
        y=df['department'],
        orientation='h',
        marker_color='#0066CC',
        text=df['count'],
        textposition='outside'
    )])

    fig.update_layout(
        xaxis_title='시스템 수',
        yaxis_title='',
        margin=dict(t=20, b=40, l=100, r=40),
        height=350
    )

    return fig


def create_cost_pie(services):
    """서비스별 비용 비중 파이 차트"""
    if not services:
        return go.Figure()

    df = pd.DataFrame(services)

    fig = go.Figure(data=[go.Pie(
        labels=df['service_name'],
        values=df['monthly_cost'],
        hole=0.4,
        textinfo='label+percent',
        textposition='outside'
    )])

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(t=20, b=20, l=20, r=20),
        height=350
    )

    return fig


def create_monthly_trend(monthly_data):
    """월별 추이 라인 차트"""
    if not monthly_data:
        return go.Figure()

    df = pd.DataFrame(monthly_data)

    fig = go.Figure(data=[go.Scatter(
        x=df['month'],
        y=df['value'],
        mode='lines+markers',
        line=dict(color='#0066CC', width=2),
        marker=dict(size=8)
    )])

    fig.update_layout(
        xaxis_title='월',
        yaxis_title='금액 (USD)',
        margin=dict(t=20, b=40, l=60, r=20),
        height=350
    )

    return fig


def create_progress_gauge(progress):
    """진행률 게이지 차트"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=progress * 100,
        number={'suffix': '%'},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#0066CC"},
            'steps': [
                {'range': [0, 30], 'color': "#FF6B6B"},
                {'range': [30, 70], 'color': "#FFE66D"},
                {'range': [70, 100], 'color': "#95E1D3"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))

    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        height=200
    )

    return fig
