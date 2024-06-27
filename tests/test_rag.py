import unittest
from src.models.rag_model import RagModelWrapper

class TestRagModel(unittest.TestCase):
    def setUp(self):
        self.model = RagModelWrapper('mistralai/rag-model')

    def test_predict(self):
        result = self.model.predict("What is the capital of France?")
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
