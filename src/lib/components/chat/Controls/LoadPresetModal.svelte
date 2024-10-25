<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import Modal from '$lib/components/common/Modal.svelte';

  export let showModal = false;
  export let presets = [];
  export let searchQuery = '';
  export let applyPreset;
  export let deletePreset;

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

  const handleDelete = (preset) => {
    if (confirm(`Are you sure you want to delete the preset "${preset.name}"?`)) {
      deletePreset(preset);
    }
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
        <li class="mb-2 flex justify-between items-center">
          <button
            class="w-full text-left p-2 border rounded hover:bg-gray-100 dark:hover:bg-gray-700"
            on:click={() => applyPreset(preset)}
          >
            {preset.name}
          </button>
          <button
            class="ml-2 text-red-500 hover:text-red-700"
            on:click={() => handleDelete(preset)}
          >
            Delete
          </button>
        </li>
      {/each}
    </ul>
  </div>
</Modal>
