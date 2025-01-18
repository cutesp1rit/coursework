CREATE TABLE IF NOT EXISTS "users" (
  "telegram_user_id" varchar UNIQUE PRIMARY KEY NOT NULL,
  "username" varchar,
  "nickname" varchar,
  "voice_file_path" varchar,
  "vmm_mode" bool
);

CREATE TABLE IF NOT EXISTS "chat_messages" (
  "id" varchar UNIQUE PRIMARY KEY,
  "chat_id" varchar NOT NULL,
  "user_id" varchar NOT NULL,
  "message_text" text,
  "created_at" timestamp
);

CREATE TABLE IF NOT EXISTS "group_chats" (
  "chat_id" varchar UNIQUE PRIMARY KEY NOT NULL,
  "privacy" bool
);

COMMENT ON COLUMN "users"."username" IS 'Имя пользователя Telegram';

COMMENT ON COLUMN "users"."nickname" IS 'Прозвище для озвучки диалогов';

COMMENT ON COLUMN "users"."voice_file_path" IS 'Путь к файлу сгенерированного голоса';

COMMENT ON COLUMN "users"."vmm_mode" IS 'Режим преобразование текста в голосовое сообщение на любое текстовое сообщение';

COMMENT ON COLUMN "chat_messages"."message_text" IS 'Текст сообщения';

COMMENT ON COLUMN "chat_messages"."created_at" IS 'Время отправки сообщения';

COMMENT ON COLUMN "group_chats"."privacy" IS 'Имеет ли бот доступ ко всем сообщениям?';

ALTER TABLE "chat_messages" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("telegram_user_id");

ALTER TABLE "chat_messages" ADD FOREIGN KEY ("chat_id") REFERENCES "group_chats" ("chat_id");