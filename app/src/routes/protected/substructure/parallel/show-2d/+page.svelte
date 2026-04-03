<script lang="ts">
  import { baseUrl, nginxUrl } from "$lib/constants.js";
  import { logout } from "../../../../auth/logout/logout.remote.js";

  let { data } = $props();

  let prev: number = $derived(Number(data.offset) - Number(data.limit));
  let next: number = $derived(Number(data.offset) + Number(data.limit));

  let link: string = `${baseUrl}/protected/substructure/parallel/show-2d`;

  let currPage = $derived.by(() => {
    return Math.round(Number(data.offset) / Number(data.limit)) + 1;
  });
  let maxPage = $derived.by(() => {
    return Math.round(Number(data.totalSmile) / Number(data.limit)) + 1;
  });

  let linkPngs = $derived.by(() => {
    return Number(data.offset) === 0
      ? `${nginxUrl}/substructure/parallel/${data.key}/pngs`
      : `${nginxUrl}/substructure/parallel/${data.key}/pngs-next-prev`;
  });
</script>

<div class="flex w-[calc(w-full-16.2rem)] m-4 justify-between">
  <div class="flex items-center space-x-2">
    {#if !data.error}
      <a
        target="_self"
        href={`${link}?key=${data.key}&name=${data.name}&offset=${prev}&limit=${data.limit}`}
        class={`btn btn-sm btn-error hover:btn-primary text-white ${Number(data.offset) === 0 ? "btn-disabled" : ""}`}
        >Prev</a
      >
      <span class="text-sm border border-slate-400 rounded-full p-2"
        >{currPage}/{maxPage}</span
      >
      <a
        target="_self"
        href={`${link}?key=${data.key}&name=${data.name}&offset=${next}&limit=${data.limit}`}
        class={`btn btn-sm btn-error hover:btn-primary text-white ${currPage === maxPage ? "btn-disabled" : ""}`}
        >Next</a
      >
    {/if}
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
      <span class="text-2xl font-semibold"
        >Parallel Substructure - 2D Result</span
      >
      <!-- <img src="/images/logo.jpg" alt="logo" width="60" /> -->
    </label>
  </div>
</div>

{#if data.error}
  <div
    class="flex flex-wrap w-[calc(w-full-16.2rem)] m-4 pt-10 justify-center items-center"
  >
    <div class="text-red-500 text-3xl">{data.detail}</div>
  </div>
{:else}
  <div
    class="flex flex-wrap gap-1 w-[calc(w-full-16.2rem)] m-4 overflow-x-auto rounded-box border border-base-content/5 bg-base-100"
  >
    <!-- PNG -->
    <div class="tooltip tooltip-right">
      <div
        class="tooltip-content border bg-white text-black text-sm flex flex-col items-start"
      >
        {#each Object.entries(data.prop) as [key, value]}
          <p>{key} : {value}</p>
        {/each}
      </div>
      <div class="box">
        <div
          class="flex justify-center text-white bg-[rgba(196,74,137,0.8)] rounded-full"
        >
          Input Smile
        </div>
        <img
          src={`${nginxUrl}/substructure/parallel/${data.key}/${data.png}`}
          alt={data.png}
          width="250"
          class="rounded-full animate-bounce"
        />
        <div class="midname">TEST SMILES</div>
      </div>
    </div>

    <!-- PNGS -->
    {#each data.props as prop, index}
      <div class="tooltip tooltip-right">
        <div
          class="tooltip-content border bg-white text-black text-sm flex flex-col items-start"
        >
          {#each Object.entries(prop) as [key, value]}
            <p>{key} : {value}</p>
          {/each}
        </div>
        <div class="box">
          <div class="flex justify-end">
            ({Number(data.offset) + index + 1})
          </div>
          <img
            src={`${linkPngs}/${data.pngs[index]}`}
            alt={data.pngs[index]}
            width="250"
            class="rounded-full"
          />
          <div class="midname">
            {`(${Number(data.pngs[index].split(".")[0]) + Number(data.offset)}.png)`}
          </div>
        </div>
      </div>
    {/each}
  </div>
{/if}
