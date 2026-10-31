export type Visual = 'stock' | 'ai_image' | 'chart' | 'map' | 'title_card' | 'quote';

export type Word = {text: string; start: number; end: number}; // frames relative to the scene

export type ChartSpec = {
	type: 'bar' | 'line';
	title: string | null;
	unit: string;
	data: [string, number][];
};

export type MapSpec = {
	highlight: string[];
	points: {label: string; lon: number; lat: number}[];
};

export type KenBurns = {z0: number; z1: number; x0: number; x1: number; y0: number; y1: number};

export type SceneData = {
	id: string;
	visual: Visual;
	startFrame: number;
	durationFrames: number;
	narrationStartFrame: number;
	media: string | null;
	onScreenText: string | null;
	subtitle: string | null;
	chart: ChartSpec | null;
	map: MapSpec | null;
	quote: string | null;
	author: string | null;
	showCaptions: boolean;
	kenBurns: KenBurns;
	words: Word[];
};

export type Timeline = {
	fps: number;
	width: number;
	height: number;
	totalFrames: number;
	transitionFrames: number;
	scenes: SceneData[];
};
