import { redirect } from "@sveltejs/kit";
import type { Actions, PageServerLoad } from "./$types";
import logger from "$lib/server/logger";
import { apiUrl } from "$lib/constants";

///
export const load: PageServerLoad = async ({ fetch, locals, params }) => {
  if (!locals.user) redirect(303, "/auth/login");

  logger.info("-------------------");
  logger.info("Substructure Parallel: load.");

  // Get libs
  const offset = params.offset;
  let url = new URL(`${apiUrl}/user_similarity_libraries/libs`);
  url.search = new URLSearchParams({ offset: offset, limit: "1000" }).toString();
  let libs = await fetch(url, {
    method: "GET",
    signal: AbortSignal.timeout(10000), // 10secs
  }).then((r) => r.json()); // [[filename, size], [filename, size], ...]

  // Get files in 'parallel' dir
  url = new URL(`${apiUrl}/user_substructure_parallel/files`)
  url.search = new URLSearchParams({ offset: offset, limit: "1000" }).toString();
  let res = await fetch(url, {
    method: "GET",
    signal: AbortSignal.timeout(30000), // 30secs
  }).then((r) => r.json());

  logger.info("Substructure Parallel: load success.");
  return { libs, res };
};

/// Remote Functions cannot receive return error
/// if has +page.server.ts
export const actions = {
  run: async({ request }) => {
    logger.info("-------------------");
    logger.info("Substructure Parallel: run.");
    const obj = Object.fromEntries(await request.formData());
    logger.info(`${obj.subDir}, ${obj.name}, ${obj.lib}, ${obj.cpu}, ${obj.rank}, ${obj.limit}`);

    let url = new URL(`${apiUrl}/user_substructure_parallel/parent`);
    url.search = new URLSearchParams({
      cpu: String(obj.cpu),
      rank: String(obj.rank),
      sub_dir: String(obj.subDir),
      smi_file: String(obj.name),
      smilib: String(obj.lib) }).toString();
    let res = await fetch(url, {
      method: "POST",
      signal: AbortSignal.timeout(10800000), // 3 hour
    }); // .then((r) => r.json());
    logger.info("Substructure Parallel: run success.");

    if (!res.ok) {
      const detail = "Abort, Not Found Substructure."
      logger.info(detail);
      return { error: true, detail: detail };
    }

    if (res.status !== 200) {
      const detail = "Abort, Not Found Substructure."
      logger.info(detail);
      return { error: true, detail: detail };    
    }
  }
} satisfies Actions;

