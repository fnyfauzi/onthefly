import { integer, sqliteTable, text } from 'drizzle-orm/sqlite-core';

export const users = sqliteTable('users', {
	id: integer("id").primaryKey({ autoIncrement: true }).notNull(),
	email: text("email", { length: 64 }).notNull().unique(),
	username: text("username", { length: 64 }).notNull().unique(),
	hashed: text("hashed", { length: 64 }).notNull(),
});

export const sessions = sqliteTable('sessions', {
	id: text("id").primaryKey().unique(), // id=token
  userId: integer("user_id")
    .notNull()
    .references(() => users.id),
  expires: integer("expires", { mode: "timestamp" }).notNull(),
});

export type User = typeof users.$inferSelect;
export type Session = typeof sessions.$inferSelect;

