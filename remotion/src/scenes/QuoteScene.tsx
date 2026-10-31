import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {body, clamp01, colors, display, easeOut} from '../theme';
import type {ShotData} from '../types';

export const QuoteScene: React.FC<{scene: ShotData}> = ({scene}) => {
	const frame = useCurrentFrame();
	const words = (scene.quote ?? '').split(' ');
	const markP = easeOut((frame - 4) / 18);
	const authorP = easeOut((frame - Math.min(80, Math.floor(scene.durationFrames * 0.45))) / 18);
	return (
		<AbsoluteFill style={{backgroundColor: colors.bg, justifyContent: 'center', alignItems: 'center'}}>
			<div style={{width: 1400, textAlign: 'left', position: 'relative'}}>
				<div style={{fontFamily: display, fontSize: 340, color: colors.accent, lineHeight: 0.8, opacity: markP, height: 170}}>“</div>
				<div style={{fontFamily: body, fontWeight: 700, fontSize: 68, lineHeight: 1.3, color: colors.text}}>
					{words.map((w, i) => (
						// Each word fades in 4 frames after the previous one, starting once the dissolve is over.
						<span key={i} style={{opacity: clamp01((frame - 14 - i * 4) / 8), marginRight: 18, display: 'inline-block'}}>
							{w}
						</span>
					))}
				</div>
				{scene.author ? (
					<div style={{marginTop: 44, fontFamily: body, fontWeight: 500, fontSize: 42, color: colors.accent, opacity: authorP, letterSpacing: 2}}>
						— {scene.author}
					</div>
				) : null}
			</div>
		</AbsoluteFill>
	);
};
