export type Visual = 'stock' | 'ai_image' | 'chart' | 'map' | 'title_card' | 'quote' | 'chapter_card';

// Absolute frames; `p` = paragraph index (caption phrases never cross paragraphs).
export type Word = {text: string; start: number; end: number; p: number};

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

export type ShotData = {
	id: string;
	visual: Visual;
	startFrame: number;
	durationFrames: number; // includes the overlap the next shot dissolves over
	media: string | null;
	onScreenText: string | null;
	subtitle: string | null;
	chart: ChartSpec | null;
	map: MapSpec | null;
	quote: string | null;
	author: string | null;
	kenBurns: KenBurns;
	chapterNumber: number | null;
};

export type ChapterMark = {title: string; startFrame: number; mood: string};

export type Timeline = {
	fps: number;
	width: number;
	height: number;
	totalFrames: number;
	transitionFrames: number;
	showCaptions: boolean;
	shots: ShotData[];
	words: Word[];
	chapters: ChapterMark[];
};
