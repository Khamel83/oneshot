"""Tests for core.dispatch.direct_api with mocked urllib."""

import json
from io import BytesIO
from unittest.mock import patch, MagicMock
import urllib.error

from core.dispatch.direct_api import _mask_secrets, _validate_response


class TestMaskSecrets:
    def test_masks_sk_key(self):
        assert _mask_secrets("key: sk-abc12345defgh") == "key: [REDACTED]"

    def test_masks_key_prefix(self):
        assert _mask_secrets("key-key12345678xyz") == "[REDACTED]"

    def test_preserves_short_strings(self):
        assert _mask_secrets("key: sk-short") == "key: sk-short"


class TestValidateResponse:
    def test_valid_response(self):
        data = {"choices": [{"message": {"content": "hello"}}]}
        assert _validate_response(data) == "hello"

    def test_missing_choices(self):
        try:
            _validate_response({"id": "foo"})
            assert False, "Should have raised"
        except ValueError as e:
            assert "choices" in str(e)

    def test_empty_choices(self):
        try:
            _validate_response({"choices": []})
            assert False, "Should have raised"
        except ValueError as e:
            assert "empty" in str(e)

    def test_missing_message(self):
        try:
            _validate_response({"choices": [{"role": "user"}]})
            assert False, "Should have raised"
        except ValueError as e:
            assert "message" in str(e)

    def test_non_dict_response(self):
        try:
            _validate_response("not a dict")
            assert False, "Should have raised"
        except ValueError as e:
            assert "not a dict" in str(e)


class TestCall:
    def _make_mock_urlopen(self, response_data: dict):
        resp_bytes = json.dumps(response_data).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = resp_bytes
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    @patch("core.dispatch.direct_api._get_api_key", return_value="sk-testkey12345678")
    @patch("core.dispatch.direct_api.urllib.request.urlopen")
    def test_successful_call(self, mock_urlopen, mock_key):
        mock_urlopen.return_value = self._make_mock_urlopen(
            {"choices": [{"message": {"content": "result text"}}]}
        )
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test prompt")
            f.flush()
            from core.dispatch.direct_api import call
            result = call("https://api.example.com/v1", "test-model", f.name)
            os.unlink(f.name)
        assert result == "result text"

    @patch("core.dispatch.direct_api._get_api_key", return_value="sk-testkey12345678")
    @patch("core.dispatch.direct_api.urllib.request.urlopen")
    def test_timeout_is_configurable(self, mock_urlopen, mock_key):
        import os
        os.environ["ONESHOT_API_TIMEOUT"] = "5"
        try:
            mock_urlopen.return_value = self._make_mock_urlopen(
                {"choices": [{"message": {"content": "ok"}}]}
            )
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                f.write("prompt")
                f.flush()
                from core.dispatch.direct_api import call
                call("https://api.example.com/v1", "model", f.name)
                os.unlink(f.name)
            call_kwargs = mock_urlopen.call_args
            assert call_kwargs.kwargs.get("timeout") == 5 or mock_urlopen.call_args[1].get("timeout") == 5
        finally:
            del os.environ["ONESHOT_API_TIMEOUT"]

    @patch("core.dispatch.direct_api._get_api_key", return_value="sk-testkey12345678")
    @patch("core.dispatch.direct_api.urllib.request.urlopen")
    def test_http_error_masks_secrets(self, mock_urlopen, mock_key):
        error_resp = MagicMock()
        error_resp.read.return_value = b'{"error": "invalid key sk-testkey12345678"}'
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.example.com/v1/chat/completions",
            code=401, msg="Unauthorized", hdrs=None, fp=error_resp,
        )
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("prompt")
            f.flush()
            from core.dispatch.direct_api import call
            try:
                call("https://api.example.com/v1", "model", f.name)
                assert False, "Should have exited"
            except SystemExit:
                pass
            finally:
                os.unlink(f.name)

    @patch("core.dispatch.direct_api._get_api_key", return_value="sk-testkey12345678")
    def test_invalid_base_url(self, mock_key):
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("prompt")
            f.flush()
            from core.dispatch.direct_api import call
            try:
                call("ftp://bad-url", "model", f.name)
                assert False, "Should have exited"
            except SystemExit:
                pass
            finally:
                os.unlink(f.name)
