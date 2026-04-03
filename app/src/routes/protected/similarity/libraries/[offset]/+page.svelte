<script lang="ts">
  import { apiUrl, nginxUrl } from "$lib/constants";
  import { logout } from "../../../../auth/logout/logout.remote";
  import { remove, upload } from "../libraries.remote";

  let { data } = $props();

  // const data = load();
  // const { user, libs } = $derived.by(() => {
  //   if (data.current) {
  //     return { user: data.current.user, libs: data.current.libs };
  //   } else {
  //     return { user: null, libs: [] };
  //   }
  // });

  let inputFile: File | null = $state(null);
  const handleFiles = function (event: Event | DragEvent) {
    event.preventDefault();
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length) {
      inputFile = target.files[0];
    } else {
      inputFile = null;
    }
  };

  let isLoading = $state(false);
  let worker: Worker;
  $effect(() => {
    (async () => {
      const W = await import("../worker.svelte?worker");
      worker = new W.default();
      worker.onmessage = (e: MessageEvent) => {
        const { error } = e.data;
        isLoading = false;
        if (error) {
          console.log(`worker error: ${error}`);
        }
      };
    })();
  });
</script>

<!-- Upload -->
<div class="flex w-[calc(w-full-16.2rem)] m-4 justify-between">
  <div class="flex items-center space-x-2">
    <form
      {...upload.for("upload").enhance(async ({ form, data, submit }) => {
        // isLoading = true;
        try {
          await submit();
          // await submit().updates(load(params.offset)); // not refreshed
          if (inputFile && worker) {
            // if (inputFiles.length > 0 && worker) {
            isLoading = true;
            worker.postMessage({
              files: [inputFile],
              // files: inputFiles,
              url: `${apiUrl}/user_similarity_libraries/chunk`,
            });
          }
          //
          // let urls: string[] = [];
          // for (const i in inputFiles) {
          //   const file: File = inputFiles[i];
          //   const chunkSize = 50 * 1024 * 1024; // 50MB
          //   // const chunkSize = 10 * 1024; // 10KB
          //   const totalChunk = Math.ceil(file.size / chunkSize);
          //   // let ret: string[] = [];
          //   for (let start = 0; start < file.size; start += chunkSize) {
          //     const chunk: Blob = file.slice(start, start + chunkSize);
          //     const formData = new FormData();
          //     formData.append("files", chunk);

          //     const indexChunk = Math.floor(start / chunkSize);
          //     const params: Record<string, any> = {
          //       filename: file.name,
          //       isInitial: start == 0 ? true : false,
          //       totalChunk: totalChunk,
          //       indexChunk: indexChunk,
          //     };
          //     const url = new URL(`${apiUrl}/user_similarity_libraries/chunk`);
          //     url.search = new URLSearchParams(params).toString();
          //     const res = await fetch(url, {
          //       method: "POST",
          //       body: formData,
          //       signal: AbortSignal.timeout(10800000), // 3 hour
          //     });
          //     if (!res.ok) {
          //       isLoading = false;
          //       throw new Error("Error Upload");
          //     }
          //     // ret = await res.json();
          //     // if (indexChunk === totalChunk - 1) {
          //     //   urls.push(ret[0]);
          //     // }
          //   }
          // }
          //
          // form.append("urls", urls.join(","));
          form.reset();
        } catch (error) {
          isLoading = false;
        } finally {
          // isLoading = false;
        }
      })}
      enctype="multipart/form-data"
    >
      <!-- <form method="POST" action="?/upload" enctype="multipart/form-data" use:enhance={upload}> -->
      <div class="join gap-x-2">
        <span class="flex items-center">💊</span>
        <label for="" class="label text-slate-800">SMI</label>
        <input
          type="file"
          accept=".smi"
          class="file-input file-input-sm input-error rounded-box"
          onchange={handleFiles}
          required
        />
        <!-- <input
          multiple
          accept=".smi"
          type="file"
          class="file-input file-input-sm input-error rounded-box"
          onchange={handleFiles}
          required
        /> -->
        {#if isLoading}
          <button class="btn btn-sm btn-disabled">
            <span class="loading loading-spinner loading-sm"></span>
            Uploading (Don't close this page)...
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
      <span class="text-2xl font-semibold">Libraries Similarity</span>
      <!-- <img src="/images/logo.jpg" alt="logo" width="60" /> -->
    </label>
  </div>
</div>

<!-- Table -->
<div
  class="flex w-[calc(w-full-16.2rem)] m-4 overflow-x-auto rounded-box border border-base-content/5 bg-base-100"
>
  <table class="table table-sm">
    <thead>
      <tr>
        <th>ID</th>
        <th>Libraries</th>
        <th>Size (bytes)</th>
        <th>Download</th>
        <th>Remove</th>
      </tr>
    </thead>
    <tbody>
      <!-- 
      {#each await load(params.offset) as lib, index}
        <tr class="hover:bg-base-300">
          <td class="text-sm">{index + 1}</td>
          <td class="text-sm">{lib}</td>
          <td>
            <form
              {...remove.enhance(async ({ form, data, submit }) => {
                isLoading = true;
                try {
                  await submit();
                  form.reset();
                } catch (error) {
                } finally {
                  isLoading = false;
                }
              })}
            >
              <input type="hidden" name="name" hidden value={lib} />
              <button class="btn btn-sm btn-error hover:btn-primary text-white"
                >Remove</button
              >
            </form>
          </td>
        </tr>
      {/each}
       -->
      <!-- {#if data.libs.error}
        <tr class="hover:bg-base-300"><td>oops!</td></tr>
      {:else if data.libs.loading}
        <tr class="hover:bg-base-300"><td>loading...</td></tr>
      {:else} -->
      {#each data.libs as [lib, size], index}
        <tr class="hover:bg-base-300">
          <td class="text-sm">{index + 1}</td>
          <td class="text-sm">{lib}</td>
          <td class="text-sm">{size}</td>
          <td class="text-sm">
            <a
              download={`${lib}`}
              target="_blank"
              href={`${nginxUrl}/similarity/libraries/${lib}`}
              class="button btn btn-sm btn-error hover:btn-primary text-white"
              >Download</a
            >
          </td>
          <td>
            <form
              {...remove.for(index).enhance(async ({ submit }) => {
                await submit();
              })}
            >
              <input
                {...remove.fields.name.as("text")}
                type="hidden"
                name="name"
                hidden
                value={lib}
              />
              <button class="btn btn-sm btn-error hover:btn-primary text-white"
                >Remove</button
              >
            </form>
          </td>
        </tr>
      {/each}
      <!-- {/if} -->
    </tbody>
  </table>
</div>
