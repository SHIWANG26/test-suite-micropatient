"""
Custom Promptfoo Provider — Micropatient RAG Mock Provider.

This provider is called by promptfoo to get responses from the
Micropatient AI system. In mock mode, it returns responses from
the golden dataset.

See: https://promptfoo.dev/docs/providers/python/
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.client.llm_client import MicropatientLLMClient  # noqa: E402


def call_api(prompt: str, options: dict, context: dict) -> dict:
    """
    Promptfoo provider entry point.

    Args:
        prompt: The rendered prompt string.
        options: Provider configuration from promptfooconfig.yaml.
        context: Test case context including variables.

    Returns:
        dict with 'output' key containing the model response.
    """
    client = MicropatientLLMClient(mode="mock")

    # Extract the patient query from the prompt
    query = prompt
    if "PATIENT QUERY:" in prompt:
        query = prompt.split("PATIENT QUERY:")[-1].strip()

    response = client.query(query)

    return {
        "output": response.answer,
        "tokenUsage": {
            "total": response.tokens_used,
            "prompt": int(response.tokens_used * 0.3),
            "completion": int(response.tokens_used * 0.7),
        },
    }
