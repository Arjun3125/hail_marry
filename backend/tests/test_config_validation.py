"""Tests for config.py — CORS parsing, startup settings, security defaults."""
import os
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"


class CORSParsingTests(unittest.TestCase):
    """Verify _parse_cors_origins handles all expected input shapes."""

    def setUp(self):
        from config import _parse_cors_origins
        self.parse = _parse_cors_origins

    def test_none_returns_fallback(self):
        result = self.parse(None, ["http://localhost:3000"])
        self.assertEqual(result, ["http://localhost:3000"])

    def test_none_without_fallback_returns_empty(self):
        result = self.parse(None)
        self.assertEqual(result, [])

    def test_list_input(self):
        result = self.parse(["https://a.com", "https://b.com"])
        self.assertEqual(result, ["https://a.com", "https://b.com"])

    def test_json_string(self):
        result = self.parse('["https://a.com","https://b.com"]')
        self.assertEqual(result, ["https://a.com", "https://b.com"])

    def test_csv_string(self):
        result = self.parse("https://a.com,https://b.com")
        self.assertEqual(result, ["https://a.com", "https://b.com"])

    def test_empty_string_returns_empty(self):
        result = self.parse("")
        self.assertEqual(result, [])

    def test_wrapped_quotes_stripped(self):
        result = self.parse('"https://a.com,https://b.com"')
        self.assertEqual(result, ["https://a.com", "https://b.com"])

    def test_single_origin(self):
        result = self.parse("https://mysite.com")
        self.assertEqual(result, ["https://mysite.com"])

    def test_spaces_trimmed(self):
        result = self.parse("  https://a.com ,  https://b.com  ")
        self.assertEqual(result, ["https://a.com", "https://b.com"])

    def test_invalid_type_raises(self):
        with self.assertRaises(ValueError):
            self.parse(12345)

    def test_app_settings_accepts_plain_env_origin(self):
        from config import AppSettings

        original = os.environ.get("APP_CORS_ORIGINS")
        os.environ["APP_CORS_ORIGINS"] = "https://proxy-notebooklm.vercel.app"
        try:
            settings = AppSettings()
            self.assertEqual(settings.cors_origins, ["https://proxy-notebooklm.vercel.app"])
        finally:
            if original is None:
                os.environ.pop("APP_CORS_ORIGINS", None)
            else:
                os.environ["APP_CORS_ORIGINS"] = original


class SecurityDefaultTests(unittest.TestCase):
    """Verify JWT secret enforcement behavior."""

    def test_debug_mode_generates_ephemeral_secret(self):
        from config import Settings
        os.environ["DEBUG"] = "true"
        s = Settings()
        self.assertTrue(len(s.auth.jwt_secret) >= 32)

    def test_non_debug_rejects_empty_secret(self):
        from config import Settings
        original_debug = os.environ.get("DEBUG")
        os.environ["JWT_SECRET"] = ""
        try:
            # Force non-debug via direct attribute override after init
            s = Settings()
            s.app.debug = False
            s.auth.jwt_secret = ""
            with self.assertRaises(ValueError):
                s._validate_security_defaults()
        finally:
            if original_debug:
                os.environ["DEBUG"] = original_debug
            os.environ.pop("JWT_SECRET", None)

    def test_non_debug_rejects_short_secret(self):
        from config import Settings
        s = Settings()
        s.app.debug = False
        s.auth.jwt_secret = "tooshort"
        with self.assertRaises(ValueError):
            s._validate_security_defaults()


if __name__ == "__main__":
    unittest.main()
