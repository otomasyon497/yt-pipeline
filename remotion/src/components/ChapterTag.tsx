import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {clamp01, colors, display, easeOut} from '../theme';

// Chapter title over the chapter's first picture (instead of a full-screen chapter card, which stopped the video for
// a second and a half): centred above the captions (the top holds on-screen labels and date tags), an accent line
// draws under it, then it fades. YouTube's chapters come from the
// description's timestamps.
export const ChapterTag: React.FC<{text: string; hold?: number}> = ({text, hold = 84}) => {
	const frame = useCurrentFrame();
	const inP = easeOut(frame / 12);
	const out = clamp01((frame - hold) / 12);
	const opacity = inP * (1 - out);
	if (opacity <= 0) return null;
	return (
		<AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 150}}>
			<div style={{opacity, transform: `translateY(${(1 - inP) * 18}px)`, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
				<div
					style={{
						fontFamily: display,
						fontSize: 58,
						letterSpacing: 3,
						color: colors.text,
						padding: '6px 26px 2px',
						backgroundColor: 'rgba(8,10,18,0.62)',
						textShadow: '0 2px 10px rgba(0,0,0,0.5)',
					}}
				>
					{text}
				</div>
				<div style={{height: 5, width: 120, marginTop: 8, backgroundColor: colors.accent, transform: `scaleX(${easeOut((frame - 6) / 14)})`}} />
			</div>
		</AbsoluteFill>
	);
};
