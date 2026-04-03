<script lang="ts">
  import "./layout.css";
  // import favicon from '$lib/assets/favicon.svg';
  import favicon from "$lib/assets/favicon.png";

  let { children } = $props();
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
  <title>Artivila Small Molecule</title>
</svelte:head>

{@render children()}
