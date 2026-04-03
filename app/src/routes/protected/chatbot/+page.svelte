<script lang="ts">
  import { load, submit } from "./chatbot.remote";
  import { logout } from "../../auth/logout/logout.remote";
  const data = load();
  let model: string | null = $state(null);
  const { user, models } = $derived.by(() => {
    if (data.current) {
      return { user: data.current.user, models: data.current.models };
    } else {
      return { user: null, models: null };
    }
  });

  $effect(() => {
    model = models?.length ? models[0] : null;
  });

  let prompt: string | null = $state(null);
  let streaming: boolean = $state(false);
  let response: string | null = $state(null);
  let isLoading = $state(false);

  const onSubmit = (prompt: string | null, model: string | null) => {
    isLoading = true;
    console.log(`model: ${model}, prompt: ${prompt}`);
    isLoading = false;
  };
</script>

<!--  -->
<div class="flex w-[calc(w-full-16.2rem)] m-4 justify-between">
  <div class="flex items-center space-x-2">
    Small Languange Model (CPU-based)
  </div>
  <div class="flex items-center space-x-4 mr-4">
    <a
      target="_blank"
      href="http://10.168.1.12:8009"
      class="btn btn-sm btn-error hover:btn-primary text-white">ArtChat</a
    >
    <form {...logout}>
      <button class="btn btn-sm btn-error hover:btn-primary text-white"
        >Logout</button
      >
    </form>
    <label for="" class="label">
      <span class="text-2xl font-semibold">Chatbot</span>
    </label>
  </div>
</div>

<!--  -->
<div
  class="flex w-[calc(w-full-16.2rem)] m-4 overflow-x-auto justify-start items-center mb-2"
>
  <div class="flex w-1/2 justify-start">
    <span class="label font-semibold text-gray-500 mr-4">Model</span>
    <select bind:value={model} class="select select-sm">
      {#each models as _model}
        <option value={_model}>
          {_model}
        </option>
      {/each}
    </select>
  </div>
</div>

<!--  -->
<div
  class="flex w-[calc(w-full-16.2rem)] m-4 overflow-x-auto rounded-box border border-base-content/5 bg-base-100"
>
  <!-- <div class="flex w-full gap-4 mr-4">
    <div class="w-1/3">
      <div class="ml-4 mt-2 text-sm">Your Question</div>
      <textarea
        class="textarea textarea-md m-2 grow w-full"
        placeholder="Type here..."
      ></textarea>
    </div>
    <div class="w-2/3">
      <div class="ml-4 mt-2 text-sm">Hi, I am {model}</div>
      <textarea class="textarea textarea-md m-2 grow w-full"></textarea>
    </div>
  </div> -->

  <form
    {...submit.enhance(async ({ form, data, submit }) => {
      isLoading = true;
      try {
        await submit();
        form.reset();
      } catch (error) {
        isLoading = false;
      } finally {
        isLoading = false;
      }
    })}
    class="flex w-full gap-4 mr-4"
  >
    <fieldset class="fieldset w-1/3">
      <legend class="fieldset-legend ml-4 mt-2">Your Question:</legend>
      <input
        {...submit.fields.model.as("text")}
        type="hidden"
        name="model"
        hidden
        value={model}
      />
      <textarea
        {...submit.fields.prompt.as("text")}
        class="textarea textarea-md ml-2 mb-2 grow w-full min-h-40 field-sizing-content overflow-hidden"
        placeholder="Type here..."
        name="prompt"
        bind:value={prompt}
        onkeydown={async (e: KeyboardEvent) => {
          if (e.key !== "Enter") return;
          if (!prompt) return;
          e.preventDefault();
          await onSubmit(prompt, model);
        }}
      ></textarea>
    </fieldset>
    <div class="flex items-start mt-8.5">
      {#if isLoading}
        <button class="btn btn-sm btn-disabled">
          <span class="loading loading-sm loading-spinner"></span>
          loading
        </button>
      {:else}
        <button
          class="btn btn-sm btn-error hover:btn-primary text-white h-16 rounded-md"
          >Submit</button
        >
      {/if}
    </div>
    <fieldset class="fieldset w-2/3">
      <legend class="fieldset-legend ml-2 mt-2">Hi, I am {model}</legend>
      <textarea
        class="textarea textarea-md mb-2 grow w-full min-h-40 field-sizing-content overflow-hidden"
        name="response"
      >
        {response}
      </textarea>
    </fieldset>
  </form>
</div>
