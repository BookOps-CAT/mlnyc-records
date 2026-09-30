from __future__ import annotations

import logging
import os
from typing import Any

from bookops_worldcat import MetadataSession, WorldcatAccessToken
from pymarc import Field, Record

logger = logging.getLogger(__name__)


class BriefBibResponse:
    def __init__(self, wc_response: dict[str, Any]) -> None:
        self.cat_level: str | None = wc_response.get("catalogingInfo", {}).get(
            "levelOfCataloging"
        )
        self.oclc_number = wc_response["oclcNumber"]

    def sort_key(self) -> tuple[int, int]:
        if self.cat_level in [" ", "I"]:
            return (0, 0)
        if self.cat_level is None:
            return (2, 0)
        if self.cat_level in ["K", "L", "M"]:
            return (1, 9)
        return (1, int(self.cat_level))


class FullWorldCatResponse:
    def __init__(self, isbn: str, wc_response: Record) -> None:
        self.isbn = isbn
        self.record = wc_response

        if self.isbn and not self.isbn.isnumeric():
            self.isbn = self.record.isbn

    @property
    def author_data(self) -> Field | None:
        field = (
            self.record.get("100") or self.record.get("110") or self.record.get("111")
        )
        return field if field else None

    @property
    def author_name(self) -> str | None:
        if not self.author_data:
            return None
        return self.author_data["a"].rstrip(" ,")

    @property
    def author_dates(self) -> str | None:
        if not self.author_data:
            return None
        return self.author_data.get("d", "").rstrip(",")

    @property
    def description(self) -> str:
        try:
            return self.record["520"].format_field()
        except KeyError:
            return ""

    @property
    def pub_date(self) -> str | None:
        pub_date = self.record.pubyear
        if isinstance(pub_date, str) and "-" not in pub_date:
            return pub_date.strip("[].")
        elif isinstance(pub_date, str) and "-" in pub_date:
            return pub_date.strip(".")
        return pub_date

    @property
    def title(self) -> str:
        title_field = self.record["245"]
        title = self.record.title
        title_part = title_field.get("p")
        if title_part:
            title += f" {title_part}"
        return title.strip(" :/.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "author_name": self.author_name,
            "author_dates": self.author_dates,
            "description": self.description,
            "pub_date": self.pub_date,
            "title": self.title,
            "isbn": self.isbn,
        }


class WorldcatManager:
    FORMAT_MAPPING = {
        "dvd": "x4:DVD",
        "playaway": "x0:AudioBook AND kw:playaway",
        "lprint": "x4:LargePrint",
        "book": "x4:PrintBook",
    }

    def __init__(self) -> None:
        self.worldcat_token = WorldcatAccessToken(
            key=os.environ["WORLDCAT_KEY"],
            secret=os.environ["WORLDCAT_SECRET"],
            scopes="WorldCatMetadataAPI",
        )
        self.session = None

    def __enter__(self, *args, **kwargs) -> WorldcatManager:
        self.session = MetadataSession(
            authorization=self.worldcat_token, timeout=(10, 10), totalRetries=2
        )
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.session.close()

    def parse_brief_bib(self, brief_records: list[dict[str, Any]]) -> list[str]:
        parsed_responses = [BriefBibResponse(i) for i in brief_records]
        parsed_responses = sorted(parsed_responses, key=BriefBibResponse.sort_key)
        return [i.oclc_number for i in parsed_responses]

    def get_full_record(self, isbn: str, oclc_number: str) -> FullWorldCatResponse:
        logger.debug(f"OCLC number `{oclc_number}`: retrieving full bib record.")
        full_bib_response = self.session.bib_get(
            oclcNumber=oclc_number, responseFormat="application/marc"
        )
        record = Record(data=full_bib_response.content)  # type: ignore
        return FullWorldCatResponse(isbn=isbn, wc_response=record)

    def get_oclc_number_from_id(
        self, isbn: str, index: str, format: str, title: str | None = None
    ) -> list[dict[str, Any]]:
        logger.debug(f"ISBN/UPC `{isbn}`: searching brief bib records.")
        format_attrs = self.FORMAT_MAPPING.get(format)
        if format_attrs:
            brief_bibs = self.search_brief_bibs(
                query=f"{index}:{isbn} AND {format_attrs}"
            )
        else:
            brief_bibs = self.search_brief_bibs(query=f"{index}:{isbn}")
        if brief_bibs:
            return brief_bibs
        if title:
            logger.debug(f"Title `{title}`: searching brief bib records.")
        if title and format_attrs:
            brief_bibs = self.search_brief_bibs(query=f"ti:{title} AND {format_attrs}")
        elif title and not format_attrs:
            brief_bibs = self.search_brief_bibs(query=f"ti:{title}")
        if brief_bibs:
            return brief_bibs
        logger.info(
            f"No records found in WorldCat for `{index}:{isbn}`, "
            f"`ti:{title}` and `{format}`."
        )
        return None

    def search_brief_bibs(self, query: str) -> list[dict[str, Any]]:
        brief_bib = self.session.brief_bibs_search(q=query)
        brief_bib_json = brief_bib.json()
        brief_records = brief_bib_json.get("briefRecords", [])
        if not brief_records:
            logger.debug(f"{len(brief_records)} records found for `{query}`.")
        return self.parse_brief_bib(brief_records=brief_records)

    def get_worldcat_data_for_part(
        self,
        isbn: str,
        index: str,
        format: str | None = "book",
        title: str | None = None,
    ) -> dict[str, Any]:
        oclc_numbers = self.get_oclc_number_from_id(
            isbn=isbn, index=index, format=format, title=title
        )
        if not oclc_numbers:
            return {
                "author_name": None,
                "author_dates": None,
                "description": "",
                "pub_date": None,
                "title": title,
                "isbn": isbn,
            }
        first_rec = None
        for oclc in oclc_numbers:
            full_rec = self.get_full_record(oclc_number=oclc, isbn=isbn)
            if not full_rec.description:
                logger.debug(
                    f"Full bib record for `{oclc}` missing description. "
                    f"Checking next record if present."
                )
                first_rec = full_rec
                continue
            else:
                return full_rec.to_dict()
        return first_rec.to_dict()
