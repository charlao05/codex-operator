"""Integração com WhatsApp Business API (Meta)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import httpx

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class WhatsAppAPI:
    """Cliente para enviar mensagens via WhatsApp Business API (Meta)."""

    def __init__(
        self,
        phone_number_id: str | None = None,
        access_token: str | None = None,
        api_version: str = "v22.0",
    ):
        """
        Inicializar cliente WhatsApp.

        :param phone_number_id: ID do número de telefone (Phone Number ID). Se não fornecido, usa WHATSAPP_PHONE_ID.
        :param access_token: Token de acesso. Se não fornecido, usa WHATSAPP_TOKEN.
        :param api_version: Versão da API do Facebook (padrão: v22.0).
        """
        self.phone_number_id = phone_number_id or os.getenv("WHATSAPP_PHONE_ID")
        self.access_token = access_token or os.getenv("WHATSAPP_TOKEN")
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"

        if not self.phone_number_id or not self.access_token:
            logger.error(
                "WhatsApp credentials not found. Set WHATSAPP_PHONE_ID and WHATSAPP_TOKEN."
            )
            raise ValueError(
                "WhatsApp credentials missing in environment or parameters."
            )

    def send_text_message(
        self, recipient_number: str, message_text: str
    ) -> Dict[str, Any]:
        """
        Enviar uma mensagem de texto simples.

        :param recipient_number: Número do destinatário (formato: +5511999999999).
        :param message_text: Conteúdo da mensagem.
        :return: Resposta da API (com message_id, status, etc.).
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_number,
            "type": "text",
            "text": {"body": message_text},
        }

        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                logger.info(
                    "Mensagem enviada para %s | message_id=%s",
                    recipient_number,
                    data.get("messages", [{}])[0].get("id"),
                )
                return data
        except httpx.HTTPError as e:
            logger.exception("Erro ao enviar mensagem WhatsApp: %s", e)
            return {"error": str(e), "status": "failed"}

    def send_template_message(
        self,
        recipient_number: str,
        template_name: str,
        template_language: str = "pt_BR",
    ) -> Dict[str, Any]:
        """
        Enviar uma mensagem usando um template pré-aprovado.

        :param recipient_number: Número do destinatário.
        :param template_name: Nome do template (ex: "hello_world", "invoice_notification").
        :param template_language: Código do idioma (padrão: pt_BR).
        :return: Resposta da API.
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": template_language},
            },
        }

        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                logger.info(
                    "Template enviado para %s | template=%s",
                    recipient_number,
                    template_name,
                )
                return data
        except httpx.HTTPError as e:
            logger.exception("Erro ao enviar template WhatsApp: %s", e)
            return {"error": str(e), "status": "failed"}

    def send_document_message(
        self,
        recipient_number: str,
        document_url: str,
        document_filename: str = "documento.pdf",
    ) -> Dict[str, Any]:
        """
        Enviar um documento/arquivo via WhatsApp.

        :param recipient_number: Número do destinatário.
        :param document_url: URL do documento (pública ou presigned).
        :param document_filename: Nome do arquivo (ex: "nota_fiscal.pdf").
        :return: Resposta da API.
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_number,
            "type": "document",
            "document": {
                "link": document_url,
                "filename": document_filename,
            },
        }

        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                logger.info(
                    "Documento enviado para %s | arquivo=%s",
                    recipient_number,
                    document_filename,
                )
                return data
        except httpx.HTTPError as e:
            logger.exception("Erro ao enviar documento WhatsApp: %s", e)
            return {"error": str(e), "status": "failed"}


def send_nf_notification(
    recipient_number: str,
    client_name: str,
    nf_value: float,
    custom_message: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Enviar notificação de nota fiscal via WhatsApp (exemplo prático).

    :param recipient_number: Número do cliente.
    :param client_name: Nome do cliente.
    :param nf_value: Valor da nota fiscal.
    :param custom_message: Mensagem customizada (se None, usa padrão).
    :return: Resposta da API.
    """
    api = WhatsAppAPI()

    if custom_message is None:
        custom_message = (
            f"Olá {client_name}! 👋\n\n"
            f"Sua nota fiscal foi gerada com sucesso!\n"
            f"💰 Valor: R$ {nf_value:.2f}\n\n"
            f"Qualquer dúvida, entre em contato!\n"
            f"Obrigado! 🙏"
        )

    return api.send_text_message(recipient_number, custom_message)


if __name__ == "__main__":
    # Teste local (requer WHATSAPP_TOKEN e WHATSAPP_PHONE_ID em .env)
    test_number = os.getenv("WHATSAPP_TEST_NUMBER", "+1 555 632 2287")
    try:
        api = WhatsAppAPI()
        result = api.send_text_message(
            test_number, "Teste de mensagem do CODEX-OPERATOR ✅"
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except ValueError as e:
        print(f"Erro: {e}")
