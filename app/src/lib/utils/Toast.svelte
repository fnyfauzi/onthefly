<script lang="ts">
  // import { toast } from "./states.svelte";
  let { value }: { value: string | null } = $props();
  // const close = () => (toast.value = null);
</script>

<div class="toast toast-top toast-center">
  <!-- <div class="toast toast-middle toast-center"> -->
  {#if value}
    <div
      class="alert alert-horizontal border border-pink-500 text-black text-md py-1.5"
    >
      <span>{value}</span>
      <button
        class="btn btn-md border border-red-500 text-white bg-red-500"
        onclick={() => close()}>Close</button
      >
    </div>
  {/if}
</div>
