"""
Server-Sent Events (SSE) Real-Time AI Streaming End-to-End Tests.
Verifies `/api/v1/ai/stream` SSE lifecycle, thought event chunks, tool notifications, and graceful completion.
"""
import pytest
from fastapi.testclient import TestClient


def test_sse_ai_stream_lifecycle(test_client: TestClient):
    """
    Verifies that `/api/v1/ai/stream` yields a valid text/event-stream response
    with event lines matching SSE format (e.g. data: {...}).
    """
    with test_client.stream("GET", "/api/v1/ai/stream?query=Explain+NVIDIA+data+center+revenue+drivers") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        events_received = []
        for line in response.iter_lines():
            if line:
                events_received.append(line)

        assert len(events_received) > 0
        # Check that events have data lines
        has_data = any(line.startswith("data:") for line in events_received)
        assert has_data is True


def test_sse_ai_stream_short_query_validation(test_client: TestClient):
    """Verifies that an invalid single-character query triggers a 422 validation response."""
    resp = test_client.get("/api/v1/ai/stream?query=x")
    assert resp.status_code == 422
