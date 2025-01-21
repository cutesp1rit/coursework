CREATE TABLE IF NOT EXISTS "users" (
  "telegram_user_id" varchar UNIQUE PRIMARY KEY NOT NULL,
  "nickname" varchar,
  "gender" boolean,
  "voice" boolean
);

CREATE TABLE IF NOT EXISTS "chat_messages" (
  "id" varchar UNIQUE PRIMARY KEY,
  "chat_id" varchar NOT NULL,
  "user_id" varchar NOT NULL,
  "username" varchar,
  "message_text" text,
  "created_at" timestamp
);

COMMENT ON COLUMN "users"."nickname" IS 'Прозвище для озвучки диалогов';

COMMENT ON COLUMN "users"."gender" IS 'Гендер пользователя: false - мужской, true - женский';

COMMENT ON COLUMN "users"."voice" IS 'Голос пользователя для генерации: false - по умолчанию, true - его аудио';

COMMENT ON COLUMN "chat_messages"."username" IS 'Имя пользователя Telegram';

COMMENT ON COLUMN "chat_messages"."message_text" IS 'Текст сообщения';

COMMENT ON COLUMN "chat_messages"."created_at" IS 'Время отправки сообщения';

ALTER TABLE IF NOT EXISTS "chat_messages" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("telegram_user_id");