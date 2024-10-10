<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let prompt = '';
	let aspectRatio = '1:1';
	let generatedImageUrl = '';

	const aspectRatioOptions = ['1:1', '3:2', '16:9', '3:4'];

	const generateImage = async () => {
		// Placeholder for image generation logic
		// Replace this with actual API call to generate image
		generatedImageUrl = 'https://via.placeholder.com/300';
	};

	onMount(() => {
		goto('/image');
	});
</script>

<div class="container mx-auto p-4">
	<h1 class="text-2xl font-bold mb-4">Image Generation</h1>
	<div class="grid grid-cols-2 gap-4">
		<div>
			<form on:submit|preventDefault={generateImage}>
				<div class="mb-4">
					<label for="prompt" class="block text-sm font-medium text-gray-700">Prompt</label>
					<input
						type="text"
						id="prompt"
						bind:value={prompt}
						class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
					/>
				</div>
				<div class="mb-4">
					<label for="aspect-ratio" class="block text-sm font-medium text-gray-700">Aspect Ratio</label>
					<select
						id="aspect-ratio"
						bind:value={aspectRatio}
						class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
					>
						{#each aspectRatioOptions as option}
							<option value={option}>{option}</option>
						{/each}
					</select>
				</div>
				<button
					type="submit"
					class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
				>
					Generate Image
				</button>
			</form>
		</div>
		<div>
			{#if generatedImageUrl}
				<img src={generatedImageUrl} alt="Generated Image" class="w-full h-auto" />
			{/if}
		</div>
	</div>
</div>
