import unittest
import pandas as pd
from data_processing.transform_data import clean_customer_data

class TestCustomerData(unittest.TestCase):
    
    def test_clean_customer_data_removes_duplicates(self):
        # Test data with duplicate emails
        test_data = pd.DataFrame({
            'customer_id': [1, 2, 3],
            'email': ['test@email.com', 'test@email.com', 'unique@email.com'],
            'first_name': ['John', 'Jane', 'Bob']
        })
        
        result = clean_customer_data(test_data)
        
        # Should remove duplicate email
        self.assertEqual(len(result), 2)

if __name__ == '__main__':
    unittest.main()