import json
import logging
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

from src.util.runner import Runner


logger = logging.getLogger(__name__)


class Cleaner:
    CUT_MARKERS = [
        "GovDelivery Signup",
        "function getArgs()",
        "function load(",
        "PAT Social Media",
        "@import url(",
        "html { scroll-behavior",
        "Back to top",
    ]

    MIN_TEXT_LENGTH = 30

    RESERVATION_DATA_PATTERN = re.compile(
        r"var\s+reservation_data\s*=\s*\[.*?\];\s*var\s+script_version\s*=\s*['\"].*?['\"];?",
        re.IGNORECASE,
    )

    RESERVATION_DATA_FALLBACK_PATTERN = re.compile(
        r"var\s+reservation_data\s*=\s*\[.*?\];",
        re.IGNORECASE,
    )

    def __init__(self, path, max_workers=None):
        self.path = Path(path)
        self.cleaned_file = (
            self.path.parent / f"{self.path.stem}_cleaned{self.path.suffix}"
        )
        self.runner = Runner(max_workers=max_workers)

    def clean(self) -> Path:
        stats = {
            "total": 0,
            "written": 0,
            "dropped_empty": 0,
            "dropped_error": 0,
            "dropped_invalid_json": 0,
            "dropped_too_short": 0,
        }

        with self.cleaned_file.open("w", encoding="utf-8") as dst:
            lines = []
            with self.path.open("r", encoding="utf-8") as src:
                for raw_line in src:
                    line = raw_line.strip()
                    if not line:
                        continue

                    stats["total"] += 1
                    lines.append(line)

            for result in self.runner.run_many(self._clean_line, lines):
                if not result:
                    continue

                status = result["status"]
                if status == "ok":
                    # Write each cleaned row as soon as it is ready.
                    dst.write(json.dumps(result["record"], ensure_ascii=False) + "\n")
                    stats["written"] += 1
                elif status in stats:
                    stats[status] += 1

        logger.info(
            "Wrote %s cleaned records to %s", stats["written"], self.cleaned_file
        )
        logger.info(
            "Dropped: empty=%s error=%s invalid_json=%s too_short=%s",
            stats["dropped_empty"],
            stats["dropped_error"],
            stats["dropped_invalid_json"],
            stats["dropped_too_short"],
        )

        return self.cleaned_file

    def _clean_line(self, line):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            return {"status": "dropped_invalid_json"}

        if record.get("error"):
            return {"status": "dropped_error"}

        section_text = record.get("sectionText")
        if not isinstance(section_text, str) or not section_text.strip():
            return {"status": "dropped_empty"}

        cleaned_text = self._clean_section_text(
            text=section_text,
            section_heading=(record.get("sectionHeading") or "").strip(),
            page_heading=(record.get("pageHeading") or "").strip(),
            park_name=(record.get("parkName") or "").strip(),
        )

        if len(cleaned_text) < self.MIN_TEXT_LENGTH:
            return {"status": "dropped_too_short"}

        essential = {
            "parkName": record.get("parkName", ""),
            "parkUrl": record.get("parkUrl", ""),
            "sectionId": record.get("sectionId", ""),
            "sectionUrl": record.get("sectionUrl", ""),
            "finalUrl": record.get("finalUrl", ""),
            "pageTitle": record.get("pageTitle", ""),
            "pageHeading": record.get("pageHeading", ""),
            "sectionHeading": record.get("sectionHeading", ""),
            "sectionFound": record.get("sectionFound"),
            "fetchedAt": record.get("fetchedAt", ""),
            "cleanedAt": datetime.now(timezone.utc).isoformat(),
            "cleanText": cleaned_text,
        }

        return {"status": "ok", "record": essential}

    def _clean_section_text(self, text, section_heading, page_heading, park_name):
        cleaned = self._normalize_whitespace(unescape(text))

        # Remove huge embedded reservation JSON blob that dominates the scraped text.
        cleaned = self.RESERVATION_DATA_PATTERN.sub(" ", cleaned)
        cleaned = self.RESERVATION_DATA_FALLBACK_PATTERN.sub(" ", cleaned)

        # Start from a human-facing anchor when possible.
        del park_name
        anchor = section_heading or page_heading
        if anchor:
            index = cleaned.lower().find(anchor.lower())
            if index >= 0:
                cleaned = cleaned[index:]

        # Cut away trailing scripts/styles/footer boilerplate.
        end = len(cleaned)
        for marker in self.CUT_MARKERS:
            index = cleaned.find(marker)
            if index >= 0 and index < end:
                end = index
        cleaned = cleaned[:end]

        # Remove the most common template remnants.
        cleaned = re.sub(r"<%.*?%>", " ", cleaned)
        cleaned = cleaned.replace("Page Menu", " ")
        cleaned = cleaned.replace("loading...", " ")
        return self._normalize_whitespace(cleaned)

    @staticmethod
    def _normalize_whitespace(text):
        return re.sub(r"\s+", " ", text).strip()
