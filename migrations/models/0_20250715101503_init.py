from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "category" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "create_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "update_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "blog" (
    "id" UUID NOT NULL PRIMARY KEY,
    "cover_image" TEXT,
    "title" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "favor" INT NOT NULL,
    "create_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "update_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "category_id" UUID NOT NULL REFERENCES "category" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "blogimage" (
    "id" UUID NOT NULL PRIMARY KEY,
    "image_path" TEXT NOT NULL,
    "description" TEXT,
    "upload_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "blog_id" UUID NOT NULL REFERENCES "blog" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "tag" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "create_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "update_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "blog_tag" (
    "blog_id" UUID NOT NULL REFERENCES "blog" ("id") ON DELETE CASCADE,
    "tag_id" UUID NOT NULL REFERENCES "tag" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_blog_tag_blog_id_f24005" ON "blog_tag" ("blog_id", "tag_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
