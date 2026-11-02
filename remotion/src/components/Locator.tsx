import React from 'react';
import {Img, staticFile, useCurrentFrame} from 'remotion';
import {body, colors, easeOut} from '../theme';

// "Where are we": a small mini map (drawn by pipeline/locator.py) in the top-right corner of stock / photo shots.
export const Locator: React.FC<{src: string; label: string; delay: number; until: number}> = ({src, label, delay, until}) => {
	const frame = useCurrentFrame();
	const pIn = easeOut((frame - delay) / 14);
	const pOut = easeOut((until - frame) / 12);
	const p = Math.min(pIn, pOut);
	if (p <= 0) return null;
	return (
		<div
			style={{
				position: 'absolute',
				top: 46,
				right: 46,
				width: 330,
				opacity: p,
				transform: `translateY(${(1 - pIn) * -16}px)`,
				filter: 'drop-shadow(0 10px 24px rgba(0,0,0,0.55))',
			}}
		>
			<Img src={staticFile(`media/${src}`)} style={{width: 330, height: 220, display: 'block'}} />
			{label ? (
				<div
					style={{
						marginTop: 10,
						display: 'inline-block',
						padding: '6px 14px',
						borderLeft: `5px solid ${colors.accent}`,
						background: 'rgba(11, 15, 26, 0.78)',
						color: colors.text,
						fontFamily: body,
						fontWeight: 700,
						fontSize: 24,
						letterSpacing: 4,
						textTransform: 'uppercase',
					}}
				>
					{label}
				</div>
			) : null}
		</div>
	);
};
