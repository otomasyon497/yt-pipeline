import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import type {ShotData} from '../types';

// Archive photo. Near-16:9 pictures fill the frame with a slow push-in; others (portraits, engravings)
// sit framed over a blurred, darkened copy of themselves, the way documentaries show archive material.
export const PhotoScene: React.FC<{scene: ShotData}> = ({scene}) => {
	const frame = useCurrentFrame();
	const k = scene.kenBurns;
	const t = interpolate(frame, [0, scene.durationFrames], [0, 1], {easing: Easing.inOut(Easing.quad), extrapolateRight: 'clamp'});
	const main = staticFile(`media/${scene.media}`);
	if (scene.photoFit === 'cover') {
		const z = k.z0 + (k.z1 - k.z0) * t;
		return (
			<AbsoluteFill style={{backgroundColor: '#000', overflow: 'hidden'}}>
				<Img src={main} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `translate(${k.x0 + (k.x1 - k.x0) * t}%, ${k.y0 + (k.y1 - k.y0) * t}%) scale(${z})`}} />
				<AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.5) 100%)'}} />
			</AbsoluteFill>
		);
	}
	const zoom = 1 + 0.07 * t;
	return (
		<AbsoluteFill style={{backgroundColor: '#000', overflow: 'hidden'}}>
			<Img src={staticFile(`media/${(scene.media ?? '').replace(/\.jpg$/, '_bg.jpg')}`)} style={{width: '100%', height: '100%', transform: `scale(${1.05 + 0.04 * t})`}} />
			<AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
				<Img
					src={main}
					style={{
						maxWidth: '84%',
						maxHeight: '80%',
						objectFit: 'contain',
						transform: `scale(${zoom})`,
						boxShadow: '0 18px 60px rgba(0,0,0,0.65)',
						border: '6px solid rgba(244,241,234,0.92)',
					}}
				/>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};
