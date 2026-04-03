<script lang="ts">
  let { children } = $props();
</script>

<div class="flex ml-2">
  <aside class="overflow-y-auto h-screen min-w-[16.2rem]">
    <div class="flex justify-center items-center mt-4">
      <div class="flex space-x-4 justify-center items-center">
        <img src="/images/logo.jpg" alt="logo" width="60" />
        <div class="flex flex-col">
          <p class="text-md text-slate-500">ArtSMol</p>
          <!-- <p class="text-md text-slate-500">Small Molecule</p> -->
        </div>
      </div>
    </div>
    <ul class="menu menu-sm bg-base-100 rounded-box w-60 space-y-2 mb-20">
      <li class="flex justify-center"></li>
      <li class="mt-2 space-y-4">
        <details open>
          <summary class="text-bold text-sm">Chatbot</summary>
          <ul>
            <li>
              <a href="/protected/chatbot" class="text-sm">Chatbot</a>
            </li>
          </ul>
        </details>
        <details open>
          <summary class="text-bold text-sm">Similarity</summary>
          <ul>
            <li>
              <a href="/protected/similarity/libraries/0" class="text-sm"
                >Libraries</a
              >
            </li>
            <li>
              <a href="/protected/similarity/parallel/0" class="text-sm"
                >Parallel</a
              >
            </li>
          </ul>
        </details>
        <details open>
          <summary class="text-bold text-sm">Substructure</summary>
          <ul>
            <li>
              <a href="/protected/substructure/parallel/0" class="text-sm"
                >Parallel</a
              >
            </li>
          </ul>
        </details>
      </li>
    </ul>
  </aside>

  <main class="overflow-y-auto h-screen w-full">
    {@render children?.()}
  </main>
</div>
