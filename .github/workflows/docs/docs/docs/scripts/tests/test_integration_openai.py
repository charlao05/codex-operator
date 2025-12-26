"""Integration tests for OpenAI LLM client using mocks."""
import os
from unittest.mock import Mock, patch, MagicMock
import pytest


@pytest.fixture
def mock_openai_key():
    """Fixture providing fake API key for tests."""
    return "sk-test-fake-key-12345"


@pytest.fixture
def mock_env(mock_openai_key):
    """Fixture mocking environment variables."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": mock_openai_key}):
        yield


@patch("openai.ChatCompletion.create")
def test_llm_client_call_success(mock_create):
    """Test successful API call with mocked OpenAI."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Resposta simulada"
    mock_create.return_value = mock_response
    
    # Simulate API call
    from src.llm_client import LLMClient
    client = LLMClient(api_key="sk-test-fake")
    response = client.call("Ola, como vai?")
    
    # Assertions
    assert response is not None
    mock_create.assert_called_once()
    assert "Resposta simulada" in str(response)


@patch("openai.ChatCompletion.create")
def test_llm_client_error_handling(mock_create):
    """Test error handling when API fails."""
    # Setup mock to raise exception
    mock_create.side_effect = Exception("API Error: rate limited")
    
    from src.llm_client import LLMClient
    client = LLMClient(api_key="sk-test-fake")
    
    # Should raise exception
    with pytest.raises(Exception):
        client.call("Test message")


@patch("openai.ChatCompletion.create")
def test_llm_client_initialization(mock_create, mock_env):
    """Test client initialization with mock API key."""
    from src.llm_client import LLMClient
    
    client = LLMClient()
    assert client is not None
    assert client.api_key == "sk-test-fake-key-12345"
