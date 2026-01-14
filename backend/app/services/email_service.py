"""
Email service for sending transactional emails via Resend
"""
import resend
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Configure Resend API key
resend.api_key = os.getenv("RESEND_API_KEY")

def send_access_code_email(email: str, access_code: str, credits: int, pack_name: str) -> bool:
    """
    Send access code email after successful purchase

    Args:
        email: Customer email address
        access_code: Generated access code (e.g., MP-XXXX-XXXX)
        credits: Number of credits purchased
        pack_name: Name of the pack purchased (Starter, Pro, Business)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Calculate image processing capacity
        basic_images = credits  # 1 credit = 1 basic image
        premium_images = credits // 3  # 3 credits = 1 premium image

        # HTML email template with Masterpost.io branding
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Your Masterpost.io Access Code</title>
    <!--[if mso]>
    <style type="text/css">
        body, table, td {{font-family: Arial, Helvetica, sans-serif !important;}}
    </style>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <!-- Wrapper Table -->
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f3f4f6;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <!-- Main Container -->
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">

                    <!-- HEADER (Verde #52B788) -->
                    <tr>
                        <td style="background-color: #52B788; padding: 40px 30px; text-align: center;">
                            <!-- Logo -->
                            <img src="https://masterpost.io/logo-masterpost.png" alt="Masterpost.io Logo" width="80" height="80" style="display: block; margin: 0 auto 20px; border-radius: 50%;">
                            <!-- Title -->
                            <h1 style="margin: 0 0 10px; color: #ffffff; font-size: 28px; font-weight: bold; line-height: 1.3;">
                                Welcome to Masterpost.io! 🎉
                            </h1>
                            <!-- Subtitle -->
                            <p style="margin: 0; color: rgba(255, 255, 255, 0.9); font-size: 16px; line-height: 1.5;">
                                Your purchase was successful
                            </p>
                        </td>
                    </tr>

                    <!-- BODY CONTENT -->
                    <tr>
                        <td style="padding: 40px 30px; background-color: #ffffff;">

                            <!-- Greeting -->
                            <h2 style="margin: 0 0 15px; color: #1f2937; font-size: 22px; font-weight: 600;">
                                Hi there! 👋
                            </h2>

                            <!-- Main Message -->
                            <p style="margin: 0 0 25px; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                Thank you for purchasing the <strong style="color: #1f2937;">{pack_name}</strong>. You now have <strong style="color: #52B788;">{credits} credits</strong> ready to use!
                            </p>

                            <!-- ACCESS CODE BOX (Amarillo #F4D35E) -->
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin: 30px 0;">
                                <tr>
                                    <td style="background-color: #FFF9E6; border: 2px solid #F4D35E; border-radius: 12px; padding: 25px; text-align: center;">
                                        <p style="margin: 0 0 10px; color: #6b7280; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                                            Your Access Code:
                                        </p>
                                        <p style="margin: 0; color: #2D3748; font-size: 32px; font-weight: bold; letter-spacing: 3px; font-family: 'Courier New', Courier, monospace;">
                                            {access_code}
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- PURCHASE DETAILS -->
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin: 25px 0; background-color: #f9fafb; border-radius: 8px; padding: 20px;">
                                <tr>
                                    <td>
                                        <p style="margin: 0 0 10px; color: #1f2937; font-size: 16px; font-weight: 600;">
                                            📦 What you purchased:
                                        </p>
                                        <p style="margin: 0; color: #4b5563; font-size: 15px; line-height: 1.6;">
                                            <strong>{pack_name}</strong> - {credits} credits
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- BENEFITS SECTION -->
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin: 25px 0; background-color: #f0fdf4; border-left: 4px solid #52B788; border-radius: 8px; padding: 20px;">
                                <tr>
                                    <td>
                                        <p style="margin: 0 0 15px; color: #1f2937; font-size: 16px; font-weight: 600;">
                                            🚀 What you can do:
                                        </p>
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                                            <tr>
                                                <td style="padding: 8px 0;">
                                                    <span style="color: #52B788; font-size: 18px; margin-right: 8px;">✅</span>
                                                    <span style="color: #4b5563; font-size: 15px; line-height: 1.6;">
                                                        Process <strong>{basic_images} Basic images</strong> or <strong>{premium_images} Premium images</strong>
                                                    </span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0;">
                                                    <span style="color: #52B788; font-size: 18px; margin-right: 8px;">✅</span>
                                                    <span style="color: #4b5563; font-size: 15px; line-height: 1.6;">
                                                        Amazon, eBay, Instagram marketplace ready
                                                    </span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0;">
                                                    <span style="color: #52B788; font-size: 18px; margin-right: 8px;">✅</span>
                                                    <span style="color: #4b5563; font-size: 15px; line-height: 1.6;">
                                                        Batch processing up to 100 images at once
                                                    </span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0;">
                                                    <span style="color: #52B788; font-size: 18px; margin-right: 8px;">✅</span>
                                                    <span style="color: #4b5563; font-size: 15px; line-height: 1.6;">
                                                        Credits never expire
                                                    </span>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                            <!-- CTA BUTTON (Verde #52B788) -->
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin: 35px 0 30px;">
                                <tr>
                                    <td align="center">
                                        <a href="https://masterpost.io/login" style="display: inline-block; background: linear-gradient(135deg, #52B788 0%, #40916C 100%); color: #ffffff; font-size: 16px; font-weight: 600; text-decoration: none; padding: 14px 32px; border-radius: 8px; box-shadow: 0 4px 6px rgba(82, 183, 136, 0.3); transition: all 0.3s ease;">
                                            Go to Login →
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <!-- HELP SECTION -->
                            <p style="margin: 30px 0 0; padding-top: 25px; border-top: 1px solid #e5e7eb; color: #718096; font-size: 14px; line-height: 1.6; text-align: center;">
                                Need help? Reply to this email or contact us at
                                <a href="mailto:support@masterpost.io" style="color: #52B788; text-decoration: none; font-weight: 500;">support@masterpost.io</a>
                            </p>

                        </td>
                    </tr>

                    <!-- FOOTER (Gris claro #F7FAFC) -->
                    <tr>
                        <td style="background-color: #F7FAFC; border-top: 1px solid #E2E8F0; padding: 30px; text-align: center;">
                            <!-- Help Text -->
                            <p style="font-size: 14px; color: #4a5568; margin: 0 0 8px 0;">
                                Need help? Reply to this email
                            </p>
                            <p style="font-size: 14px; color: #52B788; margin: 0 0 16px 0;">
                                <a href="mailto:support@masterpost.io" style="color: #52B788; text-decoration: none;">
                                    support@masterpost.io
                                </a>
                            </p>

                            <!-- Divider -->
                            <div style="border-top: 1px solid #e2e8f0; margin: 16px 0;"></div>

                            <!-- Copyright -->
                            <p style="font-size: 14px; color: #4a5568; margin: 0 0 4px 0;">
                                © 2026 Masterpost.io 💚
                            </p>
                            <p style="font-size: 12px; color: #718096; margin: 0 0 12px 0;">
                                Professional Image Processing
                            </p>

                            <!-- Neuracoder Team -->
                            <p style="font-size: 13px; color: #718096; margin: 0;">
                                Powered by ☕ <a href="https://neuracoder.com" style="color: #718096; text-decoration: none;">Neuracoder Team</a>
                            </p>
                        </td>
                    </tr>

                </table>
                <!-- End Main Container -->

                <!-- Spacer for mobile -->
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                        <td style="padding: 20px; text-align: center;">
                            <p style="margin: 0; color: #9ca3af; font-size: 12px; line-height: 1.5;">
                                This email was sent because you purchased credits at masterpost.io<br>
                                If you have any questions, we're here to help!
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

        # Send email via Resend
        params = {
            "from": "Masterpost.io <noreply@masterpost.io>",
            "to": [email],
            "subject": f"🎉 Your Masterpost.io Access Code - {credits} Credits Ready!",
            "html": html_content,
        }

        response = resend.Emails.send(params)

        logger.info(f"✅ Access code email sent to {email} - Email ID: {response.get('id')}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send email to {email}: {str(e)}")
        return False


async def send_free_trial_email(
    to_email: str,
    access_code: str,
    credits: int = 10
) -> bool:
    """
    Send welcome email for free trial

    Args:
        to_email: User email
        access_code: Generated access code
        credits: Credits granted (default 10)

    Returns:
        bool: True if sent successfully
    """
    try:
        # HTML Template for Free Trial
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Masterpost.io - Free Trial</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background-color: #f9fafb;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background: linear-gradient(135deg, #52B788 0%, #40916C 100%);">
        <tr>
            <td style="padding: 40px 20px; text-align: center;">
                <img src="https://masterpost.io/logo-masterpost.png" alt="Masterpost.io" style="width: 80px; height: 80px; margin-bottom: 16px;">
                <h1 style="color: white; font-size: 32px; font-weight: 800; margin: 0 0 8px 0;">Welcome to Masterpost.io! 🎉</h1>
                <p style="color: rgba(255,255,255,0.9); font-size: 16px; margin: 0;">Your free trial is ready</p>
            </td>
        </tr>
    </table>

    <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: white;">
        <tr>
            <td style="padding: 40px 32px;">
                <p style="font-size: 16px; color: #1f2937; margin: 0 0 16px 0;">Hi there! 👋</p>

                <p style="font-size: 16px; color: #4b5563; margin: 0 0 24px 0;">
                    Welcome to Masterpost.io! We're excited to have you on board. You now have <strong>{credits} free credits</strong> ready to use!
                </p>

                <table role="presentation" style="width: 100%; border-collapse: collapse; background: linear-gradient(to right, #fffbeb, #f0fdf4, #fffbeb); border-left: 4px solid #F4D35E; border-radius: 12px; margin: 24px 0;">
                    <tr>
                        <td style="padding: 24px;">
                            <p style="font-size: 14px; font-weight: 600; color: #1f2937; margin: 0 0 8px 0;">🔑 Your Access Code:</p>
                            <p style="font-family: 'Courier New', monospace; font-size: 28px; font-weight: 700; letter-spacing: 3px; color: #2d3748; margin: 0;">{access_code}</p>
                        </td>
                    </tr>
                </table>

                <div style="margin: 32px 0;">
                    <p style="font-size: 16px; font-weight: 600; color: #1f2937; margin: 0 0 12px 0;">🚀 What you get:</p>
                    <ul style="margin: 0; padding-left: 20px; color: #4b5563;">
                        <li style="margin-bottom: 8px;">10 Free Credits (no payment required)</li>
                        <li style="margin-bottom: 8px;">Process up to 10 basic images or 3 premium images</li>
                        <li style="margin-bottom: 8px;">Test all marketplace formats (Amazon, eBay, Instagram)</li>
                        <li style="margin-bottom: 8px;">Credits never expire</li>
                    </ul>
                </div>

                <div style="margin: 32px 0;">
                    <p style="font-size: 16px; font-weight: 600; color: #1f2937; margin: 0 0 12px 0;">✨ Ready to start?</p>
                    <ol style="margin: 0; padding-left: 20px; color: #4b5563;">
                        <li style="margin-bottom: 8px;">Go to <a href="https://masterpost.io/login" style="color: #52B788; text-decoration: none;">masterpost.io/login</a></li>
                        <li style="margin-bottom: 8px;">Enter your email and access code</li>
                        <li style="margin-bottom: 8px;">Start processing images!</li>
                    </ol>
                </div>

                <table role="presentation" style="margin: 32px 0;">
                    <tr>
                        <td style="text-align: center;">
                            <a href="https://masterpost.io/login" style="display: inline-block; padding: 14px 32px; background: linear-gradient(to right, #52B788, #40916C); color: white; text-decoration: none; font-weight: 600; border-radius: 8px; font-size: 16px;">
                                Go to Login →
                            </a>
                        </td>
                    </tr>
                </table>

                <div style="margin: 32px 0; padding: 20px; background-color: #f9fafb; border-radius: 8px;">
                    <p style="font-size: 14px; font-weight: 600; color: #1f2937; margin: 0 0 8px 0;">💡 Want more credits?</p>
                    <p style="font-size: 14px; color: #4b5563; margin: 0 0 12px 0;">Check out our affordable pricing plans:</p>
                    <ul style="margin: 0; padding-left: 20px; color: #4b5563; font-size: 14px;">
                        <li>Starter: 50 credits - $6.99</li>
                        <li>Pro: 250 credits - $24.99</li>
                        <li>Business: 650 credits - $54.99</li>
                    </ul>
                </div>

                <p style="font-size: 14px; color: #6b7280; margin: 32px 0 0 0; text-align: center;">
                    Need help? Reply to this email or contact us at <a href="mailto:support@masterpost.io" style="color: #52B788; text-decoration: none;">support@masterpost.io</a>
                </p>
            </td>
        </tr>
    </table>

    <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #f7fafc; border-top: 1px solid #e2e8f0;">
        <tr>
            <td style="padding: 24px; text-align: center;">
                <!-- Help Text -->
                <p style="font-size: 14px; color: #4a5568; margin: 0 0 8px 0;">
                    Need help? Reply to this email
                </p>
                <p style="font-size: 14px; color: #52B788; margin: 0 0 16px 0;">
                    <a href="mailto:support@masterpost.io" style="color: #52B788; text-decoration: none;">
                        support@masterpost.io
                    </a>
                </p>

                <!-- Divider -->
                <div style="border-top: 1px solid #e2e8f0; margin: 16px 0;"></div>

                <!-- Copyright -->
                <p style="font-size: 14px; color: #4a5568; margin: 0 0 4px 0;">
                    © 2026 Masterpost.io 💚
                </p>
                <p style="font-size: 12px; color: #718096; margin: 0 0 12px 0;">
                    Professional Image Processing
                </p>

                <!-- Neuracoder Team -->
                <p style="font-size: 13px; color: #718096; margin: 0;">
                    Powered by ☕ <a href="https://neuracoder.com" style="color: #718096; text-decoration: none;">Neuracoder Team</a>
                </p>
            </td>
        </tr>
    </table>
</body>
</html>
"""

        # Send email via Resend
        params = {
            "from": "Masterpost.io <noreply@masterpost.io>",
            "to": [to_email],
            "subject": "Your Free Masterpost.io Credits Are Ready! 🎉",
            "html": html_content,
        }

        response = resend.Emails.send(params)

        logger.info(f"✅ Free trial email sent to {to_email} - Email ID: {response.get('id')}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send free trial email to {to_email}: {e}")
        return False


def send_test_email(email: str) -> bool:
    """
    Send a test email to verify configuration

    Args:
        email: Email address to send test to

    Returns:
        bool: True if successful
    """
    try:
        params = {
            "from": "Masterpost.io <noreply@masterpost.io>",
            "to": [email],
            "subject": "🧪 Test Email from Masterpost.io",
            "html": "<h1>Success!</h1><p>Email service is working correctly.</p>",
        }

        response = resend.Emails.send(params)
        logger.info(f"✅ Test email sent to {email} - Email ID: {response.get('id')}")
        return True

    except Exception as e:
        logger.error(f"❌ Test email failed: {str(e)}")
        return False
