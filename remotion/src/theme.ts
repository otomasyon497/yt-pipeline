import {loadFont as loadBebas} from '@remotion/google-fonts/BebasNeue';
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';

export const display = loadBebas().fontFamily;
export const body = loadInter('normal', {weights: ['500', '700'], subsets: ['latin']}).fontFamily;
// Same family, italic face (map sea labels).
export const bodyItalic = loadInter('italic', {weights: ['500'], subsets: ['latin']}).fontFamily;

export const colors = {
	bg: '#0b0f1a',
	panel: '#141a2b',
	line: '#2c3752',
	text: '#f4f1ea',
	muted: '#9aa4bd',
	accent: '#f5a623',
};

// Soft ease used by most animations.
export const easeOut = (t: number) => 1 - Math.pow(1 - Math.min(Math.max(t, 0), 1), 3);
export const clamp01 = (t: number) => Math.min(Math.max(t, 0), 1);
