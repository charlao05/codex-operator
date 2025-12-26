# WhatsApp integration tests
from unittest.mock import patch, MagicMock
import pytest

@patch('requests.post')
def test_whatsapp_send_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'messages': [{'id': 'msg-123'}]}
    mock_post.return_value = mock_response
    
    from src.integrations.whatsapp import WhatsAppClient
    client = WhatsAppClient(token='EAAFaKajjJnkBATest', phone_id='123456789')
    result = client.send_message(to='5511999999999', message='Ola!')
    
    assert result is not None
    mock_post.assert_called_once()

@patch('requests.post')
def test_whatsapp_error(mock_post):
    mock_post.side_effect = Exception('API failed')
    
    from src.integrations.whatsapp import WhatsAppClient
    client = WhatsAppClient(token='EAAFaKajjJnkBATest', phone_id='123456789')
    
    with pytest.raises(Exception):
        client.send_message(to='5511999999999', message='Test')
