import { form, getRequestEvent, query } from "$app/server";
import { apiUrl } from "$lib/constants";
import logger from "$lib/server/logger";
import { redirect } from "@sveltejs/kit";
import * as v from "valibot";

/// parallel/[offset]
///
export const upload = form(async () => {
  return { success: true };
});

///
export const run = form(v.object({
  subDir: v.string(),
  name: v.string(),
  lib: v.string(),
  cpu: v.string(),
  rank: v.string(),
  limit: v.string(),
}), async ({ subDir, name, lib, cpu, rank, limit }) => {
  logger.info("-------------------");
  logger.info("Similarity Parallel: run.");
  logger.info(`${subDir}, ${name}, ${lib}, ${cpu}, ${rank}, ${limit}`);
  let url = new URL(`${apiUrl}/user_similarity_parallel/parent`);
  url.search = new URLSearchParams({ cpu: cpu, rank: rank,
    sub_dir: subDir, smi_file: name, smilib: lib }).toString();
  let res = await fetch(url, {
    method: "POST",
    signal: AbortSignal.timeout(10800000), // 3 hour
  }).then((r) => r.json());
  logger.info("Similarity Parallel: run success.");
});

///
export const remove = form(v.object({ subDir: v.string() }), async ({ subDir }) => {
  logger.info("-------------------");
  logger.info("Similarity Parallel: delete.");
  logger.info(`subDir: ${subDir}`);
  const res = await fetch(`${apiUrl}/user_similarity_parallel/${subDir}`, {
    method: "DELETE",
    signal: AbortSignal.timeout(10000), // 10secs
  }).then((r) => r.json());
  logger.info("Similarity Parallel: delete success.");
});


/// parallel/show-3d
// export const loadShow3D = query(async () => {
//   const { fetch, locals, params, url } = getRequestEvent();
//   if (!locals.user) redirect(303, "/auth/login");

//   logger.info("-------------------");
//   logger.info("Similarity Show-3D: load.");

//   let subDir = url.searchParams.get('key')!;
//   let filename = url.searchParams.get("name")!;
//   const offset = url.searchParams.get("offset")!;
//   const limit = url.searchParams.get("limit")!;

//   let _url = new URL(`${apiUrl}/user_similarity_parallel/show-3d`);
//   if (Number(offset) > 0) {
//     _url = new URL(`${apiUrl}/user_similarity_parallel/show-3d-next-prev`);
//   }

//   // const controller = new AbortController();
//   // const timer = setTimeout(() => controller.abort(), 300000); // 300secs = 5min

//   _url.search = new URLSearchParams({ sub_dir: subDir, filename, offset, limit }).toString();
//   const res = await fetch(_url, {
//     method: "GET",
//     signal: AbortSignal.timeout(300000), // 300secs = 5min
//     // signal: controller.signal
//   }).then((r) => r.json());
//   // clearTimeout(timer);

//   const files = res['pdbs']; // result files
//   const totalSmile = res['total_smile']; // pagination
//   const site = res['site']; // initial / next-prev

//   return { key: subDir, name: filename, offset, limit, files, totalSmile, site }; 
// });

