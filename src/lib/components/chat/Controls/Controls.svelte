<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	const dispatch = createEventDispatcher();
	const i18n = getContext('i18n');

	import XMark from '$lib/components/icons/XMark.svelte';
	import AdvancedParams from '../Settings/Advanced/AdvancedParams.svelte';
	import Valves from '$lib/components/chat/Controls/Valves.svelte';
	import FileItem from '$lib/components/common/FileItem.svelte';
	import Collapsible from '$lib/components/common/Collapsible.svelte';
	import Modal from '$lib/components/common/Modal.svelte';

	import { user } from '$lib/stores';
	export let models = [];
	export let chatFiles = [];
	export let params = {};

	let showModal = false;
	let presets = [];
	let searchQuery = '';
	let validationMessage = '';

	// Function to save preset
	const savePreset = async () => {
		const presetName = prompt($i18n.t('Enter preset name:'));
		if (!presetName) {
			validationMessage = $i18n.t('Preset name cannot be empty.');
			return;
		}

		const preset = {
			name: presetName,
			system_prompt: params.system,
			advanced_params: params
		};

		try {
			const response = await fetch('/api/presets/save', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(preset)
			});

			if (!response.ok) {
				const errorData = await response.json();
				validationMessage = $i18n.t(errorData.detail);
				throw new Error('Failed to save preset');
			}

			alert($i18n.t('Preset saved successfully!'));
			validationMessage = '';
		} catch (error) {
			console.error(error);
			alert($i18n.t('Failed to save preset.'));
		}
	};

	// Function to load preset
	const loadPreset = async () => {
		try {
			const response = await fetch('/api/presets');
			if (!response.ok) {
				throw new Error('Failed to fetch presets');
			}

			presets = await response.json();
			showModal = true;
		} catch (error) {
			console.error(error);
			alert($i18n.t('Failed to load presets.'));
		}
	};

	const applyPreset = (preset) => {
		params.system = preset.system_prompt;
		params = { ...params, ...preset.advanced_params };
		showModal = false;
	};

	const filteredPresets = () => {
		return presets.filter((preset) =>
			preset.name.toLowerCase().includes(searchQuery.toLowerCase())
		);
	};
</script>

<div class=" dark:text-white">
	<div class=" flex justify-between dark:text-gray-100 mb-2">
		<div class=" text-lg font-medium self-center font-primary">{$i18n.t('Chat Controls')}</div>
		<button
			class="self-center"
			on:click={() => {
				dispatch('close');
			}}
		>
			<XMark className="size-4" />
		</button>
	</div>

	<div class=" dark:text-gray-200 text-sm font-primary py-0.5">
		{#if chatFiles.length > 0}
			<Collapsible title={$i18n.t('Files')} open={true}>
				<div class="flex flex-col gap-1 mt-1.5" slot="content">
					{#each chatFiles as file, fileIdx}
						<FileItem
							className="w-full"
							item={file}
							edit={true}
							url={file?.url ? file.url : null}
							name={file.name}
							type={file.type}
							size={file?.size}
							dismissible={true}
							on:dismiss={() => {
								// Remove the file from the chatFiles array

								chatFiles.splice(fileIdx, 1);
								chatFiles = chatFiles;
							}}
							on:click={() => {
								console.log(file);
							}}
						/>
					{/each}
				</div>
			</Collapsible>

			<hr class="my-2 border-gray-100 dark:border-gray-800" />
		{/if}

		<Collapsible title={$i18n.t('Valves')}>
			<div class="text-sm mt-1.5" slot="content">
				<Valves />
			</div>
		</Collapsible>

		<hr class="my-2 border-gray-100 dark:border-gray-800" />

		<Collapsible title={$i18n.t('System Prompt')} open={true}>
			<div class=" mt-1.5" slot="content">
				<textarea
					bind:value={params.system}
					class="w-full rounded-lg px-3.5 py-2.5 text-sm dark:text-gray-300 dark:bg-gray-850 border border-gray-100 dark:border-gray-800 outline-none resize-none"
					rows="4"
					placeholder={$i18n.t('Enter system prompt')}
				/>
			</div>
		</Collapsible>

		<hr class="my-2 border-gray-100 dark:border-gray-800" />

		<Collapsible title={$i18n.t('Advanced Params')} open={true}>
			<div class="text-sm mt-1.5" slot="content">
				<div>
					<AdvancedParams admin={$user?.role === 'admin'} bind:params />
				</div>
			</div>
		</Collapsible>

		<hr class="my-2 border-gray-100 dark:border-gray-800" />

		<div class="flex justify-between mt-4">
			<button
				class="bg-blue-500 text-white px-4 py-2 rounded"
				on:click={savePreset}
			>
				{$i18n.t('Save Preset')}
			</button>
			<button
				class="bg-green-500 text-white px-4 py-2 rounded"
				on:click={loadPreset}
			>
				{$i18n.t('Load Preset')}
			</button>
		</div>

		{#if validationMessage}
			<div class="text-red-500 mt-2">{validationMessage}</div>
		{/if}
	</div>
</div>

{#if showModal}
	<Modal on:close={() => (showModal = false)}>
		<div class="p-4">
			<input
				type="text"
				placeholder={$i18n.t('Search presets')}
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
{/if}
