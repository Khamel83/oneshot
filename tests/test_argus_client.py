"""Tests for core/search/argus_client.py."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.search import argus_client


class TestArgusClient:
    def test_get_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("ARGUS_API_KEY", "env-secret")
        assert argus_client.get_api_key() == "env-secret"

    def test_get_api_key_from_vault_fallback(self, monkeypatch):
        monkeypatch.delenv("ARGUS_API_KEY", raising=False)
        with (
            patch.object(argus_client, "_get_config", return_value={"search": {}}),
            patch.object(argus_client, "_load_api_key_from_vault", return_value="vault-secret"),
        ):
            assert argus_client.get_api_key() == "vault-secret"

    def test_search_sends_bearer_auth(self):
        response = MagicMock()
        response.read.return_value = json.dumps({"results": []}).encode()
        response.__enter__.return_value = response

        with (
            patch.object(argus_client, "get_base_url", return_value="http://argus.test"),
            patch.object(argus_client, "get_api_key", return_value="secret-token"),
            patch("urllib.request.urlopen", return_value=response) as mock_urlopen,
        ):
            result = argus_client.search("example")

        assert result == {"results": []}
        request = mock_urlopen.call_args.args[0]
        assert request.get_header("Authorization") == "Bearer secret-token"
        assert request.full_url == "http://argus.test/api/search"

    def test_build_research_pack_hits_workflow_endpoint(self):
        response = MagicMock()
        response.read.return_value = json.dumps({"run_id": "wf-1"}).encode()
        response.__enter__.return_value = response

        with (
            patch.object(argus_client, "get_base_url", return_value="http://argus.test"),
            patch.object(argus_client, "get_api_key", return_value="secret-token"),
            patch("urllib.request.urlopen", return_value=response) as mock_urlopen,
        ):
            result = argus_client.build_research_pack("sdk", official_url="https://docs.example.com")

        assert result == {"run_id": "wf-1"}
        request = mock_urlopen.call_args.args[0]
        assert request.full_url == "http://argus.test/api/workflows/build-research-pack"
