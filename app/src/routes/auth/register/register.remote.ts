import { form, getRequestEvent, query } from "$app/server";
import { redirect } from "@sveltejs/kit";

import * as v from "valibot";
import { db } from "$lib/server/db";
import * as table from "$lib/server/db/schema";
import * as auth from "$lib/server/auth";
import { eq, or } from "drizzle-orm";
import logger from "$lib/server/logger";
import { hash } from "@node-rs/argon2";

interface UserProp {
  id: number;
  email: string;
  username: string;
  hashed: string;
}

///
export const load = query(async () => {
  const { locals } = getRequestEvent();
  if (locals.user) redirect(303, "/");
  return locals.user;
});

///
export const register = form(
  v.object({ email: v.string(), username: v.string(), password: v.string() }),
  async ({ email, username, password }) => {
    logger.info("-------------------");
    logger.info("Auth: register.");
    logger.info(`Email: ${email}`);
    logger.info(`Username: ${username}`);
    logger.info(`Password: hidden`);

    let res: UserProp[] = await db
      .select()
      .from(table.users)
      .where(
        or(eq(table.users.email, email), eq(table.users.username, username))
      );
    if (res.length) {
      const detail = `Abort, duplicate email or username.`
      logger.info(detail);
      return { error: true, detail: detail };
    }

    const hashed = await hash(password, {
      // recommended minimum parameters
      memoryCost: 19456,
      timeCost: 2,
      outputLen: 32,
      parallelism: 1,
    });

    res = await db
      .insert(table.users)
      .values({ email, username, hashed })
      .returning({
        id: table.users.id,
        email: table.users.email,
        username: table.users.username,
        hashed: table.users.hashed,
      });
    const token = auth.generateToken();
    const session = await auth.insertSession(token, res[0].id);

    const { cookies } = getRequestEvent();

    auth.cookiesSet(cookies, token, session.expires);

    logger.info("Auth: register success.");
    // return { success: true };
    redirect(303, "/");
  }
);
