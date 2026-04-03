<script lang="ts">
  // import { toast } from "$lib/utils/states.svelte";
  // import Toast from "$lib/utils/Toast.svelte";
  import { load, login } from "./login.remote";
  load();
  let isLoading = $state(false);
</script>

<div class="flex flex-col h-screen w-full justify-center items-center">
  <div class="bg-[rgba(196,74,137,0.8)] rounded-full w-150 h-160">
    <div class="flex flex-col mt-12 justify-center items-center">
      <img src="/images/logo.jpg" alt="logo" width="28%" class="rounded-full" />
      <div class="mt-4 text-3xl text-white">Artivila Small Molecule</div>
      <div class="mt-1 text-3xl text-white">(ArtSMol)</div>
    </div>

    <div class="bg-white mx-24 my-4 rounded-box">
      <fieldset
        class="fieldset border border-gray-100 rounded-md m-4 px-4 py-1 mx-auto"
      >
        <legend
          class="fieldset-legend mx-auto px-2 text-lg text-[rgba(196,74,137,0.8)]"
          >Login</legend
        >
        <form
          {...login.enhance(async ({ form, data, submit }) => {
            isLoading = true;
            try {
              await submit();
              // await submit().updates(getPosts());
              // await submit().updates(getPosts().withOverride((posts) => [newPost, ...posts]));
              form.reset();
              // showToast('Successfully published!');
            } catch (error) {
              // showToast("Oh no! Something went wrong");
            } finally {
              isLoading = false;
            }
          })}
        >
          <!-- <span hidden> {(toast.value = login.result?.error ? login.result.detail : null)} </span> -->
          <div class="mb-2 w-full justify-center items-center">
            <label for="" class="floating-label flex place-content-center">
              <input
                type="text"
                name="username"
                placeholder="Username"
                class="input input-md input-neutral rounded-box"
                required
              />
            </label>
          </div>
          <div class="mb-2 w-full justify-center items-center">
            <label for="" class="floating-label flex place-content-center">
              <input
                type="password"
                name="password"
                placeholder="Password"
                class="input input-md input-neutral rounded-box"
                required
              />
            </label>
          </div>
          <div class="flex flex-col space-y-2 justify-center items-center">
            <div>
              {#if login.result?.error}
                <p class="error text-red-500 text-sm">
                  {login.result.detail}
                </p>
              {/if}
            </div>
            <div>
              {#if isLoading}
                <button class="btn btn-sm btn-disabled">
                  <span class="loading loading-sm loading-spinner"></span>
                  loading
                </button>
              {:else}
                <button
                  class="btn btn-sm w-[16rem] bg-[rgba(196,74,137,0.8)] text-white text-sm"
                  >Login</button
                >
              {/if}
            </div>
            <a
              href="/auth/register"
              class="link link-hover mx-4 mt-2 mb-4 text-sm">Register</a
            >
          </div>
        </form>
      </fieldset>
    </div>

    <div class="flex place-content-center mt-6 text-white text-sm">
      Copyright: Artivila
    </div>
  </div>
</div>

<!-- {#if toast.value} <Toast value={toast.value} /> {/if} -->
