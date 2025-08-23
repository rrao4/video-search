from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

EMBEDDING_DIM = 768  # set to embedding dimension of the CLIP model. Assuming clip-ViT-L-14


class Base(DeclarativeBase):
    pass


class Video(Base):
    __tablename__ = "video"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # video metadata fields
    aspect_ratio: Mapped[str | None] = mapped_column(String, nullable=True)
    genre: Mapped[str | None] = mapped_column(String, nullable=True)

    video_property_values: Mapped[list["VideoPropertyValue"]] = relationship(
        back_populates="video",
        cascade="all, delete-orphan",
    )

    property_values: Mapped[list["PropertyValue"]] = relationship(
        secondary="video_property_value",
        primaryjoin="Video.id == VideoPropertyValue.video_id",
        secondaryjoin="PropertyValue.id == VideoPropertyValue.property_value_id",
        viewonly=True,
    )

    embeddings: Mapped[list["VideoEmbedding"]] = relationship(
        back_populates="video",
        cascade="all, delete-orphan",
    )

    descriptions: Mapped[list["VideoDescription"]] = relationship(
        back_populates="video",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("path", name="uq_video_path"),
    )

    def __repr__(self) -> str:
        return f"Video(id={self.id!r}, path={self.path!r})"


class Property(Base):
    __tablename__ = "property"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # self-reference field for hierarchical categories
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("property.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    display_order: Mapped[int | None] = mapped_column(Integer, nullable=True)

    parent: Mapped["Property | None"] = relationship(
        remote_side="Property.id", back_populates="children"
    )

    children: Mapped[list["Property"]] = relationship(
        back_populates="parent",
        passive_deletes=True,
    )

    values: Mapped[list["PropertyValue"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"Property(id={self.id!r}, name={self.name!r}, "
            f"parent_id={self.parent_id!r}, display_order={self.display_order!r})"
        )


class PropertyValue(Base):
    __tablename__ = "property_value"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("property.id", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[str] = mapped_column(String, nullable=False)
    display_order: Mapped[int | None] = mapped_column(Integer, nullable=True)

    property: Mapped["Property"] = relationship(back_populates="values")

    videos: Mapped[list["Video"]] = relationship(
        secondary="video_property_value",
        primaryjoin="PropertyValue.id == VideoPropertyValue.property_value_id",
        secondaryjoin="Video.id == VideoPropertyValue.video_id",
        viewonly=True,
    )

    __table_args__ = (
        UniqueConstraint("property_id", "value", name="uq_property_value_property_id_value"),
        Index("ix_property_value_property_id", "property_id"),
    )

    def __repr__(self) -> str:
        return (
            f"PropertyValue(id={self.id!r}, property_id={self.property_id!r}, "
            f"value={self.value!r}, display_order={self.display_order!r})"
        )


class VideoPropertyValue(Base):
    __tablename__ = "video_property_value"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    video_id: Mapped[int] = mapped_column(
        ForeignKey("video.id", ondelete="CASCADE"), nullable=False
    )
    property_value_id: Mapped[int] = mapped_column(
        ForeignKey("property_value.id", ondelete="CASCADE"), nullable=False
    )

    video: Mapped["Video"] = relationship(back_populates="video_property_values")
    property_value: Mapped["PropertyValue"] = relationship()

    __table_args__ = (
        Index("ix_video_property_value_property_value_id", "property_value_id"),
        Index("ix_video_property_value_video_id", "video_id"),
        UniqueConstraint("video_id", "property_value_id", name="uq_video_property_value_once"),
    )

    def __repr__(self) -> str:
        return (
            f"VideoPropertyValue(id={self.id!r}, video_id={self.video_id!r}, "
            f"property_value_id={self.property_value_id!r})"
        )


class VideoEmbedding(Base):
    __tablename__ = "video_embedding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    video_id: Mapped[int] = mapped_column(
        ForeignKey("video.id", ondelete="CASCADE"), nullable=False
    )
    # embeddings associated with the video
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)

    video: Mapped["Video"] = relationship(back_populates="embeddings")

    __table_args__ = (
        Index(
            "ix_video_embedding_hnsw_cos",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
            postgresql_with={"m": 16, "ef_construction": 64},
        ),
    )

    def __repr__(self) -> str:
        return f"VideoEmbedding(id={self.id!r}, video_id={self.video_id!r})"


class VideoDescription(Base):
    __tablename__ = "video_description"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    video_id: Mapped[int] = mapped_column(
        ForeignKey("video.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str] = mapped_column(String, nullable=False)

    video: Mapped["Video"] = relationship(back_populates="descriptions")

    __table_args__ = (
        Index("ix_video_description_video_id", "video_id"),
    )

    def __repr__(self) -> str:
        preview = (self.description[:30] + "…") if self.description and len(self.description) > 30 else self.description
        return f"VideoDescription(id={self.id!r}, video_id={self.video_id!r}, description={preview!r})"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    # store hashes for user passwords
    password: Mapped[str] = mapped_column(String(128), nullable=False)

    owned_collections: Mapped[list["Collection"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

    collection_memberships: Mapped[list["UserCollection"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # collections shared with this user
    shared_collections: Mapped[list["Collection"]] = relationship(
        secondary="user_collection",
        primaryjoin="User.id == UserCollection.user_id",
        secondaryjoin="Collection.id == UserCollection.collection_id",
        viewonly=True,
    )

    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"


class Collection(Base):
    __tablename__ = "collection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collection_name: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    owner: Mapped["User"] = relationship(back_populates="owned_collections")

    shares: Mapped[list["UserCollection"]] = relationship(
        back_populates="collection", cascade="all, delete-orphan"
    )

    # which users have access to this collection
    shared_with_users: Mapped[list["User"]] = relationship(
        secondary="user_collection",
        primaryjoin="Collection.id == UserCollection.collection_id",
        secondaryjoin="User.id == UserCollection.user_id",
        viewonly=True,
    )

    collection_videos: Mapped[list["CollectionVideo"]] = relationship(
        back_populates="collection", cascade="all, delete-orphan"
    )

    videos: Mapped[list["Video"]] = relationship(
        secondary="collection_video",
        primaryjoin="Collection.id == CollectionVideo.collection_id",
        secondaryjoin="Video.id == CollectionVideo.video_id",
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f"Collection(id={self.id!r}, name={self.collection_name!r}, owner_id={self.owner_id!r})"


class UserCollection(Base):
    __tablename__ = "user_collection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collection.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="collection_memberships")
    collection: Mapped["Collection"] = relationship(back_populates="shares")

    __table_args__ = (
        UniqueConstraint("user_id", "collection_id", name="uq_user_collection_user_id_collection_id"),
        Index("ix_user_collection_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"UserCollection(id={self.id!r}, user_id={self.user_id!r}, collection_id={self.collection_id!r})"


class CollectionVideo(Base):
    __tablename__ = "collection_video"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collection.id", ondelete="CASCADE"), nullable=False
    )
    video_id: Mapped[int] = mapped_column(
        ForeignKey("video.id", ondelete="CASCADE"), nullable=False
    )

    collection: Mapped["Collection"] = relationship(back_populates="collection_videos")
    video: Mapped["Video"] = relationship()

    __table_args__ = (
        UniqueConstraint("collection_id", "video_id", name="uq_collection_video_collection_id_video_id"),
        Index("ix_collection_video_collection_id", "collection_id"),
    )

    def __repr__(self) -> str:
        return f"CollectionVideo(id={self.id!r}, collection_id={self.collection_id!r}, video_id={self.video_id!r})"
