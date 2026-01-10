import uuid
from unittest.mock import patch
from django.test import TestCase, Client

class FakeResponse:
    def __init__(self, data):
        self.data = data

class FakeQuery:
    def __init__(self, table_name, records):
        self.table_name = table_name
        self.records = records
        self._filters = []
    def select(self, *args, **kwargs):
        return self
    def eq(self, field, value):
        self._filters.append((field, value))
        return self
    def execute(self):
        # Very small filter simulation: if filtering by id, return match
        for f, v in self._filters:
            if f == 'id':
                found = [r for r in self.records if r.get('id') == str(v)]
                return FakeResponse(found)
            if f == 'domain':
                found = [r for r in self.records if r.get('domain') == v]
                return FakeResponse(found)
            if f == 'business_id':
                found = [r for r in self.records if r.get('business_id') == v]
                return FakeResponse(found)
        # default: return all
        return FakeResponse(self.records)

class FakeClient:
    def __init__(self, business_records, post_records):
        self.business_records = business_records
        self.post_records = post_records
    def table(self, name):
        if name == 'business_profiles':
            return FakeQuery(name, self.business_records)
        elif name == 'posts':
            return FakeQuery(name, self.post_records)
        else:
            return FakeQuery(name, [])

class ProductDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.shop_domain = 'myshop.localhost'

    @patch('storefront.views.get_supabase_client')
    def test_product_detail_renders(self, mock_client_fn):
        prod_id = uuid.uuid4()
        business = {'id': 'biz-1', 'domain': 'myshop', 'business_name': 'My Test Shop'}
        post = {
            'id': str(prod_id),
            'data': {
                'productName': 'Test Product',
                'productPrice': 1200,
                'productCurrency': 'USD',
                'images': ['https://example.com/image.jpg'],
                'textContent': 'A lovely test product',
            },
            'created_at': '2025-01-01T00:00:00Z'
        }

        mock_client_fn.return_value = FakeClient([business], [post])
 
        resp = self.client.get(f'/product/{prod_id}/', HTTP_HOST=self.shop_domain)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Test Product', resp.content)
        # Accessibility & layout checks
        self.assertIn(b'Buy now', resp.content)
        self.assertIn(b'alt="Test Product"', resp.content)
        self.assertIn(b'loading="eager"', resp.content)

    @patch('storefront.views.get_supabase_client')
    def test_product_not_found_raises_404(self, mock_client_fn):
        prod_id = uuid.uuid4()
        business = {'id': 'biz-1', 'domain': 'myshop', 'business_name': 'My Test Shop'}
        # posts list is empty
        mock_client_fn.return_value = FakeClient([business], [])

        resp = self.client.get(f'/product/{prod_id}/', HTTP_HOST=self.shop_domain)
        self.assertEqual(resp.status_code, 404)
