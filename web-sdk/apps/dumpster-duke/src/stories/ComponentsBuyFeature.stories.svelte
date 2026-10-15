<script lang="ts" module>
	import { defineMeta } from '@storybook/addon-svelte-csf';

	const { Story } = defineMeta({ title: 'Components/<BuyFeature>' });
</script>

<script lang="ts">
	import { StoryLocale } from 'components-storybook';

	import BuyFeatureScene from './BuyFeatureScene.svelte';
	import { setContext } from '../game/context';

	setContext();
</script>

<Story name="menu">
	{#snippet template()}
		<StoryLocale lang="en"><BuyFeatureScene modal="buyBonus" /></StoryLocale>
	{/snippet}
</Story>

<Story name="ante on">
	{#snippet template()}
		<StoryLocale lang="en"><BuyFeatureScene modal="buyBonus" ante /></StoryLocale>
	{/snippet}
</Story>

<Story name="feature spin on">
	{#snippet template()}
		<StoryLocale lang="en"><BuyFeatureScene modal="buyBonus" spinMode="FEATURE" /></StoryLocale>
	{/snippet}
</Story>

<Story name="detail super">
	{#snippet template()}
		<StoryLocale lang="en"><BuyFeatureScene modal="buyBonusConfirm" selected="SUPER" /></StoryLocale>
	{/snippet}
</Story>

<Story name="detail feature spin">
	{#snippet template()}
		<StoryLocale lang="en"><BuyFeatureScene modal="buyBonusConfirm" selected="FEATURE" /></StoryLocale>
	{/snippet}
</Story>

<Story name="confirm">
	{#snippet template()}
		<StoryLocale lang="en"><BuyFeatureScene modal="buyBonusConfirm" /></StoryLocale>
	{/snippet}
</Story>
