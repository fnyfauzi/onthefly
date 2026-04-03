import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import logger from "$lib/server/logger";
import { apiUrl } from "$lib/constants";

///
export const load: PageServerLoad = async ({ fetch, locals, params }) => {
  if (!locals.user) redirect(303, "/auth/login");

  logger.info("-------------------");
  logger.info("Similarity Libraries: load.");
  const offset = params.offset;
  let url = new URL(`${apiUrl}/user_similarity_libraries/libs`);
  url.search = new URLSearchParams({ offset: offset, limit: "1000" }).toString();
  const libs = await fetch(url, {
    method: "GET",
    signal: AbortSignal.timeout(10000), // 10secs
  }).then((r) => r.json());
  logger.info("Similarity Libraries: load success.");
  // return { libs }; // [[filename, size], [filename, size], ...]
  return { user: locals.user, libs: libs }
};

