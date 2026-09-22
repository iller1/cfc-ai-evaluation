from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from pro_beta.model_provider import ProviderError, openai_call


class _FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class OpenAIProviderTests(unittest.TestCase):
    def test_openai_call_uses_responses_api_and_preserves_boundary(self):
        payload = {
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "CFC answer",
                        }
                    ],
                }
            ],
        }
        with patch(
            "pro_beta.model_provider.urlopen",
            return_value=_FakeResponse(payload),
        ) as mocked:
            result = openai_call(
                api_key="secret-openai-key",
                model="gpt-5.6-terra",
                text="hello",
                mode="STANDARD",
                history=[{"role": "assistant", "content": "prior"}],
                hawm_state={"goal": "answer carefully"},
            )

        request = mocked.call_args.args[0]
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.full_url, "https://api.openai.com/v1/responses")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-openai-key")
        self.assertEqual(body["model"], "gpt-5.6-terra")
        self.assertEqual(body["input"][-1], {"role": "user", "content": "hello"})
        self.assertIn("Consistency / Closure Control", body["instructions"])
        self.assertIn("Human-AI Work Model", body["instructions"])
        self.assertEqual(result["text"], "CFC answer")
        self.assertEqual(result["provider"], "openai")
        self.assertEqual(result["model"], "gpt-5.6-terra")
        self.assertEqual(result["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(result["cfc_status"], "NOT_CONNECTED_C2")
        self.assertFalse(result["truncated"])

    def test_openai_call_requires_key(self):
        with self.assertRaises(ProviderError) as ctx:
            openai_call(
                api_key="",
                model="gpt-5.6-terra",
                text="hello",
                mode="STANDARD",
                history=[],
                hawm_state=None,
            )
        self.assertEqual(str(ctx.exception), "OPENAI_API_KEY_REQUIRED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
