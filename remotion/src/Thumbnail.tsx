import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {colors, display} from './theme';

// split: our own before | after imagery (pipeline/thumbnails.py), `labels` = the two years.
export type ThumbProps = {text: string; background: string; layout: 'left' | 'center' | 'right' | 'split'; labels?: [string, string]};

const SHADOW = '0 6px 24px rgba(0,0,0,0.6)';

// Before | after: years in the top corners, the amber wipe line, the headline along the bottom (last word amber).
const Split: React.FC<ThumbProps> = ({text, background, labels}) => {
	const words = text.toUpperCase().split(/\s+/).filter(Boolean);
	const year = (s: string, color: string, side: 'left' | 'right') => (
		<div style={{position: 'absolute', top: 18, [side]: 40, fontFamily: display, fontSize: 150, lineHeight: 1, letterSpacing: 3, color, textShadow: SHADOW, WebkitTextStroke: `3px ${colors.bg}`}}>
			{s}
		</div>
	);
	return (
		<AbsoluteFill style={{backgroundColor: colors.bg}}>
			<Img src={staticFile(`media/${background}`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
			<AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,10,18,0) 55%, rgba(8,10,18,0.85) 100%)'}} />
			<div style={{position: 'absolute', left: 636, top: 0, width: 8, height: 720, backgroundColor: colors.accent}} />
			{labels ? year(labels[0], colors.text, 'left') : null}
			{labels ? year(labels[1], colors.accent, 'right') : null}
			<AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 16}}>
				<div style={{fontFamily: display, fontSize: 170, lineHeight: 1, letterSpacing: 4, textShadow: SHADOW, WebkitTextStroke: `3px ${colors.bg}`, whiteSpace: 'nowrap'}}>
					{words.map((w, i) => (
						<span key={i} style={{color: i === words.length - 1 ? colors.accent : colors.text}}>
							{w}
							{i < words.length - 1 ? ' ' : ''}
						</span>
					))}
				</div>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

// Stills are rendered once, so gradients/shadows are fine here (unlike in the video compositions).
export const Thumbnail: React.FC<ThumbProps> = (props) => {
	const {text, background, layout} = props;
	if (layout === 'split') return <Split {...props} />;
	const words = text.toUpperCase().split(/\s+/).filter(Boolean);
	// Short headlines: one word per line; longer ones split in two balanced lines.
	const lines = words.length <= 3 ? words : [words.slice(0, Math.ceil(words.length / 2)).join(' '), words.slice(Math.ceil(words.length / 2)).join(' ')];
	const align = layout === 'left' ? 'flex-start' : layout === 'right' ? 'flex-end' : 'center';
	const shade =
		layout === 'left'
			? 'linear-gradient(90deg, rgba(8,10,18,0.88) 0%, rgba(8,10,18,0.55) 45%, rgba(8,10,18,0) 80%)'
			: layout === 'right'
				? 'linear-gradient(270deg, rgba(8,10,18,0.88) 0%, rgba(8,10,18,0.55) 45%, rgba(8,10,18,0) 80%)'
				: 'linear-gradient(180deg, rgba(8,10,18,0.35) 0%, rgba(8,10,18,0.7) 100%)';
	return (
		<AbsoluteFill style={{backgroundColor: colors.bg}}>
			<Img src={staticFile(`media/${background}`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
			<AbsoluteFill style={{background: shade}} />
			<AbsoluteFill style={{justifyContent: 'center', alignItems: align, padding: '0 70px'}}>
				<div style={{textAlign: layout === 'center' ? 'center' : layout}}>
					{lines.map((line, i) => (
						<div
							key={i}
							style={{
								fontFamily: display,
								fontSize: lines.length > 2 ? 190 : 230,
								lineHeight: 0.92,
								letterSpacing: 4,
								color: i === lines.length - 1 ? colors.accent : colors.text,
								textShadow: SHADOW,
							}}
						>
							{line}
						</div>
					))}
					<div style={{height: 10, marginTop: 22, width: 380, backgroundColor: colors.accent, marginLeft: layout === 'left' ? 0 : 'auto', marginRight: layout === 'right' ? 0 : layout === 'center' ? 'auto' : 0}} />
				</div>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};
