import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { apiUrl } from "$lib/constants";
import logger from "$lib/server/logger";

///
export const load: PageServerLoad = async ({ fetch, locals, url }) => {
  if (!locals.user) redirect(303, '/auth/login');

  let subDir = url.searchParams.get('key')!;
  let filename = url.searchParams.get("name")!;
  const offset = url.searchParams.get("offset")!;
  const limit = url.searchParams.get("limit")!;

  let _url = new URL(`${apiUrl}/user_substructure_parallel/show-2d`);
  if (Number(offset) > 0) {
    _url = new URL(`${apiUrl}/user_substructure_parallel/show-2d-next-prev`);
  }
  _url.search = new URLSearchParams({ sub_dir: subDir, filename, offset, limit }).toString();
  const res = await fetch(_url, {
    method: "GET",
    signal: AbortSignal.timeout(10000), // 10secs
  }); // .then((r) => r.json());

  if (!res.ok) {
    const status = res.status;
    const data = await res.json();
    logger.info(`${status}: ${JSON.stringify(data)}`);
    return { error: true, detail: `${JSON.stringify(data)}`};
  }

  const data = await res.json(); 

  const testProps = data['test_props']; // test file
  const png = data['png']; // test file
  const resultProps = data['result_props']; // result files
  const pngs = data['pngs']; // result files
  const totalSmile = data['total_smile']; // pagination
  const site = data['site']; // initial / next-prev

  const prop = testProps[0];
  // const smile = prop['Smiles']

  // let smiles = [];
  // for (let i = 0; i < resultProps.length; i++) {
  //   const currSmile = resultProps[i]['Smiles'];
  //   smiles.push(currSmile);
  // }

  // logger.info(`prop: ${prop}`);
  // logger.info(`png: ${png}`);
  // logger.info(`props: ${resultProps}`);
  // logger.info(`pngs: ${pngs}`);
  // logger.info(`site: ${site}`);
  // logger.info(`total_smile: ${totalSmile}`);

  return { key: subDir, name: filename, offset, limit, prop, png, props: resultProps, pngs, totalSmile, site };
};
