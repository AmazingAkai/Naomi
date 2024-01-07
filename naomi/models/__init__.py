from __future__ import annotations

from typing import TYPE_CHECKING

from .actions import Action
from .challenges import Challenge

if TYPE_CHECKING:
    from beanie import Document, View

    DOCUMENT_MODELS = list[type[Document] | type[View] | str] | None

__all__ = ("document_models",)

document_models: DOCUMENT_MODELS = [
    Challenge,
    Action,
]
