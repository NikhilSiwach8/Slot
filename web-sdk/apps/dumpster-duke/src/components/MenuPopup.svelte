<!--
	Menu popup opened by the HUD menu pill: music and sound-effect volume sliders, a mute
	switch, and buttons for the game info (rules + paytable) and settings. Sits above the
	menu button in the lower-left corner; tapping outside closes it.
-->
<script lang="ts">
	import '@fontsource/lilita-one/400.css';

	import { OnHotkey } from 'components-shared';
	import { stateModal, stateSound, stateUi } from 'state-shared';

	import { socialWording } from '../game/social';

	const close = () => (stateUi.menuOpen = false);
	const open = (name: 'gameRules' | 'payTable' | 'settings') => {
		stateUi.menuOpen = false;
		stateModal.modal = { name };
	};
	const muted = $derived(stateSound.volumeValueMaster === 0);
	const toggleMute = () => (stateSound.volumeValueMaster = muted ? 50 : 0);
</script>

{#if stateUi.menuOpen}
	<OnHotkey hotkey="Escape" onpress={close} />
	<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
	<div class="backdrop" onclick={close}></div>
	<div class="popup" use:socialWording>
		<label class="row">
			<span class="icon" aria-hidden="true">♫</span>
			<span class="sr">Music volume</span>
			<input type="range" min="0" max="100" bind:value={stateSound.volumeValueMusic} style="--fill: {stateSound.volumeValueMusic}%" />
		</label>
		<label class="row">
			<span class="icon" aria-hidden="true">🔊</span>
			<span class="sr">Sound effects volume</span>
			<input type="range" min="0" max="100" bind:value={stateSound.volumeValueSoundEffect} style="--fill: {stateSound.volumeValueSoundEffect}%" />
		</label>
		<button class="mute" class:on={muted} onclick={toggleMute}>{muted ? 'SOUND OFF' : 'SOUND ON'}</button>
		<hr />
		<button class="gold" onclick={() => open('gameRules')}><span class="i">i</span> GAME INFO</button>
		<div class="pair">
			<button class="dark" onclick={() => open('payTable')}>PAYTABLE</button>
			<button class="dark" onclick={() => open('settings')}>SETTINGS</button>
		</div>
	</div>
{/if}

<style>
	.backdrop {
		position: fixed;
		inset: 0;
		z-index: 900;
	}
	.popup {
		--u: min(1vw, 1.8vh);
		position: fixed;
		z-index: 901;
		left: calc(var(--u) * 3);
		bottom: calc(var(--u) * 17);
		width: calc(var(--u) * 26);
		padding: calc(var(--u) * 1.8);
		display: flex;
		flex-direction: column;
		gap: calc(var(--u) * 1.2);
		border-radius: calc(var(--u) * 2.2);
		background: linear-gradient(#2a1745, #1d1033);
		border: calc(var(--u) * 0.45) solid #f2b33d;
		box-shadow: 0 0 0 calc(var(--u) * 0.35) #2a1208, 0 calc(var(--u) * 1) calc(var(--u) * 3) rgba(0, 0, 0, 0.6);
		font-family: 'Lilita One', 'Arial Black', sans-serif;
		color: #f6efe2;
	}
	@media (orientation: portrait) {
		.popup {
			--u: min(2.6vw, 1.4vh);
			left: 50%;
			transform: translateX(-50%);
			bottom: calc(var(--u) * 30);
		}
	}
	.row {
		display: flex;
		align-items: center;
		gap: calc(var(--u) * 1.2);
	}
	.icon {
		width: calc(var(--u) * 3);
		font-size: calc(var(--u) * 2.4);
		text-align: center;
		color: #ffcf3a;
	}
	.sr {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip: rect(0 0 0 0);
	}
	input[type='range'] {
		flex: 1;
		height: calc(var(--u) * 1.1);
		appearance: none;
		border-radius: calc(var(--u) * 1);
		background: linear-gradient(90deg, #f39a1c, #ffe066) 0 / var(--fill, 50%) 100% no-repeat, #3d2a58;
		accent-color: #ffcf3a;
		cursor: pointer;
	}
	input[type='range']::-webkit-slider-thumb {
		appearance: none;
		width: calc(var(--u) * 2.4);
		height: calc(var(--u) * 2.4);
		border-radius: 50%;
		background: #fff3c4;
		border: calc(var(--u) * 0.35) solid #5a2a0a;
	}
	input[type='range']::-moz-range-thumb {
		width: calc(var(--u) * 2);
		height: calc(var(--u) * 2);
		border-radius: 50%;
		background: #fff3c4;
		border: calc(var(--u) * 0.35) solid #5a2a0a;
	}
	hr {
		width: 100%;
		border: 0;
		border-top: 1px solid rgba(242, 179, 61, 0.35);
		margin: 0;
	}
	button {
		font-family: inherit;
		cursor: pointer;
		border-radius: calc(var(--u) * 1.2);
		padding: calc(var(--u) * 0.8) 0;
		font-size: calc(var(--u) * 1.8);
	}
	button.gold {
		border: calc(var(--u) * 0.35) solid #5a2a0a;
		background: linear-gradient(#ffe066, #f39a1c);
		color: #4a1d06;
		box-shadow: 0 calc(var(--u) * 0.4) 0 #5a2a0a;
	}
	.i {
		display: inline-grid;
		place-items: center;
		width: calc(var(--u) * 2.2);
		height: calc(var(--u) * 2.2);
		border-radius: 50%;
		background: #4a1d06;
		color: #ffe066;
		font-size: calc(var(--u) * 1.5);
		margin-right: calc(var(--u) * 0.5);
	}
	.pair {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: calc(var(--u) * 1);
	}
	button.dark,
	button.mute {
		border: calc(var(--u) * 0.3) solid #f2b33d;
		background: #1d1033;
		color: #ffcf3a;
		font-size: calc(var(--u) * 1.5);
	}
	button.mute.on {
		color: #ff9a8a;
		border-color: #ff9a8a;
	}
</style>
