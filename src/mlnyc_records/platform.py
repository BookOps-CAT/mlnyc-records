from __future__ import annotations

import logging
import os
from typing import Any

from bookops_nypl_platform import PlatformSession, PlatformToken

logger = logging.getLogger(__name__)


class PlatformManager:
    def __init__(self) -> None:
        self.platform_token = PlatformToken(
            client_id=os.environ["NYPL_PLATFORM_CLIENT"],
            client_secret=os.environ["NYPL_PLATFORM_SECRET"],
            oauth_server=os.environ["NYPL_PLATFORM_OAUTH"],
        )
        self.session: PlatformSession | None = None

    def __enter__(self, *args, **kwargs) -> PlatformSession:
        self.session = PlatformSession(authorization=self.platform_token)
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.session.close()

    def search_platform_bibs(self, control_number: str) -> dict[str, Any]:
        response = self.session.search_controlNos(control_number)
        data = response.json()
        return data["data"]
