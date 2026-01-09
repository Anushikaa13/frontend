"""
Custom Streamlit components for advanced UI features
"""
import streamlit as st
import json
from typing import Dict, Any


def local_storage_get(key: str, default=None) -> Any:
    """
    Retrieve a value from browser localStorage
    Falls back to Streamlit session state if available
    """
    try:
        # Try to get from session state first (fallback)
        if f"localStorage_{key}" in st.session_state:
            value = st.session_state[f"localStorage_{key}"]
            # If default is an int and value is a string, try to convert
            if isinstance(default, int) and isinstance(value, str):
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return default
            return value
        return default
    except:
        return default


def local_storage_set(key: str, value: Any):
    """
    Store a value in browser localStorage via Streamlit session state
    """
    try:
        st.session_state[f"localStorage_{key}"] = value
        # Also store in JavaScript local storage via a hidden div
        st.markdown(f"""
            <script>
            localStorage.setItem('{key}', {json.dumps(value)});
            </script>
        """, unsafe_allow_html=True)
    except:
        st.session_state[f"localStorage_{key}"] = value


def custom_metric_card(label: str, value: str, delta: str = None, color: str = "blue"):
    """Custom metric card component"""
    delta_html = f"<span style='color: green; font-size: 12px;'>{delta}</span>" if delta else ""
    
    html = f"""
    <div style='
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid {color};
        margin: 10px 0;
    '>
        <h4 style='margin: 0; color: #666;'>{label}</h4>
        <h2 style='margin: 10px 0 5px 0; color: #333;'>{value}</h2>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def custom_button(label: str, icon: str = "➤") -> bool:
    """Custom styled button"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        return st.button(f"{icon} {label}", use_container_width=True)


def product_card(product: Dict[str, Any]) -> None:
    """Display product as a custom card"""
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(product.get('name', 'Unknown'))
            st.caption(product.get('description', ''))
            st.markdown(f"**Price:** ${product.get('price', 0):.2f}")
            st.markdown(f"**Quantity:** {product.get('quantity', 0)} units")
        
        with col2:
            st.metric("ID", product.get('id', 'N/A'))


def storage_info_widget():
    """Display storage statistics"""
    with st.expander("💾 Storage Info"):
        storage_items = [k for k in st.session_state.keys() if k.startswith("localStorage_")]
        st.write(f"Stored items: {len(storage_items)}")
        
        if storage_items:
            st.write("**Cached data:**")
            for item in storage_items:
                key_name = item.replace("localStorage_", "")
                st.caption(f"• {key_name}")
