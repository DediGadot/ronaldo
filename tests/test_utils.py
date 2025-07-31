import unittest
from app.utils import shuffle_part_results

class TestShuffleAlgorithm(unittest.TestCase):
    def test_shuffle_balanced(self):
        """Test that shuffling produces balanced results from both sources"""
        ebay_parts = [{'id': i, 'source': 'eBay'} for i in range(1, 11)]
        ali_parts = [{'id': i, 'source': 'AliExpress'} for i in range(11, 21)]
        
        shuffled = shuffle_part_results(ebay_parts, ali_parts)
        
        # Check we have all items
        self.assertEqual(len(shuffled), 20)
        
        # Check we have a balanced mixture
        ebay_count = ali_count = 0
        for part in shuffled:
            if part['source'] == 'eBay':
                ebay_count += 1
            else:
                ali_count += 1
        
        self.assertAlmostEqual(ebay_count, 10, delta=3)
        self.assertAlmostEqual(ali_count, 10, delta=3)
        
    def test_shuffle_uneven(self):
        """Test shuffling with uneven number of parts"""
        ebay_parts = [{'id': i, 'source': 'eBay'} for i in range(1, 5)]
        ali_parts = [{'id': i, 'source': 'AliExpress'} for i in range(11, 16)]
        
        shuffled = shuffle_part_results(ebay_parts, ali_parts)
        self.assertEqual(len(shuffled), 9)
        
if __name__ == '__main__':
    unittest.main()