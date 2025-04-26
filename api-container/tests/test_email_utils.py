import pytest
from unittest.mock import patch, MagicMock, call
from flask import Flask
from flask_mail import Message
import threading
from app.email_utils import (
    init_mail, send_async_email, send_email, 
    send_partner_message, send_invitation_email, mail
)

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Set up mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'test'
    app.config['MAIL_PASSWORD'] = 'test'
    app.config['MAIL_DEFAULT_SENDER'] = 'test@example.com'
    
    # Initialize mail with the app
    mail.init_app(app)
    
    return app

def test_init_mail_default_config(app):
    """Test mail initialization with default configuration."""
    # Create a fresh app without configs
    fresh_app = Flask(__name__)
    
    # Test with default values
    with patch('app.email_utils.mail.init_app') as mock_init_app:
        init_mail(fresh_app)
        mock_init_app.assert_called_once_with(fresh_app)
    
    # Verify default config values were set
    assert fresh_app.config['MAIL_SERVER'] == 'smtp.gmail.com'
    assert fresh_app.config['MAIL_PORT'] == 587
    assert fresh_app.config['MAIL_USE_TLS'] is True
    assert fresh_app.config['MAIL_USERNAME'] == ''
    assert fresh_app.config['MAIL_PASSWORD'] == ''
    assert fresh_app.config['MAIL_DEFAULT_SENDER'] == 'together@example.com'

def test_init_mail_custom_config():
    """Test mail initialization with custom configuration."""
    # Set custom values in a new app
    custom_app = Flask(__name__)
    custom_app.config['MAIL_SERVER'] = 'custom.smtp.server'
    custom_app.config['MAIL_PORT'] = 465
    custom_app.config['MAIL_USE_TLS'] = False
    custom_app.config['MAIL_USERNAME'] = 'testuser'
    custom_app.config['MAIL_PASSWORD'] = 'testpass'
    custom_app.config['MAIL_DEFAULT_SENDER'] = 'custom@example.com'
    
    with patch('app.email_utils.mail.init_app') as mock_init_app:
        init_mail(custom_app)
        mock_init_app.assert_called_once_with(custom_app)
    
    # Verify custom values were preserved
    assert custom_app.config['MAIL_SERVER'] == 'custom.smtp.server'
    assert custom_app.config['MAIL_PORT'] == 465
    assert custom_app.config['MAIL_USE_TLS'] is False
    assert custom_app.config['MAIL_USERNAME'] == 'testuser'
    assert custom_app.config['MAIL_PASSWORD'] == 'testpass'
    assert custom_app.config['MAIL_DEFAULT_SENDER'] == 'custom@example.com'

def test_send_async_email_success(app):
    """Test successful asynchronous email sending."""
    mock_msg = MagicMock(spec=Message)
    
    with patch('app.email_utils.mail.send') as mock_send:
        with app.app_context():
            send_async_email(app, mock_msg)
            mock_send.assert_called_once_with(mock_msg)

def test_send_async_email_exception(app):
    """Test exception handling in asynchronous email sending."""
    mock_msg = MagicMock(spec=Message)
    
    with patch('app.email_utils.mail.send', side_effect=Exception("Test exception")), \
         patch('builtins.print') as mock_print:
        with app.app_context():
            send_async_email(app, mock_msg)
            mock_print.assert_called_once()
            assert "Error sending email: Test exception" in mock_print.call_args[0][0]

def test_send_email(app):
    """Test email sending with thread creation."""
    with app.app_context():
        with patch('app.email_utils.Thread') as mock_thread, \
             patch('app.email_utils.current_app._get_current_object', return_value=app):
            
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            # Test with both HTML and text body
            send_email(
                "Test Subject", 
                ["recipient@example.com"], 
                "<p>HTML Content</p>", 
                "Text Content"
            )
            
            # Verify Message object was created correctly
            mock_thread.assert_called_once()
            args = mock_thread.call_args[1]['args']
            assert args[0] == app
            
            # Verify the message properties
            msg = args[1]
            assert msg.subject == "Test Subject"
            assert msg.recipients == ["recipient@example.com"]
            assert msg.html == "<p>HTML Content</p>"
            assert msg.body == "Text Content"
            
            # Verify thread was started
            mock_thread_instance.start.assert_called_once()

def test_send_email_html_only(app):
    """Test email sending with HTML body only."""
    with app.app_context():
        with patch('app.email_utils.Thread') as mock_thread, \
             patch('app.email_utils.current_app._get_current_object', return_value=app):
            
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            # Test with HTML body only
            send_email(
                "HTML Only Subject", 
                ["recipient@example.com"], 
                "<p>HTML Content</p>"
            )
            
            # Verify Message object was created correctly
            mock_thread.assert_called_once()
            args = mock_thread.call_args[1]['args']
            
            # Verify the message properties
            msg = args[1]
            assert msg.subject == "HTML Only Subject"
            assert msg.recipients == ["recipient@example.com"]
            assert msg.html == "<p>HTML Content</p>"
            assert not hasattr(msg, "body") or msg.body is None
            
            # Verify thread was started
            mock_thread_instance.start.assert_called_once()

def test_send_partner_message(app):
    """Test partner message email."""
    with patch('app.email_utils.send_email') as mock_send_email:
        send_partner_message("partner@example.com", "Test Sender", "Hello Partner!")
        
        # Check that send_email was called with the right parameters
        mock_send_email.assert_called_once()
        args = mock_send_email.call_args[0]
        
        assert args[0] == "New message from Test Sender"  # subject
        assert args[1] == ["partner@example.com"]  # recipients
        assert "New message from Test Sender" in args[2]  # html_body
        assert "Hello Partner!" in args[2]  # message content in html
        assert "New message from Test Sender" in args[3]  # text_body
        assert "Hello Partner!" in args[3]  # message content in text

def test_send_invitation_email(app):
    """Test invitation email."""
    with patch('app.email_utils.send_email') as mock_send_email:
        send_invitation_email("invite@example.com", "Test Inviter")
        
        # Check that send_email was called with the right parameters
        mock_send_email.assert_called_once()
        args = mock_send_email.call_args[0]
        
        assert args[0] == "Test Inviter has invited you to join Together"  # subject
        assert args[1] == ["invite@example.com"]  # recipients
        assert "Test Inviter has invited you to join Together" in args[2]  # html_body
        assert "Test Inviter would like to connect with you" in args[2]  # content in html
        assert "Test Inviter has invited you to join Together" in args[3]  # text_body
        assert "Test Inviter would like to connect with you" in args[3]  # content in text