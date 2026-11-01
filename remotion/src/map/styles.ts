import type {Tint} from './types';

export type MapStyle = {
	vector: boolean; // draw land, lakes, rivers and coastlines ourselves (satellite: imagery does that)
	ocean: string;
	land: string;
	coast: string;
	coastWidth: number;
	lake: string;
	river: string;
	riverWidth: number;
	border: string;
	borderWidth: number;
	rasterFilter: string; // CSS filter on satellite / night imagery
	reliefOpacity: number;
	label: string;
	labelHalo: string;
	seaLabel: string;
	tints: Record<Tint, string>;
	highlightFill: number;
	dim: string;
	vignette: number;
	choropleth: [string, string, string]; // low, middle, high
	choroplethOpacity: number;
	nodata: string;
	globeOcean: string;
	globeLand: string;
	atmosphere: string;
	panel: string; // legend background
};

const tints = (accent: string): Record<Tint, string> => ({
	accent,
	alt: '#4fd1c5',
	red: '#ff4d4d',
	blue: '#4da3ff',
	neutral: '#e8e8e8',
});

export const STYLES: Record<string, MapStyle> = {
	// NASA Blue Marble imagery, white borders, amber accents.
	satellite: {
		vector: false,
		ocean: '#071a33',
		land: '#3a3a2e',
		coast: 'rgba(255,255,255,0.35)',
		coastWidth: 1,
		lake: '#0b2442',
		river: 'rgba(120,180,255,0.6)',
		riverWidth: 1,
		border: 'rgba(255,255,255,0.72)',
		borderWidth: 1.6,
		rasterFilter: 'none', // grade is baked into the images (pipeline/gibs.py)
		reliefOpacity: 0,
		label: '#ffffff',
		labelHalo: 'rgba(4,10,22,0.88)',
		seaLabel: '#a9d2ff',
		tints: tints('#ffb020'),
		highlightFill: 0.34,
		dim: 'rgba(2,8,20,0.58)',
		vignette: 0.5,
		choropleth: ['#fff1a8', '#f59e0b', '#c81d25'],
		choroplethOpacity: 0.8,
		nodata: 'rgba(160,170,185,0.35)',
		globeOcean: '#0a2a55',
		globeLand: '#5d6b45',
		atmosphere: 'rgba(110,170,255,0.55)',
		panel: 'rgba(6,12,24,0.78)',
	},
	// Light atlas: cream land, soft blue water, relief shading.
	atlas: {
		vector: true,
		ocean: '#b7d3e4',
		land: '#f2ecdf',
		coast: '#6f97b0',
		coastWidth: 1.3,
		lake: '#b7d3e4',
		river: '#86afc7',
		riverWidth: 1.2,
		border: '#8e8371',
		borderWidth: 1.5,
		rasterFilter: 'none',
		reliefOpacity: 0.6,
		label: '#1c222c',
		labelHalo: 'rgba(255,255,255,0.92)',
		seaLabel: '#3c6b8a',
		tints: {...tints('#e8590c'), neutral: '#3b4252'},
		highlightFill: 0.42,
		dim: 'rgba(40,45,58,0.32)',
		vignette: 0.22,
		choropleth: ['#fde9c4', '#f08c3a', '#8f1d1d'],
		choroplethOpacity: 0.9,
		nodata: 'rgba(150,150,150,0.35)',
		globeOcean: '#a8c9dc',
		globeLand: '#efe7d6',
		atmosphere: 'rgba(160,200,230,0.6)',
		panel: 'rgba(255,255,255,0.86)',
	},
	// Dark: navy land on near-black sea, glowing amber accents.
	midnight: {
		vector: true,
		ocean: '#060b16',
		land: '#18202f',
		coast: '#3e5172',
		coastWidth: 1.2,
		lake: '#060b16',
		river: '#2e4266',
		riverWidth: 1.1,
		border: '#5d7095',
		borderWidth: 1.3,
		rasterFilter: 'none',
		reliefOpacity: 0.4,
		label: '#eef2f8',
		labelHalo: 'rgba(3,6,12,0.92)',
		seaLabel: '#7d9cc6',
		tints: tints('#ffb000'),
		highlightFill: 0.4,
		dim: 'rgba(0,0,0,0.5)',
		vignette: 0.55,
		choropleth: ['#1d3557', '#2a9d8f', '#f4d35e'],
		choroplethOpacity: 0.92,
		nodata: 'rgba(90,100,120,0.35)',
		globeOcean: '#08101f',
		globeLand: '#243048',
		atmosphere: 'rgba(80,140,255,0.5)',
		panel: 'rgba(8,12,22,0.82)',
	},
};

const hex = (c: string): [number, number, number] => [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16)];

// Sequential colour for t in [0, 1] through the style's low / middle / high colours.
export const rampColor = (style: MapStyle, t: number): string => {
	const [a, b, c] = style.choropleth.map(hex);
	const u = Math.min(Math.max(t, 0), 1);
	const [p, q, s] = u < 0.5 ? [a, b, u * 2] : [b, c, (u - 0.5) * 2];
	const mix = (i: number) => Math.round(p[i] + (q[i] - p[i]) * s);
	return `rgb(${mix(0)},${mix(1)},${mix(2)})`;
};
