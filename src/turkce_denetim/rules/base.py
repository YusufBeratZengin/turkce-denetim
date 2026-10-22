"""Kural motoru temel sinif ve arayuzleri."""

from __future__ import annotations

from abc import ABC, abstractmethod

from turkce_denetim.models import Document, Finding, Severity


class Rule(ABC):
    """Tum denetim kurallarinin tureyecegi soyut temel sinif."""

    id: str
    name: str
    description: str
    severity: Severity
    suggestion: str

    def create_finding(
        self,
        message: str,
        line: int,
        column: int,
        end_line: int,
        end_column: int,
        suggestion: str | None = None,
        context: str | None = None,
    ) -> Finding:
        """Bulgu olusturma yardimcisi."""
        return Finding(
            rule_id=self.id,
            rule_name=self.name,
            message=message,
            severity=self.severity,
            line=line,
            column=column,
            end_line=end_line,
            end_column=end_column,
            suggestion=suggestion or self.suggestion,
            context=context,
        )

    @abstractmethod
    def check(self, document: Document) -> list[Finding]:
        """Belgeyi denetler ve kural ihlallerini bulgu listesi olarak dondurur."""
        pass
