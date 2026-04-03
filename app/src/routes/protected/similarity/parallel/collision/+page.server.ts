import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { apiUrl } from "$lib/constants";

export const load: PageServerLoad = async ({ fetch, locals, url }) => {
  if (!locals.user) redirect(303, "/auth/login");

  let subDir = url.searchParams.get('key')!;
  let filename = url.searchParams.get("name")!;
  const offset = url.searchParams.get("offset")!;
  const limit = url.searchParams.get("limit")!;

  let _url: URL;
  if (Number(offset) === 0) {
    _url = new URL(`${apiUrl}/user_similarity_parallel/show-3d`);
  } else {
    _url = new URL(`${apiUrl}/user_similarity_parallel/show-3d-next-prev`);
  }

  _url.search = new URLSearchParams({ sub_dir: subDir, filename, offset, limit }).toString();
  // const files = await fetch(_url, {
  //   method: "GET",
  //   signal: AbortSignal.timeout(10000), // 10secs
  // }).then((r) => r.json());
  const res = await fetch(_url, {
    method: "GET",
    signal: AbortSignal.timeout(10000), // 10secs
  }).then((r) => r.json());

  // const site = res['site']; // 'initial' or 'next-prev'
  const files = res['pdbs'];

  return { subDir, name: filename, files };
}
