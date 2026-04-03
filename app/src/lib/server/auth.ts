import { eq } from 'drizzle-orm';
import { sha256 } from '@oslojs/crypto/sha2';
import { encodeBase64url, encodeHexLowerCase } from '@oslojs/encoding';
import { db } from '$lib/server/db';
import * as table from '$lib/server/db/schema';
import type { Cookies } from '@sveltejs/kit';
import { cookiesAuth } from '$lib/constants';

const DAY_IN_MS = 1000 * 60 * 60 * 24; // 1 day

// TOKEN ------------------------------------
export function generateToken() {
  const bytes = crypto.getRandomValues(new Uint8Array(18));
  const token = encodeBase64url(bytes);
  return token;
}

export function cookiesSet(cookies: Cookies, token: string, expires: Date) {
  cookies.set(cookiesAuth, token, {
    expires: expires,
    path: "/",
    httpOnly: true,
    sameSite: "strict",
    secure: false, // adapter-node
    // maxAge: 60 * 60 * 24 * 7, // 1 week
    // maxAge: 60 * 60 * 24 * 30, // 1 month
  });
}

export function cookiesDelete(cookies: Cookies) {
  cookies.delete(cookiesAuth, {
    // expires: expires,  // expires: Date
    path: "/",
    httpOnly: true,
    sameSite: "strict",
    secure: false, // adapter-node
  });
}


// CREATE SESSION ------------------------
export async function insertSession(token: string, userId: number) {
  // id = token
  const id = encodeHexLowerCase(sha256(new TextEncoder().encode(token)));
  const session: table.Session = {
    id, userId, expires: new Date(Date.now() + DAY_IN_MS * 30)
  };
  await db.insert(table.sessions).values(session);
  return session;
}

// ----------------------------------
// Session validation and renew session.
export async function checkSession(token: string) {
  const id = encodeHexLowerCase(sha256(new TextEncoder().encode(token))); // id = token
  const [res] = await db.select({
    user: { id: table.users.id, username: table.users.username },
    session: table.sessions
  })
  .from(table.sessions)
  .innerJoin(table.users, eq(table.sessions.userId, table.users.id))
  .where(eq(table.sessions.id, id));

  if (!res) {
    return { user: null, session: null };
  }
  const { user, session } = res;

  const expires = Date.now() > session.expires.getTime();
  if (expires) {
    await db.delete(table.sessions).where(eq(table.sessions.id, session.id));
    return { user: null, session: null };
  }

  const renewSession = Date.now() >= session.expires.getTime() - DAY_IN_MS * 15;
  if (renewSession) {
    session.expires = new Date(Date.now() + DAY_IN_MS * 30); // 1 month
    await db.update(table.sessions)
          .set({ expires: session.expires })
          .where(eq(table.sessions.id, session.id));
  }

  return { user, session };
}

// ----------------------------------
export type CheckSession = Awaited<ReturnType<typeof checkSession>>;

// ----------------------------------
export async function deleteSessionById(sessionId: string) {
  await db.delete(table.sessions).where(eq(table.sessions.id, sessionId));
}
