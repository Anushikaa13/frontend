"""
Geospatial mapping features using Folium and Streamlit
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import random
from typing import Dict, List


def create_warehouse_map(products: List[Dict]) -> None:
    """Create an interactive map showing warehouse locations"""
    
    # Default warehouse locations (demo data)
    warehouses = [
        {"name": "Main Warehouse", "lat": 40.7128, "lon": -74.0060, "city": "New York", "products": 250},
        {"name": "West Coast Hub", "lat": 37.7749, "lon": -122.4194, "city": "San Francisco", "products": 180},
        {"name": "Central Storage", "lat": 41.8781, "lon": -87.6298, "city": "Chicago", "products": 220},
    ]
    
    # Create base map centered on USA
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=4,
        tiles="OpenStreetMap"
    )
    
    # Add warehouse markers
    for warehouse in warehouses:
        popup_text = f"""
        <b>{warehouse['name']}</b><br>
        Location: {warehouse['city']}<br>
        Products: {warehouse['products']}
        """
        
        folium.Marker(
            location=[warehouse['lat'], warehouse['lon']],
            popup=folium.Popup(popup_text, max_width=250),
            icon=folium.Icon(color='blue', icon='warehouse', prefix='fa'),
            tooltip=warehouse['name']
        ).add_to(m)
    
    # Add circles for coverage areas
    for warehouse in warehouses:
        folium.Circle(
            location=[warehouse['lat'], warehouse['lon']],
            radius=50000,
            color='blue',
            fill=True,
            fillOpacity=0.1,
            popup=f"Coverage area: {warehouse['name']}"
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    st_folium(m, width=700, height=500)


def create_product_distribution_map(df: pd.DataFrame) -> None:
    """Create a heatmap of product distribution"""
    
    if df.empty:
        st.info("No data to display on map")
        return
    
    # Generate random coordinates for products (demo)
    coordinates = [
        [40.7128, -74.0060],  # NYC
        [34.0522, -118.2437],  # LA
        [41.8781, -87.6298],  # Chicago
        [29.7604, -95.3698],  # Houston
        [33.7490, -84.3880],  # Atlanta
    ]
    
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=4,
        tiles="OpenStreetMap"
    )
    
    # Add heatmap data
    heat_data = []
    for idx, product in df.iterrows():
        coord = coordinates[idx % len(coordinates)]
        quantity = product.get('quantity', 0)
        
        # Create marker with size based on quantity
        folium.CircleMarker(
            location=coord,
            radius=max(5, min(20, quantity / 10)),
            popup=f"{product.get('name', 'Product')}<br>Qty: {quantity}",
            color='red',
            fill=True,
            fillColor='red',
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    st_folium(m, width=700, height=500)


def create_supply_chain_map() -> None:
    """Interactive supply chain network map"""
    
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=4,
        tiles="CartoDB positron"
    )
    
    # Supply chain nodes
    nodes = [
        {"name": "Supplier", "lat": 35.6762, "lon": 139.6503, "type": "supplier"},
        {"name": "Port", "lat": 34.0522, "lon": -118.2437, "type": "port"},
        {"name": "Distribution", "lat": 39.7392, "lon": -104.9903, "type": "distribution"},
        {"name": "Retail", "lat": 40.7128, "lon": -74.0060, "type": "retail"},
    ]
    
    # Color mapping for node types
    colors = {
        "supplier": "green",
        "port": "blue",
        "distribution": "orange",
        "retail": "red"
    }
    
    # Add nodes
    for node in nodes:
        folium.Marker(
            location=[node['lat'], node['lon']],
            popup=node['name'],
            icon=folium.Icon(color=colors[node['type']], icon='info-sign'),
            tooltip=node['name']
        ).add_to(m)
    
    # Draw connections
    for i in range(len(nodes) - 1):
        start = nodes[i]
        end = nodes[i + 1]
        folium.PolyLine(
            locations=[[start['lat'], start['lon']], [end['lat'], end['lon']]],
            color='gray',
            weight=2,
            opacity=0.7
        ).add_to(m)
    
    st_folium(m, width=700, height=500)


def location_based_inventory() -> None:
    """Interactive inventory by location"""
    
    st.subheader("📍 Location-Based Inventory")
    
    locations = {
        "New York": {"lat": 40.7128, "lon": -74.0060, "inventory": 250},
        "Los Angeles": {"lat": 34.0522, "lon": -118.2437, "inventory": 180},
        "Chicago": {"lat": 41.8781, "lon": -87.6298, "inventory": 220},
        "Houston": {"lat": 29.7604, "lon": -95.3698, "inventory": 150},
        "Atlanta": {"lat": 33.7490, "lon": -84.3880, "inventory": 190},
    }
    
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=4,
        tiles="OpenStreetMap"
    )
    
    # Add heatmap layer
    heat_data = []
    for location, data in locations.items():
        heat_data.append([data['lat'], data['lon'], data['inventory']])
        
        folium.CircleMarker(
            location=[data['lat'], data['lon']],
            radius=15,
            popup=f"{location}<br>Inventory: {data['inventory']}",
            color='darkblue',
            fill=True,
            fillColor='lightblue',
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    st_folium(m, width=700, height=500)
