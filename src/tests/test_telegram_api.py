"""Testes unitários para a integração Telegram API."""

import json
import pytest
from unittest.mock import MagicMock, patch
from src.integrations.telegram_api import TelegramAPI, send_nf_notification


def test_telegram_api_initialization():
    """Testar inicialização do cliente Telegram com token correto."""
    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123456:ABC-DEF"}):
        api = TelegramAPI()
        assert api.bot_token == "123456:ABC-DEF"
        assert "123456:ABC-DEF" in api.base_url


def test_telegram_api_missing_token():
    """Testar erro quando token está faltando."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="Telegram bot token missing"):
            TelegramAPI()


def test_send_message_success():
    """Testar envio de mensagem com sucesso."""
    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123456:ABC"}):
        with patch("httpx.Client.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "ok": True,
                "result": {
                    "message_id": 42,
                    "chat": {"id": 987654321},
                    "text": "Teste",
                },
            }
            mock_post.return_value = mock_response

            api = TelegramAPI()
            result = api.send_message("987654321", "Teste de mensagem")

            assert result["ok"] is True
            assert result["result"]["message_id"] == 42
            mock_post.assert_called_once()


def test_send_message_failure():
    """Testar tratamento de erro ao enviar mensagem."""
    import httpx

    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123456:ABC"}):
        with patch("httpx.Client.post") as mock_post:
            mock_post.side_effect = httpx.HTTPError("Connection failed")

            api = TelegramAPI()
            result = api.send_message("987654321", "Teste")

            assert result["ok"] is False
            assert "error" in result


def test_send_message_api_error():
    """Testar resposta de erro da API Telegram."""
    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123456:ABC"}):
        with patch("httpx.Client.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "ok": False,
                "error_code": 400,
                "description": "Bad Request: message text is empty",
            }
            mock_post.return_value = mock_response

            api = TelegramAPI()
            result = api.send_message("987654321", "")

            assert result["ok"] is False
            assert "Bad Request" in result["error"]


def test_send_document():
    """Testar envio de documento."""
    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123456:ABC"}):
        with patch("httpx.Client.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "ok": True,
                "result": {"message_id": 43},
            }
            mock_post.return_value = mock_response

            api = TelegramAPI()
            result = api.send_document(
                "987654321",
                "https://example.com/doc.pdf",
                caption="Seu documento",
            )

            assert result["ok"] is True
            call_args = mock_post.call_args
            assert call_args[1]["json"]["document"] == "https://example.com/doc.pdf"


def test_send_photo():
    """Testar envio de foto."""
    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123456:ABC"}):
        with patch("httpx.Client.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "ok": True,
                "result": {"message_id": 44},
            }
            mock_post.return_value = mock_response

            api = TelegramAPI()
            result = api.send_photo(
                "987654321",
                "https://example.com/photo.jpg",
                caption="Sua foto",
            )

            assert result["ok"] is True


def test_send_nf_notification():
    """Testar função de notificação de nota fiscal."""
    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123456:ABC"}):
        with patch("httpx.Client.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "ok": True,
                "result": {"message_id": 45},
            }
            mock_post.return_value = mock_response

            result = send_nf_notification("987654321", "João", 250.0)

            assert result["ok"] is True
            # Verificar que o payload contém referência ao cliente e valor
            call_args = mock_post.call_args
            message_text = call_args[1]["json"]["text"]
            assert "João" in message_text
            assert "250.00" in message_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
