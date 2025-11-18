"""Testes unitários para a integração WhatsApp API."""

import json
import pytest
from unittest.mock import MagicMock, patch
from src.integrations.whatsapp_api import WhatsAppAPI, send_nf_notification


def test_whatsapp_api_initialization():
    """Testar inicialização do cliente WhatsApp com credenciais corretas."""
    with patch.dict("os.environ", {
        "WHATSAPP_TOKEN": "test_token",
        "WHATSAPP_PHONE_ID": "123456",
    }):
        api = WhatsAppAPI()
        assert api.access_token == "test_token"
        assert api.phone_number_id == "123456"
        assert api.base_url == "https://graph.facebook.com/v22.0"


def test_whatsapp_api_missing_credentials():
    """Testar erro quando credenciais estão faltando."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="WhatsApp credentials missing"):
            WhatsAppAPI()


def test_send_text_message_success():
    """Testar envio de mensagem de texto com sucesso."""
    with patch.dict("os.environ", {
        "WHATSAPP_TOKEN": "test_token",
        "WHATSAPP_PHONE_ID": "123456",
    }):
        with patch("httpx.Client.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "messages": [{"id": "msg_123"}],
                "contacts": [{"input": "+55119999999", "wa_id": "5511999999"}],
            }
            mock_post.return_value = mock_response

            api = WhatsAppAPI()
            result = api.send_text_message("+55119999999", "Teste de mensagem")

            assert result["messages"][0]["id"] == "msg_123"
            # Verificar que a chamada HTTP foi feita corretamente
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "123456/messages" in call_args[0][0]
            assert call_args[1]["json"]["type"] == "text"


def test_send_text_message_failure():
    """Testar tratamento de erro ao enviar mensagem."""
    import httpx

    with patch.dict("os.environ", {
        "WHATSAPP_TOKEN": "test_token",
        "WHATSAPP_PHONE_ID": "123456",
    }):
        with patch("httpx.Client.post") as mock_post:
            mock_post.side_effect = httpx.HTTPError("Connection failed")

            api = WhatsAppAPI()
            result = api.send_text_message("+55119999999", "Teste")

            assert "error" in result
            assert result["status"] == "failed"


def test_send_template_message():
    """Testar envio de mensagem com template."""
    with patch.dict("os.environ", {
        "WHATSAPP_TOKEN": "test_token",
        "WHATSAPP_PHONE_ID": "123456",
    }):
        with patch("httpx.Client.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"messages": [{"id": "msg_456"}]}
            mock_post.return_value = mock_response

            api = WhatsAppAPI()
            result = api.send_template_message("+55119999999", "hello_world")

            assert result["messages"][0]["id"] == "msg_456"
            call_args = mock_post.call_args
            assert call_args[1]["json"]["type"] == "template"
            assert call_args[1]["json"]["template"]["name"] == "hello_world"


def test_send_nf_notification():
    """Testar função de notificação de nota fiscal."""
    with patch.dict("os.environ", {
        "WHATSAPP_TOKEN": "test_token",
        "WHATSAPP_PHONE_ID": "123456",
    }):
        with patch("httpx.Client.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"messages": [{"id": "msg_nf"}]}
            mock_post.return_value = mock_response

            result = send_nf_notification("+55119999999", "João", 250.0)

            assert result["messages"][0]["id"] == "msg_nf"
            # Verificar que o payload contém referência ao cliente e valor
            call_args = mock_post.call_args
            message_body = call_args[1]["json"]["text"]["body"]
            assert "João" in message_body
            assert "250.00" in message_body


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
