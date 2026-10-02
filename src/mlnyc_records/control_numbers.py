from __future__ import annotations

import json
import logging
from pathlib import Path

from mlnyc_records.platform import PlatformManager

logger = logging.getLogger(__name__)


class ControlNumberGenerator:
    def __init__(self, state_file: str, start: int = 1):
        self.state_path = Path(state_file)
        self.used_numbers = set()
        self.next_number = start

        self._load_state()

    def _load_state(self):
        if not self.state_path.exists():
            return
        data = json.loads(self.state_path.read_text())
        logger.debug(f"Loading current control number data: {data}")
        self.used_numbers = set(data.get("used_numbers", [0]))
        self.last_used = max(self.used_numbers)
        logger.debug(f"Searching Sierra for {self._format(self.last_used)}.")
        with PlatformManager() as session:
            valid_ctrl_num = self.check_control_number(session=session)
            if valid_ctrl_num:
                while valid_ctrl_num:
                    self.last_used = self.last_used + 1
                    valid_ctrl_num = self.check_control_number(session=session)
            else:
                while not valid_ctrl_num:
                    self.last_used = self.last_used - 1
                    valid_ctrl_num = self.check_control_number(session=session)
        self.next_number = max(self.used_numbers) + 1
        logger.info(f"Next control number is {self._format(self.next_number)}.")

    def _format(self, number: int) -> str:
        return f"nn-mlnyc-{number:07d}"

    def next_control_number(self) -> str:
        number = self.next_number
        self.used_numbers.add(number)
        self.next_number += 1
        return self._format(number)

    def save_state(self) -> None:
        json_data = json.dumps({"used_numbers": sorted(self.used_numbers)})
        self.state_path.write_text(json_data)

    def check_control_number(self, session: PlatformManager) -> bool:
        ctrl_number = self._format(number=self.last_used)
        bib_data = session.search_platform_bibs(control_number=ctrl_number)
        if bib_data:
            logger.debug(f"{ctrl_number} found in Sierra.")
            self.used_numbers.add(self.last_used)
            return True
        logger.debug(f"{ctrl_number} not found in Sierra.")
        self.used_numbers.discard(self.last_used)
        return False
