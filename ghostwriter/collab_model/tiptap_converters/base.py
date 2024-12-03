
from abc import ABC, abstractmethod
from typing import Any, Generic, Iterable, TypeVar, TypeVarTuple, Unpack

Args = TypeVarTuple("Args")
Out = TypeVar("Out")

class NoHandlerException(Exception):
    """
    Thrown when an unrecognized tag/mark name is passed to `dispatch_tag` or `dispatch_mark`
    """
    name: str
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = name

class TiptapTagHandlerMixin(ABC, Generic[Out, Unpack[Args]]):
    """
    ABC that specifies handler functions for TipTap tags.

    Available tags are based on the schema for the editor in `frontend/colalb_editor/editor.tsx` -
    Edit this if changes to the schema are made.
    """

    def dispatch_tag(self, tag: str, attr_changes: Iterable[tuple[str, Any | None]], *args: Unpack[Args]) -> Out:
        try:
            method = getattr(self, f"apply_tag_{tag}")
        except AttributeError as e:
            raise NoHandlerException(tag) from e
        return method(attr_changes, *args)

    @abstractmethod
    def apply_tag_paragraph(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass

    @abstractmethod
    def apply_tag_header(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass

    @abstractmethod
    def apply_tag_blockquote(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass

    @abstractmethod
    def apply_tag_table(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass

    @abstractmethod
    def apply_tag_tableRow(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass

    @abstractmethod
    def apply_tag_tableCell(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass

    @abstractmethod
    def apply_tag_tableHeader(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass

    @abstractmethod
    def apply_tag_bulletList(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass

    @abstractmethod
    def apply_tag_orderedList(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass

    @abstractmethod
    def apply_tag_listItem(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass

    @abstractmethod
    def apply_tag_hardBreak(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass

    @abstractmethod
    def apply_tag_codeBlock(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass

    @abstractmethod
    def apply_tag_hardBreak(
        self,
        attr_changes: Iterable[tuple[str, Any | None]],
        *args: Unpack[Args],
    ) -> Out:
        pass



class TiptapMarkHandlerMixin(ABC, Generic[Out, Unpack[Args]]):
    """
    ABC that specifies handler functions for TipTap marks.

    Available marks are based on the schema for the editor in `frontend/colalb_editor/editor.tsx` -
    Edit this if changes to the schema are made.
    """
    def dispatch_mark(self, name: str, attr: Any | None, *args: Unpack[Args]) -> Out:
        try:
            method = getattr(self, f"apply_mark_{name}")
        except AttributeError as e:
            raise NoHandlerException(name) from e
        return method(attr, *args)

    @abstractmethod
    def apply_mark_link(self, attr: Any | None, *args: Unpack[Args]) -> Out:
        pass

    @abstractmethod
    def apply_mark_bold(self, attr: Any | None, *args: Unpack[Args]) -> Out:
        pass

    @abstractmethod
    def apply_mark_code(self, attr: Any | None, *args: Unpack[Args]) -> Out:
        pass

    @abstractmethod
    def apply_mark_italic(self, attr: Any | None, *args: Unpack[Args]) -> Out:
        pass

    @abstractmethod
    def apply_mark_strike(self, attr: Any | None, *args: Unpack[Args]) -> Out:
        pass

    @abstractmethod
    def apply_mark_underline(self, attr: Any | None, *args: Unpack[Args]) -> Out:
        pass
