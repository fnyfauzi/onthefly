import { form, getRequestEvent } from "$app/server";
import * as auth from "$lib/server/auth";
import { redirect } from "@sveltejs/kit";

export const logout = form(async () => {
  const { cookies, locals } = getRequestEvent();
  if (locals.session) {
    await auth.deleteSessionById(locals.session.id);
  }
  auth.cookiesDelete(cookies);

  redirect(303, "/");
});
