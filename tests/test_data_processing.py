import unittest
import pandas as pd
from data_processing.transform_data import clean_customer_data

class TestDataProcessing(unittest.TestCase):
    
    def test_clean_customer_data(self):
        # Sample test data
        test_data = pd.DataFrame({
            'customer_id': [1, 2],
            'email': ['TEST@EMAIL.COM', 'user@domain.com'],
            'country': ['US', 'UK']
        })
        
        result = clean_customer_data(test_data)
        
        # Test email normalization
        self.assertEqual(result['email'].iloc[0], 'test@email.com')

if __name__ == '__main__':
    unittest.main()