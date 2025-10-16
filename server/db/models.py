from extensions import db
from pgvector.sqlalchemy import Vector
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

EMBEDDING_DIM = 768  # set to embedding dimension of the CLIP model. Assuming clip-ViT-L-14

# =====================================================
# Video
# =====================================================
class Video(db.Model):
    __tablename__ = "video"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    path = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)

    aspect_ratio = db.Column(db.String, nullable=True)
    genre = db.Column(db.String, nullable=True)

    video_property_values = db.relationship(
        "VideoPropertyValue",
        back_populates="video",
        cascade="all, delete-orphan",
    )

    property_values = db.relationship(
        "PropertyValue",
        secondary="video_property_value",
        primaryjoin="Video.id == VideoPropertyValue.video_id",
        secondaryjoin="PropertyValue.id == VideoPropertyValue.property_value_id",
        viewonly=True,
    )

    embeddings = db.relationship(
        "VideoEmbedding",
        back_populates="video",
        cascade="all, delete-orphan",
    )

    descriptions = db.relationship(
        "VideoDescription",
        back_populates="video",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.UniqueConstraint("path", name="uq_video_path"),
        db.Index("ix_video_name", "name"),
    )

    def __repr__(self):
        return f"Video(id={self.id!r}, path={self.path!r})"
    
    def to_dict(self, include_embeddings=False):
        return {
            "id": self.id,
            "path": self.path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "aspect_ratio": self.aspect_ratio,
            "genre": self.genre,

            "descriptions": [desc.description for desc in self.descriptions],

            "properties": [
                {
                    "property_id": vpv.property_value.property.id if vpv.property_value and vpv.property_value.property else None,
                    "property_name": vpv.property_value.property.name if vpv.property_value and vpv.property_value.property else None,
                    "parent_property": {
                        "id": vpv.property_value.property.parent.id,
                        "name": vpv.property_value.property.parent.name
                    } if vpv.property_value and vpv.property_value.property and vpv.property_value.property.parent else None,
                    "value_id": vpv.property_value.id if vpv.property_value else None,
                    "value": vpv.property_value.value if vpv.property_value else None
                }
                for vpv in self.video_property_values
            ],

            "embeddings": [emb.to_dict() for emb in self.embeddings] if include_embeddings else None,
        }

# =====================================================
# Property
# =====================================================
class Property(db.Model):
    __tablename__ = "property"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("property.id", ondelete="SET NULL"), nullable=True)
    name = db.Column(db.String, nullable=False, unique=True)
    display_order = db.Column(db.Integer, nullable=True)

    parent = db.relationship("Property", remote_side=[id], back_populates="children")
    children = db.relationship("Property", back_populates="parent", passive_deletes=True)

    values = db.relationship(
        "PropertyValue",
        back_populates="property",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"Property(id={self.id!r}, name={self.name!r}, "
            f"parent_id={self.parent_id!r}, display_order={self.display_order!r})"
        )

    def to_dict(self, include_parent=True):
        data = {
            "id": self.id,
            "name": self.name
        }
        if include_parent and self.parent:
            data["parent"] = {"id": self.parent.id, "name": self.parent.name}
        return data
    
    def to_filter_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_order": self.display_order,
            "values": [
                {"id": v.id, "value": v.value} for v in self.values
            ],
            "children": [
                {
                    "id": child.id,
                    "name": child.name,
                    "display_order": child.display_order,
                    "values": [{"id": v.id, "value": v.value} for v in child.values],
                }
                for child in sorted(self.children, key=lambda c: c.display_order or 0)
            ],
        }
# =====================================================
# PropertyValue
# =====================================================
class PropertyValue(db.Model):
    __tablename__ = "property_value"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("property.id", ondelete="CASCADE"), nullable=False)
    value = db.Column(db.String, nullable=False)
    display_order = db.Column(db.Integer, nullable=True)

    property = db.relationship("Property", back_populates="values")

    videos = db.relationship(
        "Video",
        secondary="video_property_value",
        primaryjoin="PropertyValue.id == VideoPropertyValue.property_value_id",
        secondaryjoin="Video.id == VideoPropertyValue.video_id",
        viewonly=True,
    )

    __table_args__ = (
        db.UniqueConstraint("property_id", "value", name="uq_property_value_property_id_value"),
        db.Index("ix_property_value_property_id", "property_id"),
    )

    def __repr__(self):
        return (
            f"PropertyValue(id={self.id!r}, property_id={self.property_id!r}, "
            f"value={self.value!r}, display_order={self.display_order!r})"
        )

    def to_dict(self, include_property=False):
            data = {
                "id": self.id,
                "value": self.value,
                "property_id": self.property_id,
            }
            if include_property and self.property:
                data["property"] = self.property.to_dict()
            return data
# =====================================================
# VideoPropertyValue
# =====================================================
class VideoPropertyValue(db.Model):
    __tablename__ = "video_property_value"

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("video.id", ondelete="CASCADE"), nullable=False)
    property_value_id = db.Column(db.Integer, db.ForeignKey("property_value.id", ondelete="CASCADE"), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False, default=0.0)

    video = db.relationship("Video", back_populates="video_property_values")
    property_value = db.relationship("PropertyValue")

    __table_args__ = (
        db.Index("ix_video_property_value_property_value_id", "property_value_id"),
        db.Index("ix_video_property_value_video_id", "video_id"),
        db.Index("ix_video_property_value_confidence_score", "confidence_score"),
        db.UniqueConstraint("video_id", "property_value_id", name="uq_video_property_value_once"),
        db.CheckConstraint("confidence_score >= 0.0 AND confidence_score <= 1.0", name="ck_video_property_value_confidence_score_range"),
    )

    def __repr__(self):
        return (
            f"VideoPropertyValue(id={self.id!r}, video_id={self.video_id!r}, "
            f"property_value_id={self.property_value_id!r})"
        )


# =====================================================
# VideoEmbedding
# =====================================================
class VideoEmbedding(db.Model):
    __tablename__ = "video_embedding"

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("video.id", ondelete="CASCADE"), nullable=False)

    # Use pgvector instead of ARRAY
    embedding = db.Column(Vector(EMBEDDING_DIM), nullable=False)

    video = db.relationship("Video", back_populates="embeddings")

    __table_args__ = (
        db.Index(
            "ix_video_embedding_hnsw_cos",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
            postgresql_with={"m": 16, "ef_construction": 64},
        ),
    )

    def __repr__(self):
        return f"VideoEmbedding(id={self.id!r}, video_id={self.video_id!r})"
    
    def to_dict(self):
        return {
            "id": self.id,
            "video_id": self.video_id,
            "embedding": self.embedding.tolist() if self.embedding else None
        }


# =====================================================
# VideoDescription
# =====================================================
class VideoDescription(db.Model):
    __tablename__ = "video_description"

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("video.id", ondelete="CASCADE"), nullable=False)
    description = db.Column(db.String, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False, default=0.0)

    video = db.relationship("Video", back_populates="descriptions")

    __table_args__ = (
        db.Index("ix_video_description_video_id", "video_id"),
        db.Index("ix_video_description_confidence_score", "confidence_score"),
        db.CheckConstraint("confidence_score >= 0.0 AND confidence_score <= 1.0", name="ck_video_description_confidence_score_range"),
    )

    def __repr__(self):
        preview = (self.description[:30] + "…") if self.description and len(self.description) > 30 else self.description
        return f"VideoDescription(id={self.id!r}, video_id={self.video_id!r}, description={preview!r})"


# =====================================================
# User
# =====================================================
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    #password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    hashed_password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


    owned_collections = db.relationship("Collection", back_populates="owner", cascade="all, delete-orphan")
    collection_memberships = db.relationship("UserCollection", back_populates="user", cascade="all, delete-orphan")

    shared_collections = db.relationship(
        "Collection",
        secondary="user_collection",
        primaryjoin="User.id == UserCollection.user_id",
        secondaryjoin="Collection.id == UserCollection.collection_id",
        viewonly=True,
    )

    __table_args__ = (
        db.UniqueConstraint("username", name="uq_users_username"),
    )

    def __repr__(self):
        return f"User(id={self.id!r}, username={self.username!r})"
    
    @property
    def password(self):
        return self.hashed_password

    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, plaintext_password):
        return check_password_hash(self.password, plaintext_password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


# =====================================================
# Collection
# =====================================================
class Collection(db.Model):
    __tablename__ = "collection"

    id = db.Column(db.Integer, primary_key=True)
    collection_name = db.Column(db.String, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = db.relationship("User", back_populates="owned_collections")

    shares = db.relationship("UserCollection", back_populates="collection", cascade="all, delete-orphan")

    shared_with_users = db.relationship(
        "User",
        secondary="user_collection",
        primaryjoin="Collection.id == UserCollection.collection_id",
        secondaryjoin="User.id == UserCollection.user_id",
        viewonly=True,
    )

    collection_videos = db.relationship("CollectionVideo", back_populates="collection", cascade="all, delete-orphan")

    videos = db.relationship(
        "Video",
        secondary="collection_video",
        primaryjoin="Collection.id == CollectionVideo.collection_id",
        secondaryjoin="Video.id == CollectionVideo.video_id",
        viewonly=True,
    )

    __table_args__ = (
        db.Index("ix_collection_owner_id", "owner_id"),
    )


    def to_dict(self):
        return {
            'id': self.id,
            'collection_name': self.collection_name,
            'owner_id': self.owner_id,
        }
    def __repr__(self):
        return f"Collection(id={self.id!r}, name={self.collection_name!r}, owner_id={self.owner_id!r})"


# =====================================================
# UserCollection
# =====================================================
class UserCollection(db.Model):
    __tablename__ = "user_collection"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey("collection.id", ondelete="CASCADE"), nullable=False)

    user = db.relationship("User", back_populates="collection_memberships")
    collection = db.relationship("Collection", back_populates="shares")

    __table_args__ = (
        db.UniqueConstraint("user_id", "collection_id", name="uq_user_collection_user_id_collection_id"),
        db.Index("ix_user_collection_user_id", "user_id"),
    )

    def __repr__(self):
        return f"UserCollection(id={self.id!r}, user_id={self.user_id!r}, collection_id={self.collection_id!r})"


# =====================================================
# CollectionVideo
# =====================================================
class CollectionVideo(db.Model):
    __tablename__ = "collection_video"

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey("collection.id", ondelete="CASCADE"), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey("video.id", ondelete="CASCADE"), nullable=False)

    collection = db.relationship("Collection", back_populates="collection_videos")
    video = db.relationship("Video")

    __table_args__ = (
        db.UniqueConstraint("collection_id", "video_id", name="uq_collection_video_collection_id_video_id"),
        db.Index("ix_collection_video_collection_id", "collection_id"),
    )

    def __repr__(self):
        return f"CollectionVideo(id={self.id!r}, collection_id={self.collection_id!r}, video_id={self.video_id!r})"


