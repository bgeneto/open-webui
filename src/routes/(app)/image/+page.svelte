<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	onMount(() => {
		goto('/image');
	});
</script>

<div>
	<h1>Image Page</h1>
	<p>This is a placeholder for the image content.</p>
</div>
