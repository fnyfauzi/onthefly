import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ locals, url }) => {
  if (!locals.user) redirect(303, "/auth/login");

  const offset = url.searchParams.get("offset");
  const subDir = url.searchParams.get("subDir")!;
  const file = url.searchParams.get('file')!;
  return { offset, subDir, file };
}
