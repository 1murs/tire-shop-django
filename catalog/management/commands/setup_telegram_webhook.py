import json
import urllib.request
import urllib.error

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set up Telegram webhook for live chat"

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            required=True,
            help="Public URL for the webhook, e.g. https://example.com/chat/webhook/",
        )

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            self.stderr.write(self.style.ERROR("TELEGRAM_BOT_TOKEN is not set in .env"))
            return

        webhook_url = options["url"]
        api_url = f"https://api.telegram.org/bot{token}/setWebhook"

        payload = json.dumps({"url": webhook_url}).encode("utf-8")
        req = urllib.request.Request(
            api_url, data=payload, headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("ok"):
                    self.stdout.write(self.style.SUCCESS(
                        f"Webhook set successfully: {webhook_url}"
                    ))
                else:
                    self.stderr.write(self.style.ERROR(
                        f"Telegram error: {result.get('description', 'Unknown error')}"
                    ))
        except urllib.error.URLError as e:
            self.stderr.write(self.style.ERROR(f"Request failed: {e}"))
