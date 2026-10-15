<script lang="ts" module>
	import type { ButtonIcon } from '../types';
	import type { HudIconName } from './hud/HudIcon.svelte';

	// How each button looks: a drawn icon on a HUD card, a bare chevron (bet − / +), or a
	// short label in the game font on a card.
	const LOOK: Record<ButtonIcon, { icon?: HudIconName; label?: string; bare?: boolean }> = {
		decrease: { icon: 'left', bare: true },
		increase: { icon: 'right', bare: true },
		menu: { icon: 'menu' },
		menuExit: { icon: 'close' },
		turbo: { icon: 'bolt' },
		autoSpin: { icon: 'auto' },
		payTable: { label: 'PAYS' },
		info: { label: 'INFO' },
		settings: { label: 'SET' },
		soundOn: { label: 'SOUND' },
		soundOff: { label: 'MUTED' },
	};
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';
	import { BitmapText, Container } from 'pixi-svelte';
	import { Button, type ButtonProps } from 'components-pixi';

	import HudCard from './hud/HudCard.svelte';
	import HudIcon from './hud/HudIcon.svelte';

	type Props = Omit<ButtonProps, 'children'> & {
		icon: ButtonIcon;
		sizes: { width: number; height: number };
		active?: boolean;
		children?: Snippet;
		variant?: 'dark' | 'light';
	};

	const { icon, active, variant: _variant, children: childrenFromParent, ...buttonProps }: Props = $props();
	const look = $derived(LOOK[icon]);
	const w = $derived(buttonProps.sizes.width);
	const h = $derived(buttonProps.sizes.height);
	const iconSize = $derived(Math.min(w, h) * (look.bare ? 0.9 : 0.62));
</script>

<Button {...buttonProps}>
	{#snippet children({ center, hovered, pressed })}
		<Container
			{...center}
			scale={pressed ? 0.93 : hovered && !buttonProps.disabled ? 1.05 : 1}
			alpha={buttonProps.disabled ? 0.45 : 1}
		>
			{#if !look.bare}
				<HudCard width={w} height={h} {active} />
			{/if}
			{#if look.icon}
				<HudIcon
					name={look.icon}
					size={iconSize}
					color={look.bare ? 0xffcf3a : active ? 0xffcf3a : 0xffffff}
				/>
			{/if}
			{#if look.label}
				<BitmapText
					anchor={0.5}
					text={look.label}
					style={{ fontFamily: 'gold', fontSize: Math.min(w, h) * (look.label.length > 4 ? 0.2 : 0.26) }}
				/>
			{/if}
		</Container>

		{@render childrenFromParent?.()}
	{/snippet}
</Button>
