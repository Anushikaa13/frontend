"""
Interactive charts and visualizations using Plotly and Streamlit
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict


def interactive_price_distribution(df: pd.DataFrame):
    """Interactive price distribution chart"""
    if df.empty:
        st.info("No data to display")
        return
    
    fig = px.histogram(df, x='price', nbins=20, 
                       title='Price Distribution',
                       labels={'price': 'Price ($)', 'count': 'Products'},
                       color_discrete_sequence=['#636EFA'])
    fig.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)


def interactive_quantity_chart(df: pd.DataFrame):
    """Interactive quantity by product chart"""
    if df.empty:
        st.info("No data to display")
        return
    
    # Sort and take top 10 products
    top_df = df.nlargest(10, 'quantity')
    
    fig = px.bar(top_df, x='name', y='quantity',
                 title='Top 10 Products by Quantity',
                 labels={'quantity': 'Stock Quantity', 'name': 'Product'},
                 color='quantity', color_continuous_scale='Viridis')
    fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)


def price_vs_quantity_scatter(df: pd.DataFrame):
    """Scatter plot: Price vs Quantity"""
    if df.empty:
        st.info("No data to display")
        return
    
    fig = px.scatter(df, x='price', y='quantity', 
                     hover_name='name',
                     title='Price vs Quantity Analysis',
                     labels={'price': 'Price ($)', 'quantity': 'Quantity'},
                     size='price', color='quantity',
                     color_continuous_scale='Blues')
    fig.update_layout(height=500, hovermode='closest')
    st.plotly_chart(fig, use_container_width=True)


def product_pie_chart(df: pd.DataFrame):
    """Pie chart for quantity distribution by product"""
    if df.empty:
        st.info("No data to display")
        return
    
    top_df = df.nlargest(8, 'quantity')
    
    fig = px.pie(top_df, values='quantity', names='name',
                 title='Inventory Distribution (Top 8 Products)',
                 hole=0.3)  # Donut chart
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def product_stats_gauge(df: pd.DataFrame):
    """Gauge charts for key metrics"""
    if df.empty:
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_price = df['price'].mean()
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_price,
            title={'text': "Avg Price"},
            gauge={'axis': {'range': [0, df['price'].max()]},
                   'bar': {'color': "darkblue"},
                   'steps': [
                       {'range': [0, df['price'].max()*0.5], 'color': "lightgray"},
                       {'range': [df['price'].max()*0.5, df['price'].max()], 'color': "gray"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                                'thickness': 0.75, 'value': df['price'].max()}}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        total_quantity = df['quantity'].sum()
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_quantity,
            title={'text': "Total Stock"},
            gauge={'axis': {'range': [0, total_quantity*1.2]}}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        num_products = len(df)
        fig = go.Figure(go.Indicator(
            mode="number",
            value=num_products,
            title={'text': "Total Products"},
            number={'font': {'size': 40}}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)


def inventory_heatmap(df: pd.DataFrame):
    """Heatmap for inventory analysis"""
    if df.empty or len(df) < 2:
        st.info("Need at least 2 products to display heatmap")
        return
    
    # Create a sample matrix: products x price ranges
    price_ranges = pd.cut(df['price'], bins=5)
    heatmap_data = pd.crosstab(df['name'].head(10), price_ranges, 
                               values=df['quantity'], aggfunc='sum')
    heatmap_data = heatmap_data.fillna(0)  # Fill NaN values with 0
    
    fig = px.imshow(heatmap_data.values,
                    labels=dict(x="Price Range", y="Product", color="Quantity"),
                    x=heatmap_data.columns.astype(str),
                    y=heatmap_data.index,
                    color_continuous_scale="YlOrRd",
                    title="Inventory Heatmap")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def multi_chart_dashboard(df: pd.DataFrame):
    """Complete dashboard with multiple charts"""
    st.subheader("📊 Advanced Analytics Dashboard")
    
    # Tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Distribution", "📊 Quantity", "🔀 Correlation",
        "🍰 Breakdown", "🔥 Heatmap"
    ])
    
    with tab1:
        interactive_price_distribution(df)
    
    with tab2:
        interactive_quantity_chart(df)
        product_stats_gauge(df)
    
    with tab3:
        price_vs_quantity_scatter(df)
    
    with tab4:
        product_pie_chart(df)
    
    with tab5:
        inventory_heatmap(df)
