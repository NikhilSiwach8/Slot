<script lang="ts" module>
	import { sound, type MusicName, type SoundEffectName, type SoundName } from '../game/sound';

	export type EmitterEventSound =
		| { type: 'soundMusic'; name: MusicName }
		| { type: 'soundOnce'; name: SoundEffectName; forcePlay?: boolean }
		| { type: 'soundLoop'; name: SoundEffectName }
		| { type: 'soundStop'; name: SoundName }
		| { type: 'soundFade'; name: SoundName; from: number; to: number; duration: number }
		| { type: 'soundScatterCounterIncrease' }
		| { type: 'soundScatterCounterClear' };
</script>

<script lang="ts">
	import { onMount } from 'svelte';

	import { waitForTimeout } from 'utils-shared/wait';
	import { SECOND } from 'constants-shared/time';
	import { stateBet } from 'state-shared';

	import { getContext } from '../game/context';
	import { stateXstateDerived } from '../game/stateXstate';

	const context = getContext();

	// Base-game music level: quieter while the game waits for the player, fuller while the
	// reels spin and wins play out. Relative to the track's own volume and the player's
	// music slider (both still apply).
	const MUSIC_LEVEL = { idle: 0.45, playing: 1 };
	const FADE_MS = { toIdle: 1500, toPlaying: 350 };
	let musicLevel = MUSIC_LEVEL.idle;
	const setMusicLevel = (target: number, duration: number) => {
		sound.players.music.fade({ name: 'bgm_main', from: musicLevel, to: target, duration });
		musicLevel = target;
	};
	$effect(() => {
		const idle = stateXstateDerived.isIdle();
		const target = idle ? MUSIC_LEVEL.idle : MUSIC_LEVEL.playing;
		if (target !== musicLevel) setMusicLevel(target, idle ? FADE_MS.toIdle : FADE_MS.toPlaying);
	});

	context.eventEmitter.subscribeOnMount({
		// ui
		soundBetMode: async ({ betModeKey }) => {
			if (betModeKey === 'SUPERSPIN') {
				// check if SUPERSPIN, when changing the bet mode.
				sound.players.once.play({ name: 'sfx_winlevel_end' });
				await waitForTimeout(SECOND);
				sound.players.music.play({ name: 'bgm_freespin' });
			} else {
				sound.players.music.play({ name: 'bgm_main' });
			}
		},
		soundPressGeneral: () => sound.players.once.play({ name: 'sfx_btn_general' }),
		soundPressBet: () => sound.players.once.play({ name: 'sfx_btn_spin' }),
		// scatterCounter
		soundScatterCounterIncrease: () => (context.stateGame.scatterCounter = context.stateGame.scatterCounter + 1), // prettier-ignore
		soundScatterCounterClear: () => (context.stateGame.scatterCounter = 0),
		// game
		soundMusic: ({ name }) => {
			sound.players.music.play({ name });
			// the base track can restart (after a bonus or a big win): keep the current level
			if (name === 'bgm_main') setMusicLevel(musicLevel, 10);
		},
		soundLoop: ({ name }) => sound.players.loop.play({ name }),
		soundOnce: ({ name, forcePlay }) => sound.players.once.play({ name, forcePlay }),
		soundStop: ({ name }) => sound.stop({ name }),
		soundFade: async ({ name, duration, from, to }) => await sound.fade({ name, duration, from, to }), // prettier-ignore
	});

	onMount(() => {
		if (stateBet.activeBetModeKey === 'SUPERSPIN') {
			// check if SUPERSPIN, when resume bet and the bet is a super spin.
			sound.players.music.play({ name: 'bgm_freespin' });
		} else {
			sound.players.music.play({ name: 'bgm_main' });
			// audio may still be loading/locked here: apply the level once the track really starts
			sound.players.music.howl.on('play', () => setMusicLevel(musicLevel, 10));

			//How to control volume per soundfile(use fade)
			// sound.players.music.fade({ name: 'bgm_main', from: 0, to: 1, duration: 3000 });

			//How to control rate per soundfile
			// sound.players.music.rate({ rate: 2, name: 'bgm_main'}); // change play back rate(1: default, 0: slow, 1+ fasterm and higher pitch )
		}
	});
</script>
