import { form, getRequestEvent, query } from "$app/server";
import { db } from "$lib/server/db";
import logger from "$lib/server/logger";
import { verify } from "@node-rs/argon2";
import { redirect } from "@sveltejs/kit";
import { eq } from "drizzle-orm";
import * as v from "valibot";
import * as auth from '$lib/server/auth';
import * as table from "$lib/server/db/schema";

// const delay = async (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

///
export const load = query(async () => {
  const { locals } = getRequestEvent();
  if (locals.user) redirect(303, "/");
  return locals.user;
});

///
export const login = form(
  v.object({ username: v.string(), password: v.string() }),
  async ({ username, password }) => {
    logger.info("-------------------");
    logger.info("Auth: login:");
    if (!username || !password) {
      logger.info("Require Username/Password.");
      return { error: true, detail: "Require Username/Password." }; // POJOs
    }
    logger.info(`Username: ${username}`);
    const res = await db
      .select()
      .from(table.users)
      .where(eq(table.users.username, username));
    const user = res.at(0);
    if (!user) {
      logger.info("Incorrect username or password.");
      return { error: true, detail: "Incorrect username or password." }; // POJOs
    }

    const isValidPassword = await verify(user.hashed, password, {
      memoryCost: 19456,
      timeCost: 2,
      outputLen: 32,
      parallelism: 1,
    });
    if (!isValidPassword) {
      logger.info("Incorrect password.");
      return { error: true, detail: "Incorrect password." }; // POJOs
    }

    const { cookies } = getRequestEvent();

    const token = auth.generateToken();
    const session = await auth.insertSession(token, user.id);
    auth.cookiesSet(cookies, token, session.expires);

    // await delay(2000); // 2 secs

    logger.info("Auth: login success.");
    redirect(303, "/");
  }
);
