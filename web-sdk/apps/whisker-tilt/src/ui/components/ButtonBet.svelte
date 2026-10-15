<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';
	import { Button, type ButtonProps } from 'components-pixi';
	import { OnHotkey } from 'components-shared';
	import { stateBetDerived } from 'state-shared';

	import UiArt from './UiArt.svelte';
	import ButtonBetProvider from './ButtonBetProvider.svelte';
	import { UI_BASE_SIZE } from '../constants';
	import { i18nDerived } from '../i18n/i18nDerived';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const disabled = $derived(!stateBetDerived.isBetCostAvailable());
	// the spin button is the hero of the bar, like on the art sheet
	const sizes = { width: UI_BASE_SIZE * 1.35, height: UI_BASE_SIZE * 1.35 };
</script>

<ButtonBetProvider>
	{#snippet children({ key, onpress })}
		{@const stopping = !['spin_default', 'spin_disabled'].includes(key)}
		{@const dimmed = disabled || ['spin_disabled', 'stop_disabled'].includes(key)}
		<OnHotkey hotkey="Space" {disabled} {onpress} />
		<Button {...props} {sizes} {onpress} {disabled}>
			{#snippet children({ center, hovered, pressed })}
				<Container
					{...center}
					scale={pressed ? 0.93 : hovered && !dimmed ? 1.04 : 1}
					alpha={dimmed ? 0.5 : 1}
				>
					<UiArt name={stopping ? 'btn_blank' : 'btn_spin'} width={sizes.width} height={sizes.height} />
					{#if stopping}
						<BitmapText anchor={0.5} text={i18nDerived.stop().toUpperCase()} style={{ fontFamily: 'gold', fontSize: sizes.width * 0.2 }} />
					{/if}
				</Container>
			{/snippet}
		</Button>
	{/snippet}
</ButtonBetProvider>
