import { browser } from "$app/environment";
import { apiUrl } from "$lib/constants";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch, url }) => {
  let subDir = url.searchParams.get('key')!;
  let filename = url.searchParams.get("name")!;
  const offset = url.searchParams.get("offset")!;
  const limit = url.searchParams.get("limit")!;

  if (browser) {
    let _url: URL;
    if (Number(offset) === 0) {
      _url = new URL(`${apiUrl}/user_substructure_parallel/show-3d`);
    } else {
      _url = new URL(`${apiUrl}/user_substructure_parallel/show-3d-next-prev`);
    }

    // const controller = new AbortController();
    // const timer = setTimeout(() => controller.abort(), 300000); // 300secs = 5min

    _url.search = new URLSearchParams({ sub_dir: subDir, filename, offset, limit }).toString();
    const res = await fetch(_url, {
      method: "GET",
      signal: AbortSignal.timeout(300000), // 300secs = 5min
      // signal: controller.signal
    }).then((r) => r.json());
    // clearTimeout(timer);

    const files = res['pdbs']; // result files
    const totalSmile = res['total_smile']; // pagination
    const site = res['site']; // initial / next-prev
    return { key: subDir, name: filename, offset, limit, files, totalSmile, site };
  }
}
