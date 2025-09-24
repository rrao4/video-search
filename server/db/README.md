# Database Design

The database is designed for a website that allows users to filter a dataset of videos based on tags and text-to-video search. At a high-level, it stores
- Videos and their metadata
- A hierarchical label/tagging system
- Per-video embeddings for semantic search (pgvector is a Postgres extension that provides a Vector type for the column)
- Video descriptions
- Users, collections, sharing, and collection contents

SQLAlchemy relationships work on the Python-side and do not affect the database itself. They simplify working with database tables that are connected through foreign keys by using SQL queries under the hood. For instance, if you have a `Property` object `property1`, then `property1.values` gives you the `PropertyValue` objects associated with `property1`, and you can add and remove `PropertyValue` objects from `property1` as well. More relationships can be added as needed for convenience.

---

## Tables

### `video`

**Purpose:** Represents the video and stores its metadata

**Columns:** 
- `id`: PK
- `path`: the ID path for where the video is stored (e.g. S3 object ARN)
- `created_at`: when the video record was added
- `aspect_ratio?`: metadata column for the video's aspect ratio
- `genre?`: metadata column for the video's genre
  
**Uniqueness:**
- `path`: the same video path should not be stored twice

More metadata columns can be added.

---

### `property`

**Purpose:** Stores the hierarchical categories that labels fall under. Every property is stored as a row, which allows new properties to be added flexibly.

**Columns:**
- `id`: PK
- `name`: category name
- `display_order?`: optional numeric ordering hint for UI
- `parent_id?`: self-referential FK to `property.id`, which refers to the parent category one level higher. For example "camera-movement" could be a property with `id=1` and `parent_id=NULL`, then "translation" could be a subcategory with `id=2` and `parent_id=1`, making it a subcategory of "camera-movement".

---

### `property_value`

**Purpose:** Stores the concrete labels under a property (e.g., "minimal-shaking" could be one of the labels under the "shaking" property). Every label is stored as a row, which allows new labels to be added flexibly. One property can have many concrete labels, and not all properties from the `property` table will be referred to in this table, since some properties will contain sub-properties.

**Columns:**
- `id`: PK
- `property_id`: FK to `property.id`, representing the property this label is associated with. There can be many labels associated with a single property.
- `value`: label text (e.g. "minimal-shaking", "tilt-down")
- `display_order?`: optional numeric ordering hint for UI

**Uniqueness:**
- `(property_id, value)`: this is unique since the same property should not have the same value twice

**Index:** 
- `property_id`: make searches like "search all labels where property_id=x" faster (this type of search is needed for displaying the labels on the UI)

---

### `video_property_value`

**Purpose:** The association table that applies labels to videos. Each row represents a video which contains some tag. One label can be associated with many different videos and one video can be associated with many different labels. This is the main table that actually tags each video, and the filtered videos will be queried from this table.

**Columns:**
- `id`: PK
- `video_id`: FK to `video.id`, representing the video that contains the label `property_value_id` refers to.
- `property_value_id`: FK to `property_value.id`, representing the label associated with the video `video_id` refers to.

**Uniqueness:**
- `(video_id, property_value_id)`: the same video should not be tagged with the same label twice.
  
**Index:** 
- `property_value_id`: make searches like "search all videos where property_value_id=x" faster (this type of search is needed whenever the user selects labels to filter videos on)
- `video_id`: make searches like "search all labels where video_id=x" faster (this type of search is needed in order to get all the labels of a specific video)

---

### `video_embedding`

**Purpose:** Stores the vector embeddings associated with a video (could be embeddings of specific frames, or embeddings of a description of the video). Each row is a single embedding-to-video association. One video can have multiple embeddings associated with it.

**Columns:**
- `id`: PK
- `video_id`: FK to `video_id`
- `embedding`: vector embedding created by CLIP or another CV model. Same functionality as a vector database (makes storage and searching over high dimensional vectors more efficient), provided by the pgvector extension.

**Index:** HNSW index (an ANN algorithm) with cosine similarity on `embedding` for fast similarity when searching

---

### `video_description`

**Purpose:** Human/AI descriptions of the videos. Can be used for displaying in UI or similarity search. One video can have multiple descriptions.

**Columns:**
- `id`: PK
- `video_id`: FK to `video.id`
- `description`: free-form text  

**Index:**
- `video_id`: make searches like "search all descriptions where video_id=x"

---

### `users`

**Purpose:** Represents different users

**Columns:**
- `id`: PK
- `username`: unique handle/login
- `password`: password hash for security

**Uniqueness:**
- `username`: usernames should be unique

---

### `collection`

**Purpose:** Stores collection entities, which are named sets of videos that users can create. Each row is an ownership record that represents new collection and its owner (creator)

**Columns:**
- `id`: PK
- `collection_name`: display name
- `owner_id`: FK to `users.id`, representing the user who created this collection. Non-owners can be shared a collection, but cannot modify it.

---

### `user_collection`

**Purpose:** Stores the access relationships between collections and users, since users can share collections to other users. Each row represents a user that can access some collection, but do not include the ownership relation since that is already stored in the `collection` table. One collection can be shared to many users, and one user can have access to many collections.

**Columns:**
- `id`: PK
- `user_id`: FK to `users.id`
- `collection_id`: FK to `collection.id`
  
**Uniqueness:**
- `(user_id, collection_id)`: the same user should not be able to access the same collection twice
  
**Index:** 
- `user_id`: make searches like "search all collections where user_id=x" faster (this is needed to display all the collections that a user has access to due to sharing in the UI)

---

### `collection_video` 

**Purpose:** Stores the videos included in a collection. One collection can have many videos, and the same video can be in many different collections.

**Columns:**
- `id`: PK
- `collection_id`: FK to `collection.id`
- `video_id`: FK to `video.id` 
  
**Uniqueness:**
- `(collection_id, video_id)`: the same collection should not have the same video twice
  
**Index:**
- `collection_id`: make searches like "search all videos where collection_id=x" faster (this is needed to display all the videos present in some collection in the UI)

## Local Testing
1. Run `docker-compose up -d` to start a local postgres instance with pgvector using Docker. You can custommize the `docker-compose.yml` configurations under the `db` directory.
2. Connect to the postgres instance using a tool such as DBeaver (DBeaver installation: https://dbeaver.io/download/)
3. Create a `.env` in the project root and add an `ANN_URL` environmental variable which will hold the database connection string. Follow the SQLAlchemy database connection url format: https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls
4. Run `python3 -m db.db_init` from the project root to initialize the tables in the database.
5. You can now start a `Session` in SQLAlchemy, run database operations, and commit them.
6. Run `python3 -m db.db_cleanup` from the project root to delete all tables.