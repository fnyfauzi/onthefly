import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import logger from "$lib/server/logger";
import { apiUrl } from "$lib/constants";

export const load: PageServerLoad = async ({ fetch, locals, params }) => {
  if (!locals.user) redirect(303, "/auth/login");

  logger.info("-------------------");
  logger.info("Similarity Parallel: load.");

  // Get libs
  const offset = params.offset;
  let url = new URL(`${apiUrl}/user_similarity_libraries/libs`);
  url.search = new URLSearchParams({ offset: offset, limit: "1000" }).toString();
  let libs = await fetch(url, {
    method: "GET",
    signal: AbortSignal.timeout(10000), // 10secs
  }).then((r) => r.json()); // [[filename, size], [filename, size], ...]

  // Get files in 'parallel' dir
  url = new URL(`${apiUrl}/user_similarity_parallel/files`)
  url.search = new URLSearchParams({ offset: offset, limit: "1000" }).toString();
  let res = await fetch(url, {
    method: "GET",
    signal: AbortSignal.timeout(30000), // 30secs
  }).then((r) => r.json());

  logger.info("Similarity Parallel: load success.");
  return { libs, res };
};

