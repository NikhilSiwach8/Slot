// Halloween night grade for the background art: greens pulled down, purples and blues
// lifted, warm lantern light kept, a little darker overall. One shared filter instance.
import { ColorMatrixFilter } from 'pixi.js';

export const nightGrade = new ColorMatrixFilter();
nightGrade.matrix = [
	0.98, 0.1, 0.0, 0, -0.03,
	0.03, 0.56, 0.05, 0, -0.04,
	0.08, 0.08, 0.92, 0, 0.0,
	0, 0, 0, 1, 0,
];
