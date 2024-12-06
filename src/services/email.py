import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiofiles
from aiosmtplib import SMTP

from schemas.email import MessageSchema
from core.config import settings


log = logging.getLogger(__name__)


class EmailService:
    def __init__(
        self,
        smtp_host: str,
        smtp_user: str,
        smtp_password: str,
        smtp_port: int,
        timeout: int = 10
    ) -> None:
        self.smtp_host = smtp_host
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.smtp_port = smtp_port
        self.timeout = timeout

    async def send_message(self, recipient: str, message: MessageSchema) -> bool:
        """
        Sends an email message to the specified recipient.

        Args:
            recipient (str): The recipient's email address.
            message (Message): a message object containing the contents of an email.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        
        msg = MIMEMultipart()
        msg['From'] = self.smtp_user
        msg['To'] = recipient
        msg['Subject'] = message.message_type.value

        html_template = await self.render_template(
            template_name = f"{message.message_type.value}.html",
            **message.model_dump(exclude={"message_type"}, exclude_none=True)
        )

        if html_template is None:
            return False

        msg.attach(MIMEText(html_template, 'html'))

        try:
            async with SMTP(
                hostname=self.smtp_host, port=self.smtp_port, timeout=self.timeout
            ) as server:
                await server.login(self.smtp_user, self.smtp_password)
                await server.sendmail(self.smtp_user, recipient, msg.as_string())
                return True
        except Exception as e:
            log.error(f"Failed to send email to %s: %s", recipient, message.__str__, e)
        
        return False
        
    async def render_template(self, template_name: str, **params: str) -> str | None:
        """
        Render HTML Template

        Args:
            template_name (str): 
            **params: Key-value pairs for placeholders in the template.
        
        Returns:
            str | None: Rendered template as a string or None if an error occurred.
        """

        if len(params) == 0:
            log.error("No element to send the email, template_name: %s", template_name)
            return None

        template = None
        template_path = settings.email.EMAIL_TEMPLATE_DIR / template_name

        try:
            async with aiofiles.open(template_path, "r") as file:
                template = await file.read()
                for key, value in params.items():
                    template = template.replace(f"{{{key}}}", str(value))
        except FileNotFoundError:
            log.error("Template not found: %s", template_name)
        except Exception as e:
            log.error("Error reading template: %s: %s", template_name, e)
        
        return template