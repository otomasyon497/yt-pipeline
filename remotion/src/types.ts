export type Visual = 'stock' | 'ai_image' | 'photo' | 'chart' | 'map' | 'title_card' | 'quote' | 'chapter_card' | 'stat';

// Full-screen number card: `value` counts up when the pipeline found a number in it (never a bare year).
export type StatSpec = {value: string; label: string; note?: string | null; source?: string | null; countUp: CountUp | null};

// Absolute frames; `p` = paragraph index (caption phrases never cross paragraphs).
export type Word = {text: string; start: number; end: number; p: number};

export type ChartSpec = {
	type: 'bar' | 'line';
	title: string | null;
	unit: string;
	data: [string, number][];
	source?: string | null;
	ref?: [number, string] | null;
	highlight?: number | null;
};

// Number inside an on-screen label that counts up ("About $9.6 billion"), decided by pipeline/timeline.py.
export type CountUp = {prefix: string; value: number; decimals: number; commas: boolean; suffix: string};
// instant: a Short's hook line, fully on screen from the first frame (no slide-in).
export type ScreenText = {text: string; from: number; countUp: CountUp | null; kind?: 'label' | 'question'; hold?: number; instant?: boolean};

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
	stat?: StatSpec | null;
	quote: string | null;
	author: string | null;
	kenBurns: KenBurns;
	chapterNumber: number | null;
	photoFit: 'cover' | 'contain' | null; // archive photos: full frame, or framed over a blurred copy
	where?: {src: string; label: string} | null; // locator inset (stock / photo / AI shots)
	cardBg?: CardBg | null; // chapter cards: blurred image of what comes next
};

// Screen placement of the chapter card backdrop (a map block's image around its first view, or a photo).
export type CardBg = {src: string; left: number; top: number; width: number; height: number; cover?: boolean};

export type ChapterMark = {title: string; startFrame: number; mood: string};

export type Timeline = {
	fps: number;
	width: number;
	height: number;
	uiScale?: number; // map labels / markers / lines (1.4 in Shorts)
	totalFrames: number;
	showCaptions: boolean;
	mapStyle: string;
	look?: 'none' | 'warm' | 'cool';
	shots: ShotData[];
	words: Word[];
	chapters: ChapterMark[];
};
