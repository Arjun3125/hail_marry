import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure backend imports resolve
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from auth.dependencies import is_demo_mode

class TestAuditFixes(unittest.TestCase):

    @patch("auth.dependencies.os.getenv")
    @patch("auth.dependencies.settings")
    def test_demo_mode_production_guard(self, mock_settings, mock_getenv):
        """Verify that demo mode is forced off in production."""
        mock_settings.app.demo_mode = True
        mock_settings.app.env = "local"

        def fake_getenv(key, default=None):
            if key == "APP_ENV":
                return "production"
            if key == "DEMO_MODE":
                return "true"
            return default

        mock_getenv.side_effect = fake_getenv
        self.assertFalse(is_demo_mode())

    def test_faiss_deletion_logic(self):
        """Test the new delete_document logic in TenantVectorStore."""
        from src.infrastructure.vector_store.vector_store import TenantVectorStore
        import numpy as np
        
        # Mock VECTOR_DIR to avoid writing to real disk
        with patch('src.infrastructure.vector_store.vector_store.VECTOR_DIR') as mock_dir:
            store = TenantVectorStore("test_tenant")
            store.index = MagicMock()
            store.index.ntotal = 10
            
            # 10 chunks, 5 for doc_A, 5 for doc_B
            store.metadata = [{"document_id": "doc_A"}] * 5 + [{"document_id": "doc_B"}] * 5
            
            # Mock vectors (10xEMBED_DIM)
            mock_vectors = np.random.rand(10, 128).astype('float32')
            store.index.reconstruct_n.return_value = mock_vectors
            
            # Delete doc_A
            store.delete_document("doc_A")
            
            # Assert metadata is filtered
            self.assertEqual(len(store.metadata), 5)
            self.assertTrue(all(m["document_id"] == "doc_B" for m in store.metadata))
            
            # Assert index was rebuilt with 5 vectors
            store.index.add.assert_called_once()
            added_vectors = store.index.add.call_args[0][0]
            self.assertEqual(len(added_vectors), 5)

if __name__ == "__main__":
    # Note: async test needs a runner, but for simplicity we'll just run the sync one
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAuditFixes)
    unittest.TextTestRunner().run(suite)
