import { form, getRequestEvent, query } from "$app/server";
import { apiUrl } from "$lib/constants";
import logger from "$lib/server/logger";
// import { redirect } from "@sveltejs/kit";
import * as v from "valibot";

/// (auto refresh many times), compiler experimental can't async
// export const load = query(async () => {
//   const { fetch, locals, params  } = getRequestEvent();
//   if (!locals.user) redirect(303, "/auth/login");

//   logger.info("-------------------");
//   logger.info("Similarity Libraries: load.");
//   const offset = params.offset;
//   let url = new URL(`${apiUrl}/user_similarity_libraries/libs`);
//   url.search = new URLSearchParams({ offset: offset!, limit: "100" }).toString();
//   const libs = await fetch(url, {
//     method: "GET",
//     signal: AbortSignal.timeout(10000), // 10secs
//   }).then((r) => r.json());
//   logger.info("Similarity Libraries: load success.");
//   return { user: locals.user, libs: libs }
// });

///
export const upload = form(async () => {
  return { success: true };
});

///
export const remove = form(v.object({ name: v.string() }), async ({ name }) => {
  logger.info("-------------------");
  logger.info("Similarity Libraries: delete.");
  logger.info(`name: ${name}`);
  const res = await fetch(`${apiUrl}/user_similarity_libraries/${name}`, {
    method: "DELETE",
    signal: AbortSignal.timeout(10000), // 10secs
  }).then((r) => r.json());
  logger.info("Similarity Libraries: delete success.");
});