<script lang="ts" module>
	import { defineMeta } from '@storybook/addon-svelte-csf';

	const { Story } = defineMeta({ title: 'Components/<ProviderSplash>' });
</script>

<!-- The provider splash on its own (nothing loads here, so it stays up). -->
<script lang="ts">
	import ProviderSplash, { stateSplash } from '../components/ProviderSplash.svelte';
	import { setContext } from '../game/context';

	setContext();
	stateSplash.visible = true;
</script>

<Story name="loading">
	<ProviderSplash />
</Story>
