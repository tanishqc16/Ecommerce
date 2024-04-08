import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/')
    assert b'iPhone 13' in response.data
    assert b'MacBook Pro' in response.data
    assert b'iPad Air' in response.data

def test_all_products(client):
    response = client.get('/all_products')
    assert response.status_code == 200
    assert b'iPhone 13' in response.data
    assert b'MacBook Pro' in response.data
    assert b'iPad Air' in response.data

def test_add_product(client):
    data = {
        'name': 'Test Product',
        'price': 100,
        'description': 'This is a test product.'
    }
    response = client.post('/add_product', json=data)
    assert response.status_code == 201
    assert b'Test Product' in response.data

def test_search_products(client):
    response = client.get('/search_products?keyword=iPhone')
    assert response.status_code == 200
    assert b'iPhone 13' in response.data

def test_view_cart(client):
    response = client.get('/cart?user_id=1')
    assert response.status_code == 200
    assert b'cart_items' in response.data
    assert b'total_amount' in response.data

def test_add_to_cart(client):
    data = {
        'user_id': 1,
        'product_id': 4,
        'quantity': 2
    }
    response = client.post('/add_to_cart', json=data)
    assert response.status_code == 200
    assert b'4' in response.data

def test_delete_from_cart(client):
    data = {
        'user_id': 1,
        'product_id': 4
    }
    response = client.post('/delete_from_cart', json=data)
    assert response.status_code == 200
    assert b'4' not in response.data

if __name__ == "__main__":
    pytest.main(['-v'])
