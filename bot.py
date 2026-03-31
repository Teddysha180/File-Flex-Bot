import logging
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

from handlers.admin import admin_command
from handlers.commands import help_command, start_command
from handlers.files import (
    handle_document,
    handle_photo,
    handle_text_input,
    handle_video,
    unknown_handler,
)
from handlers.states import reset_user_state
from utils.filesystem import ensure_download_dir


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class HealthcheckHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    @property
    def _normalized_path(self) -> str:
        return urlsplit(self.path).path

    def _send_plain_response(self, status_code: int, body: bytes = b"", *, include_body: bool) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        if include_body and body:
            self.wfile.write(body)

    def _respond(self, include_body: bool) -> None:
        if self._normalized_path in {"/", "/health", "/healthz"}:
            self._send_plain_response(200, b"ok", include_body=include_body)
            return

        self._send_plain_response(404, b"not found", include_body=include_body)

    def do_GET(self) -> None:  # noqa: N802
        self._respond(include_body=True)

    def do_HEAD(self) -> None:  # noqa: N802
        self._respond(include_body=False)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Allow", "GET, HEAD, OPTIONS")
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()

    def log_message(self, format: str, *args) -> None:
        return


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled exception while processing an update", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Something unexpected happened while processing your request. Please try again with /start."
        )


def start_healthcheck_server() -> None:
    port = os.getenv("PORT")
    if not port:
        return

    server = ThreadingHTTPServer(("0.0.0.0", int(port)), HealthcheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("Healthcheck server started on port %s", port)


def build_application() -> Application:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is not set.")

    ensure_download_dir()

    application = Application.builder().token(token).build()

    application.bot_data["reset_state"] = reset_user_state
    application.bot_data["started_at"] = time.time()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(
        MessageHandler(filters.Document.ALL & ~filters.COMMAND, handle_document)
    )
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input)
    )
    application.add_handler(MessageHandler(filters.ALL, unknown_handler))
    application.add_error_handler(error_handler)

    return application


def main() -> None:
    start_healthcheck_server()
    application = build_application()
    logger.info("Starting Telegram File Tools Bot with polling.")
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
