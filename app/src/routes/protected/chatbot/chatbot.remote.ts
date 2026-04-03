import { form, getRequestEvent, query } from "$app/server"
import logger from "$lib/server/logger";
import { redirect } from "@sveltejs/kit";
import * as v from "valibot";

import * as childProcess from "node:child_process";
import * as util from "node:util";

///
export const load = query(async () => {
  const { locals } = getRequestEvent();
  if (!locals.user) redirect(303, "/auth/login");

  const models: string[] = ['gemma3:270m', 'deepseek-r1:1.5b'];
  return { user: locals.user, models: models }
});

///
export const submit = form(
  v.object({ prompt: v.string() || v.null(),  model: v.string() || v.null() }),
  async({ prompt, model }) => {
  logger.info("-------------------");
  logger.info("Chatbot: submit.");
  if (!prompt || !model) {
    const detail = "Abort, Empty prompt or model."
    logger.info(detail);
    return { error: true, detail: detail }; // POJOs
  }
  // logger.info(`model: ${model}\nprompt: ${prompt}`);
  // console.log(`model: ${model}\nprompt: ${prompt}`);
  
  // const exec = util.promisify(childProcess.exec);
  // const cmd = `curl -X POST http://10.168.1.14:11434/api/generate -d "{ \"model\": \"gemma3:270m\", \"prompt\": \"Who am i?\", \"stream\": true, \"options\": {\"num_thread\": 8, \"num_ctx\": 2024 }}"`;
  // const { stdout, stderr } = await exec(cmd);
  // logger.info(stdout);

  logger.info("Chatbot: submit success.");
});
