<script lang="ts">
  import { enhance } from "$app/forms";
  import { apiUrl, baseUrl, nginxUrl } from "$lib/constants.js";
  import type { SubmitFunction } from "@sveltejs/kit";
  import { logout } from "../../../../auth/logout/logout.remote.js";
  import { remove, upload } from "../parallel.remote.js";

  let { data, form } = $props();

  let lib: string | null | undefined = $state(null);
  $effect(() => (lib = data.libs[0][0]));

  let check: string | null = $state(null);
  // let getCheck = $derived(() => check);
  let limit: number = $state(16);

  const cpus: number[] = [25, 50, 75, 100];
  let cpu: number = $state(100);
  const ranks: number[] = [50, 100, 1000, 5000, 10000];
  let rank: number = $state(50);

  let inputFiles: File[] = $state([]);
  const handleFiles = function (event: Event | DragEvent) {
    event.preventDefault();
    inputFiles = [];
    const target = event.target as HTMLInputElement;
    let eventFiles: FileList | null | undefined = null;
    if (event instanceof DragEvent) {
      eventFiles = event.dataTransfer?.files;
    } else {
      eventFiles = target.files;
    }
    if (!eventFiles) return;
    // console.log(`eventFiles: ${eventFiles.length} ${eventFiles[0].name}`);
    for (let i = 0; i < eventFiles.length; i++) {
      inputFiles.push(eventFiles[i]);
    }
  };

  let isLoading = $state(false);
  let isRunning = $state(false);

  // We still use legacy form actions, because remote functions not ready for production.
  // and return { error } from remote functions not working if we have +page.server.ts
  const run: SubmitFunction = () => {
    isRunning = true;
    return async ({ result, update }) => {
      isRunning = false;
      await update();
    };
  };

  // Toast display png (because tooltip and collapse is not good (cant overlay other layer))
  // Check Toast Div in the bottom-page.
  let isShowToast: boolean = $state(false);
  let pngToast: string | null = $state(null);
</script>

<!-- Upload -->
<div class="flex w-[calc(w-full-16.2rem)] m-4 justify-between">
  <div class="flex items-center space-x-2">
    <form
      {...upload.enhance(async ({ form, data, submit }) => {
        isLoading = true;
        try {
          await submit();
          const formData = new FormData();
          for (const file in inputFiles) {
            formData.append("files", inputFiles[file]);
          }
          const url = `${apiUrl}/user_substructure_parallel/upload`;
          const res = await fetch(url, {
            method: "POST",
            body: formData,
            signal: AbortSignal.timeout(10800000), // 3 hour
          });
          if (!res.ok) {
            isLoading = false;
            throw new Error("Error Upload");
          }
          form.reset();
        } catch (error) {
          isLoading = false;
        } finally {
          isLoading = false;
        }
      })}
      enctype="multipart/form-data"
    >
      <!-- <form method="POST" action="?/upload" enctype="multipart/form-data" use:enhance={upload}> -->
      <div class="join gap-x-2">
        <span class="flex items-center">💊</span>
        <label for="" class="label text-slate-800">SMI</label>
        <input
          multiple
          type="file"
          accept=".smi"
          class="file-input file-input-sm input-error rounded-box"
          onchange={handleFiles}
          required
        />
        {#if isLoading}
          <button class="btn btn-sm btn-disabled">
            <span class="loading loading-spinner loading-sm"></span>
            Uploading (wait)...
          </button>
        {:else}
          <button class="btn btn-sm btn-error hover:btn-primary text-white"
            >Upload</button
          >
        {/if}
      </div>
    </form>
  </div>
  <div class="flex items-center space-x-4 mr-4">
    <!-- <button
      class="btn btn-sm btn-error hover:btn-primary text-white"
      onclick={() => {
        window.location.reload();
      }}
    >Refresh</button> -->
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
      <span class="text-2xl font-semibold">Parallel Substructure</span>
      <!-- <img src="/images/logo.jpg" alt="logo" width="60" /> -->
    </label>
  </div>
</div>

<!-- {#if query.error}
  <p>oops!</p>
{:else if query.loading}
  <p>loading...</p>
{:else} -->
<div
  class="flex w-[calc(w-full-16.2rem)] m-4 overflow-x-auto justify-end items-center mb-2"
>
  <!-- CPU -->
  <div class="flex w-50">
    <span class="label font-semibold text-gray-500 ml-4 mr-4">CPU</span>
    <!-- <select bind:value={cpu} class="select select-xs w-1/3 ml-2"> -->
    <select bind:value={cpu} class="select select-sm">
      {#each cpus as _cpu}
        <option value={_cpu}>
          {_cpu}
        </option>
      {/each}
    </select>
  </div>

  <!-- RANK -->
  <div class="flex w-50">
    <span class="label font-semibold text-gray-500 ml-4 mr-4">Rank</span>
    <!-- <select bind:value={rank} class="select select-xs w-1/3 ml-2"> -->
    <select bind:value={rank} class="select select-sm">
      {#each ranks as _rank}
        <option value={_rank}>
          {_rank}
        </option>
      {/each}
    </select>
  </div>

  <!-- DATABASE / LIBRARIES -->
  <div class="flex w-1/2 justify-start">
    <span class="label font-semibold text-gray-500 ml-4 mr-4">Libraries</span>
    <!-- <select bind:value={database} class="select select-xs w-1/3 ml-2"> -->
    <select bind:value={lib} class="select select-sm">
      <!-- {#each (await query).libs as lib} -->
      <!-- {#each query.current?.libs as lib} -->
      {#each data.libs as [_lib, _size]}
        <option value={_lib}>
          {_lib}
        </option>
      {/each}
    </select>
  </div>
</div>

<!-- <ul>
    {#each Object.entries((await query).res) as [key1, value1], index1}
      {#each Object.entries(value1 as object) as [key2, value2], index2}
        <li>{key2}: {value2}</li>
      {/each}
    {/each}
  </ul> -->

{#if form?.error}
  <p class="ml-4 error text-red-500 text-sm">
    {form.detail}
  </p>
{/if}

<!-- TABLE -->
<div
  class="flex w-[calc(w-full-16.2rem)] m-4 overflow-x-auto rounded-box border border-base-content/5 bg-base-100"
>
  <table class="table table-sm">
    <thead>
      <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Select</th>
        <th>Run</th>
        <th>Show 2D</th>
        <th>Show 3D</th>
        <th>CSV Result</th>
        <th>Remove</th>
      </tr>
    </thead>
    <tbody>
      <!--
          d[sub_dir] = [csv_file, pdb_file, png_file, smi_file, lib_name, [png1, png2, ...], [pdb1, pdb2,...]]
        -->
      <!-- {#each Object.entries((await query).res) as [key, value], index} -->
      {#each Object.entries(data.res) as [key, value], index}
        {@const val = value as any}
        <tr class="hover:bg-base-300">
          <td class="text-sm">{index + 1}</td>
          <td class="text-sm"
            ><button
              class="text-sm border-b"
              onclick={() => {
                pngToast = `${nginxUrl}/substructure/parallel/${key}/${val[2]}`;
                isShowToast = true;
              }}>{val[3]}</button
            ></td
          >
          <td>
            <input
              type="radio"
              name="check"
              bind:group={check}
              value={[val[3], lib]}
              class="checkbox checkbox-sm"
            />
          </td>
          <td>
            <!-- <form
              {...run.for(`run-${index}`).enhance(async ({ form, submit }) => {
                isRunning = true;
                try {
                  await submit();
                  form.reset();
                } catch (error) {
                  isRunning = false;
                } finally {
                  isRunning = false;
                }
              })}
            > -->
            <form method="POST" action="?/run" use:enhance={run}>
              {#if isRunning}
                {#if check![0] === val[3]}
                  <button class="btn btn-sm btn-disabled">
                    <span class="loading loading-spinner loading-sm"></span>
                    Running...
                  </button>
                {:else}
                  <button
                    class="btn btn-sm btn-error hover:btn-primary text-white btn-disabled"
                    >Run</button
                  >
                {/if}
              {:else}
                <!-- <input {...run.fields.subDir.as("text")} type="hidden" name="subDir" hidden value={key} /> -->
                <input type="hidden" name="subDir" hidden value={key} />
                <!-- <input {...run.fields.name.as("text")} type="hidden" name="name" hidden value={val[3]} /> -->
                <input type="hidden" name="name" hidden value={val[3]} />
                <!-- <input {...run.fields.lib.as("text")} type="hidden" name="lib" hidden value={lib} /> -->
                <input type="hidden" name="lib" hidden value={lib} />
                <!-- <input {...run.fields.cpu.as("text")} type="hidden" name="cpu" hidden value={cpu} /> -->
                <input type="hidden" name="cpu" hidden value={cpu} />
                <!-- <input {...run.fields.rank.as("text")} type="hidden" name="rank" hidden value={rank} /> -->
                <input type="hidden" name="rank" hidden value={rank} />
                <!-- <input {...run.fields.limit.as("text")} type="hidden" name="limit" hidden value={limit} /> -->
                <input type="hidden" name="limit" hidden value={limit} />
                <button
                  class="btn btn-sm btn-error hover:btn-primary text-white"
                  >Run</button
                >
              {/if}
            </form>
          </td>
          <td>
            <a
              target="_blank"
              href={`${baseUrl}/protected/substructure/parallel/show-2d?key=${key}&name=${val[3]}&offset=0&limit=${limit}`}
              class="btn btn-sm btn-error hover:btn-primary text-white">Show</a
            >
          </td>
          <td>
            <a
              target="_blank"
              href={`${baseUrl}/protected/substructure/parallel/show-3d?key=${key}&name=${val[3]}&offset=0&limit=${limit}`}
              class="btn btn-sm btn-error hover:btn-primary text-white">Show</a
            >
          </td>
          <td>
            <a
              download={`${val[0]}`}
              target="_blank"
              href={`${nginxUrl}/substructure/parallel/${key}/${val[0]}`}
              class="button btn btn-sm btn-error hover:btn-primary text-white"
              >Download</a
            >
          </td>
          <td>
            <form
              {...remove.for(`remove-${index}`).enhance(async ({ submit }) => {
                await submit();
              })}
            >
              <input
                {...remove.fields.subDir.as("text")}
                type="hidden"
                name="subDir"
                hidden
                value={key}
              />
              <button class="btn btn-sm btn-error hover:btn-primary text-white"
                >Remove</button
              >
            </form>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
<!-- {/if} -->

<!-- Local toast -->
{#if isShowToast}
  <!-- <div class="toast toast-start toast-middle"> -->
  <div class="toast toast-center toast-middle">
    <div
      class="alert alert-horizontal border border-pink-500 text-black text-md py-1.5"
    >
      <img src={pngToast} alt="png" class="rounded-full animate-bounce" />
      <button
        class="btn btn-sm border text-white bg-error"
        onclick={() => {
          pngToast = null;
          isShowToast = !isShowToast;
        }}>Close</button
      >
    </div>
  </div>
{/if}
