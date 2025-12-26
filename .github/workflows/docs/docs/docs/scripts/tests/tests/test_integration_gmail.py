"""Integration tests for Gmail email client using mocks."""
import os
from unittest.mock import Mock, patch, MagicMock
import pytest


@patch("smtplib.SMTP_SSL")
def test_gmail_send_email_success(mock_smtp):
    """Test successful email sending with mocked SMTP."""
    # Setup mock
    mock_connection = MagicMock()
    mock_smtp.return_value = mock_connection
    
    from src.integrations.gmail import GmailClient
    client = GmailClient(email="test@gmail.com", password="app-password")
    
    result = client.send(
        to="recipient@example.com",
        subject="Test Email",
        body="Test body"
    )
    
    assert result is True
    mock_connection.sendmail.assert_called_once()


@patch("smtplib.SMTP_SSL")
def test_gmail_error_handling(mock_smtp):
    """Test error handling when SMTP connection fails."""
    mock_smtp.side_effect = Exception("Connection refused")
    
    from src.integrations.gmail import GmailClient
    client = GmailClient(email="test@gmail.com", password="app-password")
    
    with pytest.raises(Exception):
        client.send(to="recipient@example.com", subject="Test", body="Test")
