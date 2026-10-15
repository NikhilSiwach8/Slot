<script lang="ts">
	import { Container } from 'pixi-svelte';
	import { Button, type ButtonProps } from 'components-pixi';
	import { stateModal, stateBet, stateBetDerived } from 'state-shared';

	import { Sprite } from 'pixi-svelte';
	import HudCard from './hud/HudCard.svelte';
	import { SYMBOL_INFO_MAP } from '../../game/constants';
	import { UI_BASE_SIZE } from '../constants';
	import { getContext } from '../context';
	import { i18nDerived } from '../i18n/i18nDerived';

	const props: Partial<Omit<ButtonProps, 'children'>> = $props();
	const { stateXstateDerived, eventEmitter } = getContext();
	// a big BONUS card with the Duke on it, as tall as the SPIN card
	const sizes = { width: UI_BASE_SIZE * 1.6, height: UI_BASE_SIZE * 1.6 };
	const DUKE = SYMBOL_INFO_MAP.H1.static.assetKey;
	const disabled = $derived(!stateXstateDerived.isIdle());
	const active = $derived(stateBetDerived.activeBetMode()?.type === 'activate');

	const openModal = () => (stateModal.modal = { name: 'buyBonus' });
	const disableActiveBetMode = () => (stateBet.activeBetModeKey = 'BASE');
	const onpress = () => {
		eventEmitter.broadcast({ type: 'soundPressGeneral' });

		if (active) {
			disableActiveBetMode();
		} else {
			openModal();
		}
	};

	const getState = (value: {
		active: boolean;
		disabled: boolean;
		hovered: boolean;
		pressed: boolean;
	}) => {
		if (value.disabled) return 'disabled' as const;
		if (value.pressed) return 'pressed' as const;
		if (value.hovered) return 'hovered' as const;
		if (value.active) return 'active' as const;
		return 'default' as const;
	};
</script>

<Button {...props} {sizes} {disabled} {onpress}>
	{#snippet children({ center, hovered, pressed })}
		{@const state = getState({ active, disabled, hovered, pressed })}
		<Container
			{...center}
			scale={pressed ? 0.93 : hovered && !disabled ? 1.05 : 1}
			alpha={disabled ? 0.45 : 1}
		>
			<HudCard
				width={sizes.width}
				height={sizes.height}
				tab={state === 'active' ? i18nDerived.disable().toUpperCase() : 'BONUS'}
				active={state === 'active'}
				face={0x3a1650}
			/>
			<Sprite key={DUKE} anchor={0.5} width={sizes.width * 0.78} height={sizes.width * 0.75} y={sizes.height * 0.04} />
		</Container>
	{/snippet}
</Button>
