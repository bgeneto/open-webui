<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { getChatPresets, deleteChatPreset } from '$lib/apis/chats';
  import { user } from '$lib/stores';
  import Modal from '$lib/components/common/Modal.svelte';
  import Pagination from '$lib/components/common/Pagination.svelte';

  const dispatch = createEventDispatcher();

  let presets = [];
  let selectedPreset = null;
  let page = 0;
  let perPage = 10;

  onMount(async () => {
    presets = await getChatPresets(user.id);
  });

  const loadPreset = (preset) => {
    dispatch('load', preset);
  };

  const deletePreset = async (presetId) => {
    await deleteChatPreset(presetId);
    presets = presets.filter((preset) => preset.id !== presetId);
  };

  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      dispatch('close');
    }
  };

  const handleFocusTrap = (event: FocusEvent) => {
    const modal = event.currentTarget as HTMLElement;
    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    if (event.target === firstElement && event.relatedTarget === lastElement) {
      lastElement.focus();
    } else if (event.target === lastElement && event.relatedTarget === firstElement) {
      firstElement.focus();
    }
  };
</script>

<Modal on:close={() => dispatch('close')} on:keydown={handleKeyDown} on:focusout={handleFocusTrap}>
  <div class="p-4">
    <h2 class="text-lg font-medium mb-4">Load Preset</h2>
    <ul>
      {#each presets.slice(page * perPage, (page + 1) * perPage) as preset}
        <li class="flex justify-between items-center mb-2">
          <span>{preset.preset_name}</span>
          <div>
            <button
              class="bg-green-500 text-white px-2 py-1 rounded mr-2"
              on:click={() => loadPreset(preset)}
              aria-label="Load preset {preset.preset_name}"
            >
              Load
            </button>
            <button
              class="bg-red-500 text-white px-2 py-1 rounded"
              on:click={() => deletePreset(preset.id)}
              aria-label="Delete preset {preset.preset_name}"
            >
              Delete
            </button>
          </div>
        </li>
      {/each}
    </ul>
    <Pagination {page} {count}={presets.length} {perPage} />
  </div>
</Modal>
