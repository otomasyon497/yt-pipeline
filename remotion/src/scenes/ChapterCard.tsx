import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {body, colors, display, easeOut} from '../theme';
import type {ShotData} from '../types';

// Bebas Neue is condensed (~0.45 em per glyph): shrink long titles so they stay on one line.
export const fitSize = (text: string, max: number, min = 90) => Math.max(min, Math.min(max, 1650 / Math.max(1, text.length * 0.47)));

export const ChapterCard: React.FC<{shot: ShotData}> = ({shot}) => {
	const frame = useCurrentFrame();
	const title = (shot.onScreenText ?? '').toUpperCase();
	const labelP = easeOut((frame - 4) / 16);
	const titleP = easeOut((frame - 10) / 22);
	const lineP = easeOut((frame - 18) / 24);
	return (
		<AbsoluteFill style={{backgroundColor: colors.bg, justifyContent: 'center', alignItems: 'center'}}>
			<div style={{textAlign: 'center'}}>
				<div style={{fontFamily: body, fontWeight: 700, fontSize: 38, letterSpacing: 12, color: colors.accent, opacity: labelP}}>
					CHAPTER {shot.chapterNumber}
				</div>
				<div
					style={{
						fontFamily: display,
						fontSize: fitSize(title, 200),
						color: colors.text,
						lineHeight: 1,
						marginTop: 18,
						letterSpacing: 4,
						opacity: titleP,
						transform: `translateY(${(1 - titleP) * 40}px)`,
					}}
				>
					{title}
				</div>
				<div style={{height: 6, width: 480 * lineP, backgroundColor: colors.accent, margin: '28px auto 0'}} />
			</div>
		</AbsoluteFill>
	);
};
