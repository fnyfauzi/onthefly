import type { Handle } from '@sveltejs/kit';
import * as auth from '$lib/server/auth';
import { dev } from '$app/environment';
import { cookiesAuth } from '$lib/constants';
import { sequence } from '@sveltejs/kit/hooks';

//
export const suppressHandle: Handle = async ({ event, resolve }) => {
  if (
    dev &&
    event.url.pathname === "/.well-known/appspecific/com.chrome.devtools.json"
  ) {
    return new Response(undefined, { status: 404 });
  }
  return await resolve(event);
};

//
const authHandle: Handle = async ({ event, resolve }) => {
	const token = event.cookies.get(cookiesAuth);
  if (!token) {
    event.locals.user = null;
    event.locals.session = null;
    return await resolve(event);
  }

  const { user, session } = await auth.checkSession(token);
  if (session) {
    auth.cookiesSet(event.cookies, token, session.expires);
  } else {
    auth.cookiesDelete(event.cookies);
  }

  event.locals.user = user;
  event.locals.session = session;
  return await resolve(event);
};

export const handle: Handle = sequence(suppressHandle, authHandle);

//
process.on("SIGINT", () => {
  console.log("Received SIGINT. Initiating graceful shutdown...");
  process.exit(0);
});
