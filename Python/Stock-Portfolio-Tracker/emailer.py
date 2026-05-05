# emailer.py
# ─────────────────────────────────────────────
# Handles SMTP email sending with CID-embedded
# inline chart images using Gmail SMTP.
# ─────────────────────────────────────────────

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.image     import MIMEImage
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER


def send_email(subject, html_body, chart_images):
    """
    Sends the HTML report email with inline CID chart images.

    Parameters:
        subject      (str)  : Email subject line
        html_body    (str)  : Full HTML email body string
        chart_images (dict) : { "TICKER": <png bytes>, ... }
    """
    try:
        msg_root              = MIMEMultipart("related")
        msg_root["Subject"]   = subject
        msg_root["From"]      = EMAIL_SENDER
        msg_root["To"]        = EMAIL_RECEIVER

        msg_alternative = MIMEMultipart("alternative")
        msg_root.attach(msg_alternative)
        msg_alternative.attach(MIMEText(html_body, "html"))

        for ticker, png_bytes in chart_images.items():
            if png_bytes:
                img = MIMEImage(png_bytes, _subtype="png")
                img.add_header("Content-ID", f"<chart_{ticker}>")
                img.add_header(
                    "Content-Disposition", "inline",
                    filename=f"chart_{ticker}.png"
                )
                msg_root.attach(img)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg_root.as_string())
        server.quit()
        print("Email report sent successfully.")

    except Exception as e:
        print(f"Failed to send email: {e}")
