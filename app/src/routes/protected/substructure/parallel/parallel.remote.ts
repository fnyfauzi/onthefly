import { form, getRequestEvent, query } from "$app/server";
import { apiUrl } from "$lib/constants";
import logger from "$lib/server/logger";
import * as v from "valibot";

///
export const upload = form(async () => {
  return { success: true };
});

/// Remote Functions cannot receive return error
/// if has +page.server.ts
// export const run = form(v.object({
//   subDir: v.string(),
//   name: v.string(),
//   lib: v.string(),
//   cpu: v.string(),
//   rank: v.string(),
//   limit: v.string(),
// }), async ({ subDir, name, lib, cpu, rank, limit }) => {
//   logger.info("-------------------");
//   logger.info("Substructure Parallel: run.");
//   logger.info(`${subDir}, ${name}, ${lib}, ${cpu}, ${rank}, ${limit}`);
//   let url = new URL(`${apiUrl}/user_substructure_parallel/parent`);
//   url.search = new URLSearchParams({ cpu: cpu, rank: rank,
//     sub_dir: subDir, smi_file: name, smilib: lib }).toString();
//   let res = await fetch(url, {
//     method: "POST",
//     signal: AbortSignal.timeout(10800000), // 3 hour
//   }); // .then((r) => r.json());
//   logger.info("Substructure Parallel: run success.");

//   if (!res.ok) {
//     const detail = "Abort, Not Found Substructure."
//     logger.info(detail);
//     return { error: true, detail: detail };
//   }

//   if (res.status !== 200) {
//     const detail = "Abort, Not Found Substructure."
//     logger.info(detail);
//     return { error: true, detail: detail };    
//   }
// });

///
export const remove = form(v.object({ subDir: v.string() }), async ({ subDir }) => {
  logger.info("-------------------");
  logger.info("Substructure Parallel: delete.");
  logger.info(`subDir: ${subDir}`);
  const res = await fetch(`${apiUrl}/user_substructure_parallel/${subDir}`, {
    method: "DELETE",
    signal: AbortSignal.timeout(10000), // 10secs
  }); // .then((r) => r.json());
  logger.info("Substructure Parallel: delete success.");

  if (!res.ok) {
    const detail = "Abort, Server Error."
    logger.info(detail);
    return { error: true, detail: detail };      
  }
});

