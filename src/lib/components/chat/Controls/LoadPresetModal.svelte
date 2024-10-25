<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { onMount } from 'svelte';
  import { getPresets } from '$lib/apis/presets';
  import { user } from '$lib/stores';
  import Pagination from '$lib/components/common/Pagination.svelte';
  import XMark from '$lib/components/icons/XMark.svelte';
  import MagnifyingGlass from '$lib/components/icons/MagnifyingGlass.svelte';
  import Trash from '$lib/components/icons/Trash.svelte';
  import Check from '$lib/components/icons/Check.svelte';

  const dispatch = createEventDispatcher();

  let presets = [];
  let searchQuery = '';
  let filteredPresets = [];
  let page = 0;
  let perPage = 10;

  const loadPresets = async () => {
    try {
      presets = await getPresets(user.token);
      filteredPresets = presets;
    } catch (error) {
      console.error('Failed to load presets', error);
    }
  };

  const filterPresets = () => {
    filteredPresets = presets.filter((preset) =>
      preset.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  };

  const handleLoadPreset = (preset) => {
    dispatch('load', preset);
    dispatch('close');
  };

  const handleDeletePreset = (presetName) => {
    dispatch('delete', presetName);
  };

  onMount(loadPresets);
</script>

<div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
  <div class="bg-white dark:bg-gray-850 rounded-lg shadow-lg w-11/12 md:w-1/2 lg:w-1/3">
    <div class="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
      <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">Load Preset</h2>
      <button
        class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
        on:click={() => dispatch('close')}
      >
        <XMark className="size-5" />
      </button>
    </div>
    <div class="p-4">
      <div class="relative mb-4">
        <input
          type="text"
          placeholder="Search presets"
          bind:value={searchQuery}
          on:input={filterPresets}
          class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-gray-300"
        />
        <MagnifyingGlass class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
      </div>
      <ul class="space-y-2">
        {#each filteredPresets.slice(page * perPage, (page + 1) * perPage) as preset}
          <li class="flex justify-between items-center p-2 border border-gray-200 dark:border-gray-700 rounded-lg">
            <span class="text-gray-900 dark:text-gray-100">{preset.name}</span>
            <div class="flex space-x-2">
              <button
                class="text-green-500 hover:text-green-600"
                on:click={() => handleLoadPreset(preset)}
              >
                <Check className="size-5" />
              </button>
              <button
                class="text-red-500 hover:text-red-600"
                on:click={() => handleDeletePreset(preset.name)}
              >
                <Trash className="size-5" />
              </button>
            </div>
          </li>
        {/each}
      </ul>
    </div>
  </div>
</div>
