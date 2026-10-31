import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {colors, display} from './theme';

export type ThumbProps = {text: string; background: string; layout: 'left' | 'center' | 'right'};

// Stills are rendered once, so gradients/shadows are fine here (unlike in the video compositions).
export const Thumbnail: React.FC<ThumbProps> = ({text, background, layout}) => {
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
								textShadow: '0 6px 24px rgba(0,0,0,0.6)',
							}}
						>
							{line}
						</div>
					))}
					<div style={{height: 10, marginTop: 22, width: 380, backgroundColor: colors.accent, marginLeft: layout === 'center' ? 'auto' : 0, marginRight: layout === 'center' ? 'auto' : 0}} />
				</div>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};
