export type Visual = 'stock' | 'ai_image' | 'photo' | 'chart' | 'map' | 'title_card' | 'quote' | 'chapter_card';

// Absolute frames; `p` = paragraph index (caption phrases never cross paragraphs).
export type Word = {text: string; start: number; end: number; p: number};

export type ChartSpec = {
	type: 'bar' | 'line';
	title: string | null;
	unit: string;
	data: [string, number][];
};

// Number inside an on-screen label that counts up ("About $9.6 billion"), decided by pipeline/timeline.py.
export type CountUp = {prefix: string; value: number; decimals: number; commas: boolean; suffix: string};
export type ScreenText = {text: string; from: number; countUp: CountUp | null};

export type KenBurns = {z0: number; z1: number; x0: number; x1: number; y0: number; y1: number};

export type ShotData = {
	id: string;
	visual: Visual;
	startFrame: number;
	durationFrames: number; // includes the overlap the next shot dissolves over
	transitionIn: number; // frames this shot takes to appear over the previous one
	media: string | null; // stock clip, AI image, or the map block JSON
	texts: ScreenText[]; // lower-third labels, frames relative to the shot
	onScreenText: string | null; // title of title / chapter cards
	subtitle: string | null;
	chart: ChartSpec | null;
	quote: string | null;
	author: string | null;
	kenBurns: KenBurns;
	chapterNumber: number | null;
	photoFit: 'cover' | 'contain' | null; // archive photos: full frame, or framed over a blurred copy
};

export type ChapterMark = {title: string; startFrame: number; mood: string};

export type Timeline = {
	fps: number;
	width: number;
	height: number;
	totalFrames: number;
	showCaptions: boolean;
	mapStyle: string;
	shots: ShotData[];
	words: Word[];
	chapters: ChapterMark[];
};
