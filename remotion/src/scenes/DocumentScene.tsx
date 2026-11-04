import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {body, clamp01, colors, easeOut, serif} from '../theme';
import type {DocSpec} from '../types';

const MARKER = 'rgba(255, 196, 36, 0.48)';
const INK = '#1b2232';
const PAPER = '#f3eee3';
const PAPER_MUTED = '#7a6f5c';

// Title and source in a dark panel bottom left, above the captions.
const SourcePanel: React.FC<{doc: DocSpec; p: number}> = ({doc, p}) => (
	<div style={{position: 'absolute', left: 104, top: 770, opacity: p, backgroundColor: 'rgba(8,10,18,0.82)', padding: '14px 26px', borderLeft: `8px solid ${colors.accent}`, maxWidth: 1300}}>
		{doc.title ? <div style={{fontFamily: body, fontWeight: 700, fontSize: 32, color: colors.text}}>{doc.title}</div> : null}
		<div style={{fontFamily: body, fontWeight: 500, fontSize: 25, color: colors.muted, marginTop: doc.title ? 4 : 0}}>{doc.source}</div>
	</div>
);

// A public-domain page: the whole sheet first, then the camera closes in on the marked lines and a highlighter
// sweeps them one by one.
const Page: React.FC<{doc: DocSpec}> = ({doc}) => {
	const frame = useCurrentFrame();
	const PW = 960;
	const PH = PW * (doc.aspect ?? 1.294);
	const rects = doc.rects ?? [];
	const s0 = Math.min(1, 900 / PH);
	let fx = PW / 2;
	let fy = PH / 2;
	let s1 = s0;
	if (rects.length) {
		const ux0 = Math.min(...rects.map((r) => r[0])) * PW;
		const uy0 = Math.min(...rects.map((r) => r[1])) * PH;
		const ux1 = Math.max(...rects.map((r) => r[2])) * PW;
		const uy1 = Math.max(...rects.map((r) => r[3])) * PH;
		fx = (ux0 + ux1) / 2;
		fy = (uy0 + uy1) / 2;
		s1 = Math.max(s0, Math.min(3.0, 1150 / Math.max(ux1 - ux0, 1), 420 / Math.max(uy1 - uy0, 1)));
	}
	const z = easeOut((frame - 14) / 40);
	const s = s0 + (s1 - s0) * z;
	const cx = PW / 2 + (fx - PW / 2) * z;
	const cy = PH / 2 + (fy - PH / 2) * z;
	return (
		<AbsoluteFill style={{backgroundColor: colors.bg, overflow: 'hidden'}}>
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, rgba(245,166,35,0.06), transparent 65%)'}} />
			<div
				style={{
					position: 'absolute',
					left: 0,
					top: 0,
					width: PW,
					height: PH,
					transformOrigin: '0 0',
					transform: `translate(${960 - cx * s}px, ${470 - cy * s}px) scale(${s})`,
					boxShadow: '0 30px 80px rgba(0,0,0,0.55)',
					backgroundColor: '#ffffff',
					opacity: clamp01(frame / 8),
				}}
			>
				<Img src={staticFile(`media/${doc.src}`)} style={{width: PW, height: PH, display: 'block'}} />
				{rects.map((r, k) => (
					<div
						key={k}
						style={{
							position: 'absolute',
							left: r[0] * PW - 3,
							top: r[1] * PH - 2,
							width: (r[2] - r[0]) * PW + 6,
							height: (r[3] - r[1]) * PH + 4,
							backgroundColor: MARKER,
							mixBlendMode: 'multiply',
							transformOrigin: 'left center',
							transform: `scaleX(${easeOut((frame - 56 - k * 10) / 12)})`,
						}}
					/>
				))}
			</div>
			{/* The page fills the frame once zoomed: darken its lower part so the source panel and captions sit clear. */}
			<AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,10,18,0) 62%, rgba(8,10,18,0.88) 82%)', opacity: z}} />
			<SourcePanel doc={doc} p={easeOut((frame - 20) / 14)} />
		</AbsoluteFill>
	);
};

// Our own setting of a short quoted line on paper (for sources we may quote but not reproduce), marker over the key part.
const Clipping: React.FC<{doc: DocSpec}> = ({doc}) => {
	const frame = useCurrentFrame();
	const text = doc.text ?? '';
	const hi = doc.highlight && text.includes(doc.highlight) ? doc.highlight : text;
	const at = text.indexOf(hi);
	const mark = easeOut((frame - 30) / 30);
	return (
		// Centre about 580 px down: clear of a question card (top right) and of the captions (below ~880).
		<AbsoluteFill style={{backgroundColor: colors.bg, justifyContent: 'center', alignItems: 'center', paddingTop: 140, paddingBottom: 60}}>
			<div
				style={{
					width: 1360,
					padding: '56px 70px 50px',
					backgroundColor: PAPER,
					backgroundImage: 'radial-gradient(ellipse at 30% 20%, rgba(255,255,255,0.55), rgba(0,0,0,0.05) 80%)',
					boxShadow: '0 30px 80px rgba(0,0,0,0.55)',
					transform: `rotate(-0.6deg) translateY(${(1 - easeOut(frame / 16)) * 40}px)`,
					opacity: clamp01(frame / 8),
				}}
			>
				{doc.title ? (
					<div style={{fontFamily: body, fontWeight: 700, fontSize: 28, letterSpacing: 3, color: PAPER_MUTED, textTransform: 'uppercase', marginBottom: 24}}>{doc.title}</div>
				) : null}
				<div style={{fontFamily: serif, fontWeight: 500, fontSize: 60, lineHeight: 1.36, color: INK}}>
					{text.slice(0, at)}
					<span
						style={{
							backgroundImage: `linear-gradient(${MARKER}, ${MARKER})`,
							backgroundRepeat: 'no-repeat',
							backgroundSize: `${mark * 100}% 100%`,
							WebkitBoxDecorationBreak: 'clone',
							boxDecorationBreak: 'clone',
							padding: '0 4px',
						}}
					>
						{hi}
					</span>
					{text.slice(at + hi.length)}
				</div>
				<div style={{fontFamily: body, fontWeight: 500, fontSize: 26, color: PAPER_MUTED, marginTop: 30}}>{`— ${doc.source}`}</div>
			</div>
		</AbsoluteFill>
	);
};

export const DocumentScene: React.FC<{doc: DocSpec}> = ({doc}) => (doc.src ? <Page doc={doc} /> : <Clipping doc={doc} />);
