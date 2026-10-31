import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import type {ShotData} from '../types';

// Ken Burns: slow zoom + drift over the whole scene.
export const ImageScene: React.FC<{scene: ShotData}> = ({scene}) => {
	const frame = useCurrentFrame();
	const k = scene.kenBurns;
	const t = interpolate(frame, [0, scene.durationFrames], [0, 1], {easing: Easing.inOut(Easing.quad), extrapolateRight: 'clamp'});
	const z = k.z0 + (k.z1 - k.z0) * t;
	const x = k.x0 + (k.x1 - k.x0) * t;
	const y = k.y0 + (k.y1 - k.y0) * t;
	return (
		<AbsoluteFill style={{backgroundColor: '#000', overflow: 'hidden'}}>
			<Img
				src={staticFile(`media/${scene.media}`)}
				style={{width: '100%', height: '100%', objectFit: 'cover', transform: `translate(${x}%, ${y}%) scale(${z})`}}
			/>
			<AbsoluteFill style={{backgroundColor: 'rgba(0,0,0,0.15)'}} />
		</AbsoluteFill>
	);
};
