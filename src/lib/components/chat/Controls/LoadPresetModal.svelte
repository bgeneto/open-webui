<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import Modal from '$lib/components/common/Modal.svelte';

  export let showModal = false;
  export let presets = [];
  export let searchQuery = '';
  export let applyPreset;

  const dispatch = createEventDispatcher();

  const filteredPresets = () => {
    return presets.filter((preset) =>
      preset.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  };

  const closeModal = () => {
    showModal = false;
    dispatch('close');
  };
</script>

<Modal bind:show={showModal} on:close={closeModal}>
  <div class="p-4">
    <input
      type="text"
      placeholder="Search presets"
      class="w-full mb-4 p-2 border rounded"
      bind:value={searchQuery}
    />
    <ul>
      {#each filteredPresets() as preset}
        <li class="mb-2">
          <button
            class="w-full text-left p-2 border rounded hover:bg-gray-100 dark:hover:bg-gray-700"
            on:click={() => applyPreset(preset)}
          >
            {preset.name}
          </button>
        </li>
      {/each}
    </ul>
  </div>
</Modal>
