#!/usr/bin/env python3
"""Send email notifications with extracted updates"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def format_update_email(venue_name: str, updates: List[dict]) -> tuple[str, str]:
    """
    Format updates into email subject and body (single venue)
    
    Args:
        venue_name: Name of the venue/source
        updates: List of update dictionaries with 'title' and 'link'
    
    Returns:
        Tuple of (subject, html_body)
    """
    # Create subject
    update_count = len(updates)
    subject = f"🔔 {update_count} New Update{'s' if update_count != 1 else ''} from {venue_name}"
    
    # Create HTML body
    html_body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .venue {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                color: #4CAF50;
            }}
            .update {{
                margin-bottom: 25px;
                padding: 15px;
                border-left: 4px solid #4CAF50;
                background-color: #f9f9f9;
            }}
            .update-title {{
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #333;
            }}
            .update-link {{
                color: #2196F3;
                text-decoration: none;
                word-break: break-all;
            }}
            .update-link:hover {{
                text-decoration: underline;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📰 New Updates Available by AIPS</h1>
        </div>
        
        <div class="content">
            <div class="venue">📍 {venue_name}</div>
            
            <p>Found <strong>{update_count}</strong> new update{'s' if update_count != 1 else ''}:</p>
    """
    
    # Add each update
    for i, update in enumerate(updates, 1):
        title = update.get('title', 'No title')
        link = update.get('link', '#')
        
        html_body += f"""
            <div class="update">
                <div class="update-title">{i}. {title}</div>
                <div>
                    🔗 <a href="{link}" class="update-link">{link}</a>
                </div>
            </div>
        """
    
    html_body += """
        </div>
        
        <div class="footer">
            <p>This is an automated notification from your AIPS monitoring system.</p>
        </div>
    </body>
    </html>
    """
    
    return subject, html_body


def format_combined_email(all_updates: dict) -> tuple[str, str]:
    """
    Format updates from multiple venues into a single email
    
    Args:
        all_updates: Dictionary mapping venue names to lists of updates
                    Example: {"Venue1": [{"title": "...", "link": "..."}], "Venue2": [...]}
    
    Returns:
        Tuple of (subject, html_body)
    """
    # Calculate total updates
    total_updates = sum(len(updates) for updates in all_updates.values())
    venue_count = len(all_updates)
    
    # Create subject
    subject = f"🔔 {total_updates} New Update{'s' if total_updates != 1 else ''} from {venue_count} Source{'s' if venue_count != 1 else ''}"
    
    # Create HTML body
    html_body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .summary {{
                background-color: #e8f5e9;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 30px;
            }}
            .venue-section {{
                margin-bottom: 40px;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 20px;
                background-color: #fafafa;
            }}
            .venue {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                color: #4CAF50;
                border-bottom: 2px solid #4CAF50;
                padding-bottom: 10px;
            }}
            .update {{
                margin-bottom: 20px;
                padding: 15px;
                border-left: 4px solid #4CAF50;
                background-color: white;
            }}
            .update-title {{
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #333;
            }}
            .update-link {{
                color: #2196F3;
                text-decoration: none;
                word-break: break-all;
            }}
            .update-link:hover {{
                text-decoration: underline;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📰 New Updates Available by AIPS</h1>
        </div>
        
        <div class="content">
            <div class="summary">
                <strong>Summary:</strong> Found <strong>{total_updates}</strong> new update{'s' if total_updates != 1 else ''} 
                from <strong>{venue_count}</strong> source{'s' if venue_count != 1 else ''}.
            </div>
    """
    
    # Add each venue section
    for venue_name, updates in all_updates.items():
        update_count = len(updates)
        html_body += f"""
            <div class="venue-section">
                <div class="venue">📍 {venue_name} ({update_count} update{'s' if update_count != 1 else ''})</div>
        """
        
        # Add each update for this venue
        for i, update in enumerate(updates, 1):
            title = update.get('title', 'No title')
            link = update.get('link', '#')
            
            html_body += f"""
                <div class="update">
                    <div class="update-title">{i}. {title}</div>
                    <div>
                        🔗 <a href="{link}" class="update-link">{link}</a>
                    </div>
                </div>
            """
        
        html_body += """
            </div>
        """
    
    html_body += """
        </div>
        
        <div class="footer">
            <p>This is an automated notification from your AIPS monitoring system.</p>
        </div>
    </body>
    </html>
    """
    
    return subject, html_body


def send_email(venue_name: str, updates: List[dict]) -> bool:
    """
    Send email with extracted updates
    
    Args:
        venue_name: Name of the venue/source
        updates: List of update dictionaries with 'title' and 'link'
    
    Returns:
        True if email sent successfully, False otherwise
    """
    # Get email configuration from environment variables
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    
    # Validate required configuration
    if not all([sender_email, sender_password, recipient_email]):
        print("  ⚠ Email configuration incomplete. Set SENDER_EMAIL, SENDER_PASSWORD, and RECIPIENT_EMAIL in .env")
        return False
    
    # Skip if no updates
    if not updates:
        print("  ℹ No updates to send")
        return False
    
    try:
        # Format email
        subject, html_body = format_update_email(venue_name, updates)
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient_email
        
        # Attach HTML body
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)
        
        # Connect to SMTP server and send email
        print(f"  ✓ Sending email notification...")
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        print(f"  ✓ Email sent successfully to {recipient_email}")
        return True
    
    except Exception as e:
        print(f"  ✗ Failed to send email: {e}")
        return False


def send_combined_updates(all_updates: dict) -> bool:
    """
    Send a single email with updates from all venues
    
    Args:
        all_updates: Dictionary mapping venue names to lists of updates
                    Example: {"Venue1": [{"title": "...", "link": "..."}], "Venue2": [...]}
    
    Returns:
        True if email sent successfully, False otherwise
    """
    # Get email configuration from environment variables
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    
    # Validate required configuration
    if not all([sender_email, sender_password, recipient_email]):
        print("  ⚠ Email configuration incomplete. Set SENDER_EMAIL, SENDER_PASSWORD, and RECIPIENT_EMAIL in .env")
        return False
    
    # Skip if no updates
    if not all_updates:
        print("  ℹ No updates to send")
        return False
    
    try:
        # Format email
        subject, html_body = format_combined_email(all_updates)
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient_email
        
        # Attach HTML body
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)
        
        # Connect to SMTP server and send email
        total_updates = sum(len(updates) for updates in all_updates.values())
        print(f"\n✓ Sending email notification with {total_updates} updates from {len(all_updates)} source(s)...")
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        print(f"✓ Email sent successfully to {recipient_email}\n")
        return True
    
    except Exception as e:
        print(f"✗ Failed to send email: {e}\n")
        return False


def send_updates_notification(venue_name: str, updates_data: dict) -> bool:
    """
    Send email notification for updates (single venue)
    
    Args:
        venue_name: Name of the venue/source
        updates_data: Updates data from LLM extraction (dict with 'updates' key)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    if not updates_data or 'updates' not in updates_data:
        return False
    
    updates = updates_data['updates']
    
    if not updates:
        return False
    
    return send_email(venue_name, updates)


if __name__ == "__main__":
    # Example usage for testing
    test_updates = [
        {
            "title": "Test Article 1",
            "link": "https://example.com/article1"
        },
        {
            "title": "Test Article 2: A Longer Title to Test Formatting",
            "link": "https://example.com/very/long/path/to/article2"
        }
    ]
    
    send_email("Test Venue", test_updates)
