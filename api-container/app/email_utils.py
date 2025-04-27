from flask import current_app, render_template_string
from flask_mail import Mail, Message
from threading import Thread

mail = Mail()


def init_mail(app):
    """Initialize the Mail extension"""
    app.config["MAIL_SERVER"] = app.config.get("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = app.config.get("MAIL_PORT", 587)
    app.config["MAIL_USE_TLS"] = app.config.get("MAIL_USE_TLS", True)
    app.config["MAIL_USERNAME"] = app.config.get("MAIL_USERNAME", "")
    app.config["MAIL_PASSWORD"] = app.config.get("MAIL_PASSWORD", "")
    app.config["MAIL_DEFAULT_SENDER"] = app.config.get(
        "MAIL_DEFAULT_SENDER", "together@example.com"
    )
    mail.init_app(app)


def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}")


def send_email(subject, recipients, html_body, text_body=None):
    """Send an email"""
    app = current_app._get_current_object()
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    if text_body:
        msg.body = text_body

    # Send email in a background thread to not block the main thread
    Thread(target=send_async_email, args=(app, msg)).start()


def send_partner_message(recipient_email, sender_name, message_content):
    """Send a notification email when a partner sends a message"""
    subject = f"New message from {sender_name}"
    html_body = f"""
    <html>
        <body>
            <h2>New message from {sender_name}</h2>
            <p>{message_content}</p>
            <p>Login to <a href="http://together-app.com">Together</a> to reply.</p>
        </body>
    </html>
    """
    text_body = f"""
    New message from {sender_name}
    
    {message_content}
    
    Login to Together to reply: http://together-app.com
    """
    send_email(subject, [recipient_email], html_body, text_body)


def send_invitation_email(recipient_email, sender_name):
    """Send an invitation email to a partner"""
    subject = f"{sender_name} has invited you to join Together"
    html_body = f"""
    <html>
        <body>
            <h2>{sender_name} has invited you to join Together</h2>
            <p>{sender_name} would like to connect with you on Together, an app for couples to stay connected.</p>
            <p><a href="http://together-app.com/register">Click here to create your account</a></p>
        </body>
    </html>
    """
    text_body = f"""
    {sender_name} has invited you to join Together
    
    {sender_name} would like to connect with you on Together, an app for couples to stay connected.
    
    Create your account here: http://together-app.com/register
    """
    send_email(subject, [recipient_email], html_body, text_body)
