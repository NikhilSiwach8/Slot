<!-- Same HUD as desktop: the two corner clusters fit the 1920-wide layout here too. -->
<script lang="ts">
	import LayoutDesktop from './LayoutDesktop.svelte';
	import type { LayoutUiProps } from '../types';

	const props: LayoutUiProps = $props();
</script>

<LayoutDesktop {...props} />
