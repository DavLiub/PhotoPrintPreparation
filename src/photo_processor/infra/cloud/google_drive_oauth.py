from __future__ import annotations

import base64
import hashlib
import http.server
import json
import queue
import secrets
import threading
import urllib.parse
import webbrowser
from dataclasses import dataclass
from urllib import request
from urllib.error import HTTPError, URLError

from photo_processor.infra.cloud.google_drive_uploader import GoogleDriveCredentials


@dataclass(frozen=True, slots=True)
class GoogleDriveAuthorizationResult:
    credentials: GoogleDriveCredentials
    account_email: str


class GoogleDriveOAuthFlow:
    DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"
    OPENID_SCOPE = "openid"
    EMAIL_SCOPE = "email"

    def __init__(
        self,
        browser_opener: callable | None = None,
        requester: callable | None = None,
        callback_timeout_seconds: int = 180,
    ) -> None:
        self.browser_opener = browser_opener or webbrowser.open
        self.requester = requester or self._default_requester
        self.callback_timeout_seconds = callback_timeout_seconds

    def authorize(self, client_id: str, client_secret: str | None = None) -> GoogleDriveAuthorizationResult:
        verifier = _code_verifier()
        challenge = _code_challenge(verifier)
        state = secrets.token_urlsafe(32)
        callback_queue: queue.Queue[tuple[str | None, str | None, str | None]] = queue.Queue(maxsize=1)
        server = _build_loopback_server(callback_queue)
        redirect_uri = f"http://127.0.0.1:{server.server_port}/callback"

        server_thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.2}, daemon=True)
        server_thread.start()
        auth_url = self._build_authorization_url(client_id, redirect_uri, state, challenge)

        if not self.browser_opener(auth_url):
            server.shutdown()
            server_thread.join(timeout=5)
            server.server_close()
            raise RuntimeError("Could not open the browser for Google Drive sign-in.")

        try:
            code, returned_state, error = callback_queue.get(timeout=self.callback_timeout_seconds)
        except queue.Empty as exc:
            server.shutdown()
            server_thread.join(timeout=5)
            server.server_close()
            raise RuntimeError("Google Drive sign-in timed out waiting for the browser callback.") from exc
        finally:
            server.shutdown()
            server_thread.join(timeout=5)
            server.server_close()

        if error:
            raise RuntimeError(f"Google Drive sign-in failed: {error}")
        if returned_state != state:
            raise RuntimeError("Google Drive sign-in failed because the callback state did not match.")
        if not code:
            raise RuntimeError("Google Drive sign-in failed because no authorization code was returned.")

        token_data = self._exchange_code_for_tokens(
            client_id=client_id,
            client_secret=client_secret,
            code=code,
            redirect_uri=redirect_uri,
            verifier=verifier,
        )
        refresh_token = token_data.get("refresh_token")
        access_token = token_data.get("access_token")
        if not refresh_token or not access_token:
            raise RuntimeError("Google Drive sign-in did not return both access and refresh tokens.")

        account_email = self._fetch_account_email(str(access_token))
        return GoogleDriveAuthorizationResult(
            credentials=GoogleDriveCredentials(
                client_id=client_id,
                refresh_token=str(refresh_token),
                client_secret=client_secret,
            ),
            account_email=account_email,
        )

    def _build_authorization_url(self, client_id: str, redirect_uri: str, state: str, challenge: str) -> str:
        query = urllib.parse.urlencode(
            {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": " ".join([self.DRIVE_SCOPE, self.OPENID_SCOPE, self.EMAIL_SCOPE]),
                "access_type": "offline",
                "prompt": "consent",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "state": state,
            }
        )
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"

    def _exchange_code_for_tokens(
        self,
        client_id: str,
        client_secret: str | None,
        code: str,
        redirect_uri: str,
        verifier: str,
    ) -> dict[str, object]:
        payload_data = {
            "client_id": client_id,
            "code": code,
            "code_verifier": verifier,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        if client_secret:
            payload_data["client_secret"] = client_secret
        payload = urllib.parse.urlencode(payload_data).encode("utf-8")
        status_code, response_body = self.requester(
            "POST",
            "https://oauth2.googleapis.com/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            payload,
        )
        if status_code >= 400:
            raise RuntimeError(
                f"Google token exchange failed with status {status_code}: {response_body.decode('utf-8', errors='replace')}"
            )
        return json.loads(response_body.decode("utf-8"))

    def _fetch_account_email(self, access_token: str) -> str:
        status_code, response_body = self.requester(
            "GET",
            "https://openidconnect.googleapis.com/v1/userinfo",
            {"Authorization": f"Bearer {access_token}"},
            None,
        )
        if status_code >= 400:
            raise RuntimeError(
                f"Google user info lookup failed with status {status_code}: {response_body.decode('utf-8', errors='replace')}"
            )
        data = json.loads(response_body.decode("utf-8"))
        email = data.get("email")
        if not email:
            raise RuntimeError("Google user info lookup did not return an email address.")
        return str(email)

    def _default_requester(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
    ) -> tuple[int, bytes]:
        request_obj = request.Request(url, data=body, method=method, headers=headers)
        try:
            with request.urlopen(request_obj) as response:
                return response.getcode(), response.read()
        except HTTPError as exc:
            return exc.code, exc.read()
        except URLError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(f"Google OAuth request failed: {exc.reason}") from exc


def _code_verifier() -> str:
    return secrets.token_urlsafe(64)


def _code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _build_loopback_server(callback_queue: queue.Queue[tuple[str | None, str | None, str | None]]):
    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return
            params = urllib.parse.parse_qs(parsed.query)
            callback_queue.put(
                (
                    params.get("code", [None])[0],
                    params.get("state", [None])[0],
                    params.get("error", [None])[0],
                )
            )
            body = (
                "<html><body><h3>Google Drive connection complete.</h3>"
                "<p>You can close this browser window and return to the application.</p>"
                "</body></html>"
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            threading.Thread(target=self.server.shutdown, daemon=True).start()

        def log_message(self, _format: str, *_args) -> None:  # pragma: no cover
            return

    return http.server.ThreadingHTTPServer(("127.0.0.1", 0), CallbackHandler)
