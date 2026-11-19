import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {AbsoluteFill, Easing, cancelRender, continueRender, delayRender, interpolate, staticFile, useCurrentFrame} from 'remotion';

// A full-frame archive photo with a 2.5D camera move (script.photo_motion = "parallax", 2026-11-19).
// The depth map (Depth Anything V2 Small, white = near) shifts near pixels further than far ones while the camera
// drifts sideways and pushes in. Backward mapping on the CPU into a 2D canvas, like the globe (no WebGL in the
// headless renderer): every output pixel looks up where it came from, refined once by the depth found there.

type Pixels = {data: Uint8ClampedArray; w: number; h: number};
const cache = new Map<string, Pixels>();

const usePixels = (src: string): Pixels | null => {
	const [px, setPx] = useState<Pixels | null>(cache.get(src) ?? null);
	const [handle] = useState(() => (cache.has(src) ? null : delayRender(`parallax ${src}`)));
	useEffect(() => {
		if (px || handle === null) return;
		const img = new Image();
		img.crossOrigin = 'anonymous';
		img.onload = () => {
			const c = document.createElement('canvas');
			c.width = img.naturalWidth;
			c.height = img.naturalHeight;
			const ctx = c.getContext('2d', {willReadFrequently: true});
			if (!ctx) return cancelRender(new Error('no 2d context for a parallax photo'));
			ctx.drawImage(img, 0, 0);
			const p = {data: ctx.getImageData(0, 0, c.width, c.height).data, w: c.width, h: c.height};
			cache.set(src, p);
			setPx(p);
			continueRender(handle);
		};
		img.onerror = () => cancelRender(new Error(`parallax image failed to load: ${src}`));
		img.src = staticFile(`media/${src}`);
	}, [src, px, handle]);
	return px;
};

const W = 1920;
const H = 1080;
const AMP = 0.022; // sideways travel of the nearest pixels, as a fraction of the frame width

// framed: the photo sits inside the frame at its own aspect (archive prints, portraits), like PhotoScene's contain mode.
export const ParallaxPhoto: React.FC<{media: string; depth: string; durationFrames: number; seed: number; framed?: boolean}> = ({media, depth, durationFrames, seed, framed}) => {
	const frame = useCurrentFrame();
	const img = usePixels(media);
	const dep = usePixels(depth);
	const ref = useRef<HTMLCanvasElement>(null);
	const t = interpolate(frame, [0, durationFrames], [0, 1], {easing: Easing.inOut(Easing.quad), extrapolateRight: 'clamp'});
	const dir = seed % 2 === 0 ? 1 : -1;
	// canvas size: the whole frame, or the photo fitted into 84 % x 80 % of it
	const fit = img ? Math.min((W * 0.84) / img.w, (H * 0.8) / img.h) : 1;
	const CW = framed && img ? Math.round(img.w * fit) : W;
	const CH = framed && img ? Math.round(img.h * fit) : H;
	useLayoutEffect(() => {
		const ctx = ref.current?.getContext('2d');
		if (!ctx || !img || !dep) return;
		const out = ctx.createImageData(CW, CH);
		const o = out.data;
		// cover-fit the photo, then zoom 1.06 -> 1.12 around the centre (headroom for the shift)
		const zoom = framed ? 1.04 + 0.04 * t : 1.06 + 0.06 * t;
		const cover = Math.max(CW / img.w, CH / img.h) * zoom;
		const sx = dir * AMP * (t - 0.5) * 2 * CW; // camera offset in output pixels, -AMP..+AMP
		const sy = -0.35 * AMP * (t - 0.5) * 2 * CH;
		const {data: id, w: iw, h: ih} = img;
		const {data: dd, w: dw, h: dh} = dep;
		const kx = dw / iw;
		const ky = dh / ih;
		for (let y = 0; y < CH; y++) {
			for (let x = 0; x < CW; x++) {
				// source position without parallax
				let u = (x - CW / 2) / cover + iw / 2;
				let v = (y - CH / 2) / cover + ih / 2;
				// depth there, then once more where the shifted ray lands
				let di = Math.min(dh - 1, Math.max(0, (v * ky) | 0)) * dw + Math.min(dw - 1, Math.max(0, (u * kx) | 0));
				let d = dd[di * 4] / 255 - 0.5;
				let uu = u - (sx * d) / cover;
				let vv = v - (sy * d) / cover;
				di = Math.min(dh - 1, Math.max(0, (vv * ky) | 0)) * dw + Math.min(dw - 1, Math.max(0, (uu * kx) | 0));
				d = dd[di * 4] / 255 - 0.5;
				u -= (sx * d) / cover;
				v -= (sy * d) / cover;
				const ix = Math.min(iw - 1, Math.max(0, u | 0));
				const iy = Math.min(ih - 1, Math.max(0, v | 0));
				const si = (iy * iw + ix) * 4;
				const oi = (y * CW + x) * 4;
				o[oi] = id[si];
				o[oi + 1] = id[si + 1];
				o[oi + 2] = id[si + 2];
				o[oi + 3] = 255;
			}
		}
		ctx.putImageData(out, 0, 0);
	}, [img, dep, t, dir, CW, CH]);
	if (framed) {
		return (
			<canvas
				ref={ref}
				width={CW}
				height={CH}
				style={{width: CW, height: CH, boxShadow: '0 18px 60px rgba(0,0,0,0.65)', border: '6px solid rgba(244,241,234,0.92)'}}
			/>
		);
	}
	return (
		<AbsoluteFill style={{backgroundColor: '#000', overflow: 'hidden'}}>
			<canvas ref={ref} width={W} height={H} style={{width: '100%', height: '100%'}} />
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.5) 100%)'}} />
		</AbsoluteFill>
	);
};
