import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5100")
CLIENT_URL = os.getenv("CLIENT_URL", "http://localhost:5173")
MAIL_FROM = os.getenv("MAIL_FROM", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_SECURE = os.getenv("SMTP_SECURE", "true").lower() == "true"
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")


def _send_mail(to_email, subject, html):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    msg.set_content("Please open this email in HTML-compatible mail client.")
    msg.add_alternative(html, subtype="html")

    if SMTP_SECURE:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)


def _base_email_template(title, subtitle, button_text, button_link, footer_text):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>{title}</title>
    </head>
    <body style="margin:0; padding:0; background:#f4f7fb; font-family:Arial, Helvetica, sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f4f7fb; padding:40px 0;">
        <tr>
          <td align="center">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px; background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 8px 24px rgba(0,0,0,0.08);">
              <tr>
                <td style="background:linear-gradient(135deg, #2563eb, #1d4ed8); padding:28px 32px; text-align:center;">
                  <h1 style="margin:0; color:#ffffff; font-size:24px; font-weight:700;">Account Management System</h1>
                  <p style="margin:8px 0 0; color:#dbeafe; font-size:14px;">Secure account access and verification</p>
                </td>
              </tr>

              <tr>
                <td style="padding:40px 32px; text-align:center;">
                  <h2 style="margin:0 0 12px; color:#111827; font-size:26px;">{title}</h2>
                  <p style="margin:0 0 28px; color:#4b5563; font-size:16px; line-height:1.6;">
                    {subtitle}
                  </p>

                  <a href="{button_link}"
                     style="display:inline-block; background:#2563eb; color:#ffffff; text-decoration:none; font-size:16px; font-weight:700; padding:14px 28px; border-radius:10px;">
                    {button_text}
                  </a>

                  <p style="margin:28px 0 8px; color:#6b7280; font-size:13px;">
                    If the button does not work, copy and paste this link into your browser:
                  </p>
                  <p style="margin:0; word-break:break-all; font-size:13px; color:#2563eb;">
                    {button_link}
                  </p>
                </td>
              </tr>

              <tr>
                <td style="padding:20px 32px; background:#f9fafb; border-top:1px solid #e5e7eb; text-align:center;">
                  <p style="margin:0; color:#6b7280; font-size:13px;">
                    {footer_text}
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """


def _success_page_template(title, message, button_text, button_link):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>{title}</title>
    </head>
    <body style="margin:0; padding:0; background:#f4f7fb; font-family:Arial, Helvetica, sans-serif;">
      <table width="100%" height="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f4f7fb; min-height:100vh;">
        <tr>
          <td align="center" valign="middle">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:560px; background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 8px 24px rgba(0,0,0,0.08);">
              <tr>
                <td style="background:linear-gradient(135deg, #16a34a, #15803d); padding:26px 30px; text-align:center;">
                  <h1 style="margin:0; color:#ffffff; font-size:24px;">{title}</h1>
                </td>
              </tr>
              <tr>
                <td style="padding:40px 30px; text-align:center;">
                  <div style="font-size:52px; margin-bottom:14px;">✅</div>
                  <p style="margin:0 0 24px; color:#374151; font-size:16px; line-height:1.7;">
                    {message}
                  </p>
                  <a href="{button_link}"
                     style="display:inline-block; background:#2563eb; color:#ffffff; text-decoration:none; font-size:16px; font-weight:700; padding:14px 28px; border-radius:10px;">
                    {button_text}
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """


def _error_page_template(title, message, button_text, button_link):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>{title}</title>
    </head>
    <body style="margin:0; padding:0; background:#f4f7fb; font-family:Arial, Helvetica, sans-serif;">
      <table width="100%" height="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f4f7fb; min-height:100vh;">
        <tr>
          <td align="center" valign="middle">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:560px; background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 8px 24px rgba(0,0,0,0.08);">
              <tr>
                <td style="background:linear-gradient(135deg, #dc2626, #b91c1c); padding:26px 30px; text-align:center;">
                  <h1 style="margin:0; color:#ffffff; font-size:24px;">{title}</h1>
                </td>
              </tr>
              <tr>
                <td style="padding:40px 30px; text-align:center;">
                  <div style="font-size:52px; margin-bottom:14px;">⚠️</div>
                  <p style="margin:0 0 24px; color:#374151; font-size:16px; line-height:1.7;">
                    {message}
                  </p>
                  <a href="{button_link}"
                     style="display:inline-block; background:#2563eb; color:#ffffff; text-decoration:none; font-size:16px; font-weight:700; padding:14px 28px; border-radius:10px;">
                    {button_text}
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """


def send_verification_email(email, fullname, token):
    verify_link = f"{APP_BASE_URL}/api/verify-email?token={token}"
    html = _base_email_template(
        title="Verify Your Email",
        subtitle=f"Hello {fullname}, please confirm your email address to activate your account. Click the button below to continue.",
        button_text="Click to Verify",
        button_link=verify_link,
        footer_text="If you did not create an account, you can safely ignore this email.",
    )
    _send_mail(email, "Verify Your Email Address", html)


def send_reset_email(email, fullname, token):
    reset_link = f"{CLIENT_URL}/reset-password?token={token}"
    html = _base_email_template(
        title="Reset Your Password",
        subtitle=f"Hello {fullname}, we received a request to reset your password. Click the button below to set a new password.",
        button_text="Reset Password",
        button_link=reset_link,
        footer_text="This password reset link will expire in 1 hour.",
    )
    _send_mail(email, "Reset Your Password", html)


def render_verification_success_page():
    return _success_page_template(
        title="Email Verified",
        message="Thank you. Your email address has been successfully verified. You may now continue to the login page and access your account.",
        button_text="Go to Login",
        button_link=f"{CLIENT_URL}/login",
    )


def render_verification_error_page():
    return _error_page_template(
        title="Verification Failed",
        message="This verification link is invalid, expired, or has already been used. Please try registering again or request a new verification email.",
        button_text="Go to Login",
        button_link=f"{CLIENT_URL}/login",
    )