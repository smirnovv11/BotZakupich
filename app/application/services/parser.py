"""Application-facing local parser service."""

from app.domain.parsing import ParsedItemCandidate, split_message_into_item_candidates


class LocalMessageParser:
    def split(self, raw_text: str) -> list[ParsedItemCandidate]:
        return split_message_into_item_candidates(raw_text)
