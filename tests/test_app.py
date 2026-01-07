"""
Test suite for Streamlit Product Management App
Run with: pytest tests/test_app.py -v
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import config and api_client
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import requests


# ========================
# FIXTURES
# ========================
@pytest.fixture
def mock_products():
    """Mock products data"""
    return [
        {
            "id": 1,
            "name": "Laptop",
            "description": "High-performance laptop",
            "price": 999.99,
            "quantity": 5
        },
        {
            "id": 2,
            "name": "Mouse",
            "description": "Wireless mouse",
            "price": 29.99,
            "quantity": 50
        },
        {
            "id": 3,
            "name": "Keyboard",
            "description": "Mechanical keyboard",
            "price": 89.99,
            "quantity": 20
        }
    ]


@pytest.fixture
def mock_token():
    """Mock authentication token"""
    return "test_token_123abc"


@pytest.fixture
def mock_response_success():
    """Mock successful API response"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"access_token": "test_token"}
    return response


@pytest.fixture
def mock_response_error():
    """Mock failed API response"""
    response = Mock()
    response.status_code = 400
    response.json.return_value = {"detail": "Error message"}
    return response


# ========================
# API CLIENT TESTS
# ========================
class TestAPIClient:
    """Test API client functions"""

    @patch('api_client.requests.post')
    def test_signup_success(self, mock_post, mock_response_success):
        """Test successful signup"""
        import api_client
        
        mock_post.return_value = mock_response_success
        res = api_client.signup("testuser", "testpass")
        
        assert res.status_code == 200
        mock_post.assert_called_once()

    @patch('api_client.requests.post')
    def test_signup_error(self, mock_post, mock_response_error):
        """Test signup error"""
        import api_client
        
        mock_post.return_value = mock_response_error
        res = api_client.signup("testuser", "testpass")
        
        assert res.status_code == 400

    @patch('api_client.requests.post')
    def test_login_success(self, mock_post, mock_response_success):
        """Test successful login"""
        import api_client
        
        mock_post.return_value = mock_response_success
        res = api_client.login("testuser", "testpass")
        
        assert res.status_code == 200
        mock_post.assert_called_once()

    @patch('api_client.requests.post')
    def test_login_error(self, mock_post, mock_response_error):
        """Test login error"""
        import api_client
        
        mock_post.return_value = mock_response_error
        res = api_client.login("testuser", "testpass")
        
        assert res.status_code == 400

    @patch('api_client.requests.get')
    def test_fetch_products_success(self, mock_get, mock_products, mock_token):
        """Test successful product fetching"""
        import api_client
        
        response = Mock()
        response.json.return_value = mock_products
        response.raise_for_status.return_value = None
        mock_get.return_value = response
        
        result = api_client.fetch_products(
            mock_token, 0, 1000, "price", "asc", 0, 100
        )
        
        assert len(result) == 3
        assert result[0]["name"] == "Laptop"
        mock_get.assert_called_once()

    @patch('api_client.requests.post')
    def test_create_product_success(self, mock_post, mock_response_success, mock_token):
        """Test successful product creation"""
        import api_client
        
        mock_post.return_value = mock_response_success
        res = api_client.create_product(
            mock_token, "Test Product", "Description", 99.99, 10
        )
        
        assert res.status_code == 200
        mock_post.assert_called_once()

    @patch('api_client.requests.delete')
    def test_delete_product_success(self, mock_delete, mock_response_success, mock_token):
        """Test successful product deletion"""
        import api_client
        
        mock_delete.return_value = mock_response_success
        res = api_client.delete_product(mock_token, 1)
        
        assert res.status_code == 200
        mock_delete.assert_called_once()

    def test_auth_headers_with_token(self, mock_token):
        """Test auth headers generation with token"""
        import api_client
        
        headers = api_client.auth_headers(mock_token)
        
        assert "Authorization" in headers
        assert headers["Authorization"] == f"Bearer {mock_token}"

    def test_auth_headers_without_token(self):
        """Test auth headers generation without token"""
        import api_client
        
        headers = api_client.auth_headers(None)
        
        assert headers == {}

    def test_auth_headers_empty_token(self):
        """Test auth headers generation with empty token"""
        import api_client
        
        headers = api_client.auth_headers("")
        
        assert headers == {}


# ========================
# CONFIG TESTS
# ========================
class TestConfig:
    """Test configuration"""

    def test_api_base_url_default(self):
        """Test default API base URL"""
        import config
        assert config.API_BASE_URL == "http://localhost:8000"

    def test_request_timeout(self):
        """Test request timeout"""
        import config
        assert config.REQUEST_TIMEOUT == 10

    def test_cache_ttl(self):
        """Test cache TTL"""
        import config
        assert config.CACHE_TTL == 60

    def test_page_title(self):
        """Test page title"""
        import config
        assert config.PAGE_TITLE == "Product Management App"

    def test_layout(self):
        """Test layout"""
        import config
        assert config.LAYOUT == "wide"


# ========================
# DATA HANDLING TESTS
# ========================
class TestDataHandling:
    """Test data handling and transformations"""

    def test_products_to_dataframe(self, mock_products):
        """Test converting products to DataFrame"""
        df = pd.DataFrame(mock_products)
        
        assert len(df) == 3
        assert list(df.columns) == ["id", "name", "description", "price", "quantity"]
        assert df.loc[0, "name"] == "Laptop"

    def test_empty_dataframe(self):
        """Test empty DataFrame"""
        df = pd.DataFrame()
        
        assert df.empty
        assert len(df) == 0

    def test_dataframe_filtering(self, mock_products):
        """Test DataFrame filtering"""
        df = pd.DataFrame(mock_products)
        
        # Filter by price
        filtered = df[df["price"] > 50]
        
        assert len(filtered) == 2
        assert "Laptop" in filtered["name"].values
        assert "Keyboard" in filtered["name"].values

    def test_dataframe_sorting(self, mock_products):
        """Test DataFrame sorting"""
        df = pd.DataFrame(mock_products)
        
        # Sort by price ascending
        sorted_df = df.sort_values("price")
        
        assert sorted_df.iloc[0]["name"] == "Mouse"
        assert sorted_df.iloc[-1]["name"] == "Laptop"


# ========================
# INTEGRATION TESTS
# ========================
class TestIntegration:
    """Integration tests"""

    @patch('api_client.requests.post')
    @patch('api_client.requests.get')
    def test_signup_login_flow(self, mock_get, mock_post):
        """Test signup and login flow"""
        import api_client
        
        # Setup mocks
        signup_response = Mock()
        signup_response.status_code = 200
        signup_response.json.return_value = {"message": "User created"}
        
        login_response = Mock()
        login_response.status_code = 200
        login_response.json.return_value = {"access_token": "token_123"}
        
        mock_post.side_effect = [signup_response, login_response]
        
        # Test signup
        res1 = api_client.signup("newuser", "password123")
        assert res1.status_code == 200
        
        # Test login
        res2 = api_client.login("newuser", "password123")
        assert res2.status_code == 200
        assert res2.json()["access_token"] == "token_123"

    @patch('api_client.requests.post')
    @patch('api_client.requests.get')
    @patch('api_client.requests.delete')
    def test_full_product_flow(self, mock_delete, mock_get, mock_post, mock_products, mock_token):
        """Test full product CRUD flow"""
        import api_client
        
        # Create product
        create_response = Mock()
        create_response.status_code = 200
        mock_post.return_value = create_response
        
        res_create = api_client.create_product(
            mock_token, "New Product", "Desc", 99.99, 5
        )
        assert res_create.status_code == 200
        
        # Fetch products
        fetch_response = Mock()
        fetch_response.json.return_value = mock_products
        fetch_response.raise_for_status.return_value = None
        mock_get.return_value = fetch_response
        
        res_fetch = api_client.fetch_products(
            mock_token, 0, 1000, "price", "asc", 0, 100
        )
        assert len(res_fetch) == 3
        
        # Delete product
        delete_response = Mock()
        delete_response.status_code = 200
        mock_delete.return_value = delete_response
        
        res_delete = api_client.delete_product(mock_token, 1)
        assert res_delete.status_code == 200


# ========================
# ERROR HANDLING TESTS
# ========================
class TestErrorHandling:
    """Test error handling"""

    @patch('api_client.requests.post')
    def test_signup_connection_error(self, mock_post):
        """Test signup with connection error"""
        import api_client
        
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(requests.exceptions.ConnectionError):
            api_client.signup("testuser", "testpass")

    @patch('api_client.requests.get')
    def test_fetch_timeout_error(self, mock_get):
        """Test fetch with timeout error"""
        import api_client
        
        mock_get.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(requests.exceptions.Timeout):
            api_client.fetch_products("token", 0, 1000, "price", "asc", 0, 100)

    @patch('api_client.requests.post')
    def test_create_product_http_error(self, mock_post):
        """Test create product with HTTP error"""
        import api_client
        
        response = Mock()
        response.status_code = 500
        response.text = "Internal Server Error"
        mock_post.return_value = response
        
        res = api_client.create_product("token", "Product", "Desc", 99.99, 10)
        assert res.status_code == 500

    def test_invalid_dataframe_operation(self):
        """Test invalid DataFrame operation"""
        df = pd.DataFrame()
        
        # Should not raise error for empty DataFrame
        assert df.empty is True


# ========================
# EDGE CASE TESTS
# ========================
class TestEdgeCases:
    """Test edge cases"""

    def test_empty_username_signup(self):
        """Test signup with empty username"""
        import api_client
        
        # Should still make request - validation happens on backend
        with patch('api_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_post.return_value = mock_response
            
            res = api_client.signup("", "password")
            assert mock_post.called

    def test_special_characters_in_product_name(self, mock_token):
        """Test product with special characters"""
        import api_client
        
        with patch('api_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            res = api_client.create_product(
                mock_token, "Product!@#$%", "Desc", 99.99, 10
            )
            assert res.status_code == 200

    def test_very_large_quantity(self, mock_token):
        """Test product with very large quantity"""
        import api_client
        
        with patch('api_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            res = api_client.create_product(
                mock_token, "Product", "Desc", 99.99, 999999999
            )
            assert res.status_code == 200

    def test_zero_price(self, mock_token):
        """Test product with zero price"""
        import api_client
        
        with patch('api_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            res = api_client.create_product(
                mock_token, "Free Product", "Desc", 0.0, 10
            )
            assert res.status_code == 200

    def test_negative_price_handling(self, mock_token):
        """Test product with negative price (should be handled by backend)"""
        import api_client
        
        with patch('api_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_post.return_value = mock_response
            
            res = api_client.create_product(
                mock_token, "Invalid Product", "Desc", -99.99, 10
            )
            # Backend should reject this
            assert res.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
