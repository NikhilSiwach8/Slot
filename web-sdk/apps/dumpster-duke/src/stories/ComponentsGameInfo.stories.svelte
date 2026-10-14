<script lang="ts" module>
	import { defineMeta } from '@storybook/addon-svelte-csf';

	const { Story } = defineMeta({ title: 'Components/<GameInfo>' });
</script>

<script lang="ts">
	import GameInfo from '../components/info/GameInfo.svelte';
</script>

<Story name="rules">
	{#snippet template()}
		<div style="background: #1d1530; min-height: 100vh; display: flex; justify-content: center;">
			<GameInfo />
		</div>
	{/snippet}
</Story>
