// Data written by pipeline/maps.py (one JSON per map block). Coordinates are unit Mercator
// (x, y in [0, 1] for the whole Web Mercator square), ints scaled by `q` unless noted.

export type Tint = 'accent' | 'alt' | 'red' | 'blue' | 'neutral';
export type CamKey = {start: number; frames: number; x: number; y: number; w: number};

type Base = {in: number; out: number};

// bb: the country's main body (no far overseas territories), unit Mercator floats
export type HighlightEl = Base & {kind: 'highlight'; id: string; name: string; lx: number; ly: number; dim: boolean; bb: [number, number, number, number]; rings: number[][]};
export type PlaceEl = Base & {
	kind: 'place';
	label: string;
	marker: 'city' | 'capital' | 'port' | 'site' | 'event' | 'sea' | 'label';
	x: number;
	y: number;
};
export type RouteEl = Base & {kind: 'route'; pts: number[]; mode: 'sea' | 'air' | 'line'; tint: Tint; label: string | null; draw: number};
export type ArrowEl = Base & {
	kind: 'arrow';
	from: [number, number];
	to: [number, number];
	tint: Tint;
	label: string | null;
	bend: number;
	draw: number;
};
export type ChoroplethEl = Base & {
	kind: 'choropleth';
	title: string;
	unit: string;
	source: string | null;
	min: number;
	max: number;
	scale: 'linear' | 'log';
	items: {t: number | null; rings: number[][]}[];
};
// rings here are lon/lat floats (re-projected every frame while the outline travels)
export type TrueSizeEl = Base & {kind: 'truesize'; from: [number, number]; to: [number, number]; label: string; move: number; rings: number[][]};
// Sentinel-2 before/after: `after` wipes in over `before` (frames relative to `in`).
export type CompareEl = Base & {kind: 'compare'; before: Raster; after: Raster; labelBefore: string; labelAfter: string; hold: number; wipe: number};
export type MapElement = HighlightEl | PlaceEl | RouteEl | ArrowEl | ChoroplethEl | TrueSizeEl | CompareEl;

export type Raster = {src: string; x0: number; y0: number; x1: number; y1: number; layer: 'day' | 's2' | 'night' | 'relief'; px: number};

export type Lod = {
	lod: string;
	maxSpan: number;
	box: [number, number, number, number];
	land?: number[][];
	lakes?: number[][];
	rivers?: number[][];
	coast?: number[][];
	borders: number[][];
};

export type GlobeSpec = {
	frames: number; // the globe dives until this frame, then hands over to the flat map
	fromLon: number;
	fromLat: number;
	toLon: number;
	toLat: number;
	texture: string | null; // equirectangular image (satellite style)
	land: number[][]; // lon/lat floats, 110m
};

export type MapBlockData = {
	style: 'satellite' | 'atlas' | 'midnight';
	frames: number;
	fps: number;
	drift: number;
	rho: number;
	q: number;
	safeBottom: number;
	cams: CamKey[];
	globe: GlobeSpec | null;
	layers: {f: number; layer: 'day' | 'night'}[];
	rasters: Raster[];
	lods: Lod[];
	elements: MapElement[];
};
