<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';
	import { Button, type ButtonProps } from 'components-pixi';
	import { OnHotkey } from 'components-shared';
	import { stateBetDerived, stateModal, stateUi } from 'state-shared';

	import HudCard from './hud/HudCard.svelte';
	import HudIcon from './hud/HudIcon.svelte';
	import ButtonBetProvider from './ButtonBetProvider.svelte';
	import { UI_BASE_SIZE } from '../constants';
	import { i18nDerived } from '../i18n/i18nDerived';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const disabled = $derived(!stateBetDerived.isBetCostAvailable());
	// the space bar plays a round like the SPIN card, but not while a menu or dialog is open
	const hotkeyDisabled = $derived(disabled || !!stateModal.modal || stateUi.menuOpen);
	// the SPIN card is the hero of the HUD
	const sizes = { width: UI_BASE_SIZE * 1.6, height: UI_BASE_SIZE * 1.6 };
</script>

<ButtonBetProvider>
	{#snippet children({ key, onpress })}
		{@const stopping = !['spin_default', 'spin_disabled'].includes(key)}
		{@const dimmed = disabled || ['spin_disabled', 'stop_disabled'].includes(key)}
		<OnHotkey hotkey="Space" disabled={hotkeyDisabled} {onpress} />
		<Button {...props} {sizes} {onpress} {disabled}>
			{#snippet children({ center, hovered, pressed })}
				<Container
					{...center}
					scale={pressed ? 0.93 : hovered && !dimmed ? 1.04 : 1}
					alpha={dimmed ? 0.5 : 1}
				>
					<HudCard width={sizes.width} height={sizes.height} tab="SPIN" />
					{#if stopping}
						<BitmapText anchor={0.5} text={i18nDerived.stop().toUpperCase()} style={{ fontFamily: 'gold', fontSize: sizes.width * 0.2 }} />
					{:else}
						<HudIcon name="spin" size={sizes.width * 0.62} />
					{/if}
				</Container>
			{/snippet}
		</Button>
	{/snippet}
</ButtonBetProvider>
