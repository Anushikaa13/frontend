"""
API Client module - Handles all backend API calls
"""
import requests
from config import API_BASE_URL, REQUEST_TIMEOUT


def auth_headers(token):
    """Generate authorization headers"""
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def signup(username, password):
    """Signup new user"""
    try:
        res = requests.post(
            f"{API_BASE_URL}/signup",
            json={"username": username, "password": password},
            timeout=REQUEST_TIMEOUT
        )
        return res
    except requests.exceptions.RequestException as e:
        # Return a mock response object with error info
        class ErrorResponse:
            status_code = 500
            text = str(e)
            def json(self):
                return {"detail": str(e)}
        return ErrorResponse()


def login(username, password):
    """Login user and get token"""
    try:
        res = requests.post(
            f"{API_BASE_URL}/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=REQUEST_TIMEOUT
        )
        return res
    except requests.exceptions.RequestException as e:
        # Return a mock response object with error info
        class ErrorResponse:
            status_code = 500
            text = str(e)
            def json(self):
                return {"detail": str(e)}
        return ErrorResponse()


def create_product(token, name, description, price, quantity):
    """Create new product"""
    res = requests.post(
        f"{API_BASE_URL}/products",
        json={
            "name": name,
            "description": description,
            "price": price,
            "quantity": quantity
        },
        headers=auth_headers(token)
    )
    return res


def fetch_products(token, min_price, max_price, sort_by, sort_order, skip, limit):
    """Fetch products with filters and pagination"""
    params = {
        "min_price": min_price,
        "max_price": max_price,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "skip": skip,
        "limit": limit
    }

    headers = auth_headers(token)

    res = requests.get(
        f"{API_BASE_URL}/products",
        params=params,
        headers=headers,
        timeout=REQUEST_TIMEOUT
    )

    res.raise_for_status()
    return res.json()


def delete_product(token, product_id):
    """Delete product by ID"""
    res = requests.delete(
        f"{API_BASE_URL}/products/{product_id}",
        headers=auth_headers(token)
    )
    return res
