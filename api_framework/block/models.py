from enum import StrEnum
from uuid import UUID

from pydantic import Field, ConfigDict
from sqlalchemy import ARRAY, JSON
from sqlmodel import Relationship

from api_framework.common.models import AppBaseModel


class BlockType(StrEnum):
    KEY_VALUE_SET = "KEY_VALUE_SET"
    PAGE = "PAGE"
    LINE = "LINE"
    WORD = "WORD"
    TABLE = "TABLE"
    CELL = "CELL"
    SELECTION_ELEMENT = "SELECTION_ELEMENT"
    MERGED_CELL = "MERGED_CELL"
    TITLE = "TITLE"
    QUERY = "QUERY"
    QUERY_RESULT = "QUERY_RESULT"
    SIGNATURE = "SIGNATURE"
    TABLE_TITLE = "TABLE_TITLE"
    TABLE_FOOTER = "TABLE_FOOTER"
    LAYOUT_TEXT = "LAYOUT_TEXT"
    LAYOUT_TITLE = "LAYOUT_TITLE"
    LAYOUT_HEADER = "LAYOUT_HEADER"
    LAYOUT_FOOTER = "LAYOUT_FOOTER"
    LAYOUT_SECTION_HEADER = "LAYOUT_SECTION_HEADER"
    LAYOUT_PAGE_NUMBER = "LAYOUT_PAGE_NUMBER"
    LAYOUT_LIST = "LAYOUT_LIST"
    LAYOUT_FIGURE = "LAYOUT_FIGURE"
    LAYOUT_TABLE = "LAYOUT_TABLE"
    LAYOUT_KEY_VALUE = "LAYOUT_KEY_VALUE"


class EntityType(StrEnum):
    KEY = "KEY"
    VALUE = "VALUE"
    COLUMN_HEADER = "COLUMN_HEADER"
    TABLE_TITLE = "TABLE_TITLE"
    TABLE_FOOTER = "TABLE_FOOTER"
    TABLE_SECTION_TITLE = "TABLE_SECTION_TITLE"
    TABLE_SUMMARY = "TABLE_SUMMARY"
    STRUCTURED_TABLE = "STRUCTURED_TABLE"
    SEMI_STRUCTURED_TABLE = "SEMI_STRUCTURED_TABLE"


class RelationshipType(StrEnum):
    VALUE = "VALUE"
    CHILD = "CHILD"
    COMPLEX_FEATURES = "COMPLEX_FEATURES"
    MERGED_CELL = "MERGED_CELL"
    TITLE = "TITLE"
    ANSWER = "ANSWER"
    TABLE = "TABLE"
    TABLE_TITLE = "TABLE_TITLE"
    TABLE_FOOTER = "TABLE_FOOTER"


class TextType(StrEnum):
    HANDWRITING = "HANDWRITING"
    PRINTED = "PRINTED"


class SelectionStatus(StrEnum):
    SELECTED = "SELECTED"
    NOT_SELECTED = "NOT_SELECTED"


class BlockBaseTableModel(AppBaseModel):
    __table_args__ = {"schema": "block"}

    # Common fields for all block types
    block_id: UUID = Field(foreign_key="block.block_id")
    text: str | None = Field(max_length=1000, nullable=True)
    confidence: float | None = None
    text_type: TextType | None = None
    entity_types: ARRAY[str]
    row_index: int | None = None
    column_index: int | None = None
    row_span: int | None = None
    column_span: int | None = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class BlockGeometry(BlockBaseTableModel, table=True):
    __tablename__ = "block_geometry"

    height: float
    left: float
    top: float
    width: float
    polygon_points: JSON

    block: "Block" = Relationship(back_populates="geometry")


class BlockRelationship(BlockBaseTableModel, table=True):
    __tablename__ = "block_relationship"

    related_block_id: UUID = Field(foreign_key="block.block_id")
    relationship_type: RelationshipType

    block: "Block" = Relationship(
        back_populates="relationships",
        cascade_delete=True,
    )
    related_block: "Block" = Relationship(
        back_populates="related_relationships",
        cascade_delete=True,
    )


class Block(BlockBaseTableModel, table=True):
    __tablename__ = "block"

    block_type: BlockType
    selection_status: SelectionStatus | None = None
    page: int
    query: dict | None = Field(default_factory=dict)

    # Relationships
    geometry: BlockGeometry | None = Relationship(back_populates="block")
    relationships: list[BlockRelationship] = Relationship(
        back_populates="block",
        sa_relationship_kwargs={"foreign_keys": [BlockRelationship.block_id]},
    )
    related_relationships: list[BlockRelationship] = Relationship(
        back_populates="related_block",
        sa_relationship_kwargs={"foreign_keys": [BlockRelationship.related_block_id]},
    )

    # Block type specific relationships
    page_block: "PageBlock" | None = Relationship(back_populates="block")
    line_block: "LineBlock" | None = Relationship(back_populates="block")
    word_block: "WordBlock" | None = Relationship(back_populates="block")
    table_block: "TableBlock" | None = Relationship(back_populates="block")
    cell_block: "CellBlock" | None = Relationship(back_populates="block")
    selection_element_block: "SelectionElementBlock" | None = Relationship(
        back_populates="block"
    )
    merged_cell_block: "MergedCellBlock" | None = Relationship(back_populates="block")
    key_value_set_block: "KeyValueSetBlock" | None = Relationship(
        back_populates="block"
    )


class PageBlock(BlockBaseTableModel, table=True):
    __tablename__ = "page_block"

    page_number: int

    block: Block = Relationship(back_populates="page_block")


class LineBlock(BlockBaseTableModel, table=True):
    __tablename__ = "line_block"

    block: Block = Relationship(back_populates="line_block")


class WordBlock(BlockBaseTableModel, table=True):
    __tablename__ = "word_block"

    block: Block = Relationship(back_populates="word_block")


class TableBlock(BlockBaseTableModel, table=True):
    __tablename__ = "table_block"

    title: str | None = Field(max_length=1000, nullable=True)
    footer: str | None = Field(max_length=1000, nullable=True)
    summary: str | None = Field(max_length=1000, nullable=True)

    block: Block = Relationship(back_populates="table_block")


class CellBlock(BlockBaseTableModel, table=True):
    __tablename__ = "cell_block"

    block: Block = Relationship(back_populates="cell_block")


class SelectionElementBlock(BlockBaseTableModel, table=True):
    __tablename__ = "selection_element_block"

    selection_status: SelectionStatus

    block: Block = Relationship(back_populates="selection_element_block")


class MergedCellBlock(BlockBaseTableModel, table=True):
    __tablename__ = "merged_cell_block"

    block: Block = Relationship(back_populates="merged_cell_block")


class KeyValueSetBlock(BlockBaseTableModel, table=True):
    __tablename__ = "key_value_set_block"

    key_block_id: UUID = Field(foreign_key="block.block.id")
    value_block_id: UUID = Field(foreign_key="block.block.id")

    block: Block = Relationship(back_populates="key_value_set_block")
    key_block: Block = Relationship(
        sa_relationship_kwargs={"foreign_keys": [key_block_id]}
    )
    value_block: Block = Relationship(
        sa_relationship_kwargs={"foreign_keys": [value_block_id]}
    )
