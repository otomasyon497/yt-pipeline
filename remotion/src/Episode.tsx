import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {Captions} from './components/Captions';
import {ChapterTag} from './components/ChapterTag';
import {Locator} from './components/Locator';
import {OnScreenText} from './components/OnScreenText';
import {QuestionCard} from './components/QuestionCard';
import {setFrame} from './map/geometry';
import {MapBlock} from './map/MapBlock';
import {ChapterCard} from './scenes/ChapterCard';
import {ChartScene} from './scenes/ChartScene';
import {DocumentScene} from './scenes/DocumentScene';
import {ImageScene} from './scenes/ImageScene';
import {PhotoScene} from './scenes/PhotoScene';
import {QuoteScene} from './scenes/QuoteScene';
import {StatScene} from './scenes/StatScene';
import {StockScene} from './scenes/StockScene';
import {TitleCard} from './scenes/TitleCard';
import {colors, easeOut} from './theme';
import type {ShotData, Timeline} from './types';

const ShotBody: React.FC<{shot: ShotData}> = ({shot}) => {
	switch (shot.visual) {
		case 'stock':
		case 'film': // archival film: a pre-trimmed clip like stock
			return <StockScene scene={shot} />;
		case 'ai_image':
			return <ImageScene scene={shot} />;
		case 'photo':
			return <PhotoScene scene={shot} />;
		case 'chart':
			return <ChartScene chart={shot.chart!} />;
		case 'map':
			return <MapBlock file={shot.media!} />;
		case 'title_card':
			return <TitleCard scene={shot} />;
		case 'quote':
			return <QuoteScene scene={shot} />;
		case 'chapter_card':
			return <ChapterCard shot={shot} />;
		case 'stat':
			return <StatScene stat={shot.stat!} />;
		case 'document':
			return <DocumentScene doc={shot.document!} />;
	}
};

// One grade for all footage of an episode (stock, archive, AI) so mixed sources read as one film.
const LOOKS: Record<string, string> = {
	warm: 'contrast(1.07) saturate(0.86) sepia(0.14) brightness(0.96)',
	cool: 'contrast(1.06) saturate(0.84) hue-rotate(-8deg) brightness(0.96)',
};
const FOOTAGE = new Set(['stock', 'film', 'photo', 'ai_image']);

// Every shot after the first appears over the previous one, which stays drawn for exactly that long
// (see timeline.py). Chapter cards punch in (scale down into place); everything else dissolves.
const ShotFrame: React.FC<{shot: ShotData; index: number; look: string}> = ({shot, index, look}) => {
	const frame = useCurrentFrame();
	const tin = Math.max(1, shot.transitionIn);
	const p = index === 0 ? 1 : Math.min(frame / tin, 1);
	const scale = shot.visual === 'chapter_card' && index > 0 ? 1.14 - 0.14 * easeOut(p) : 1;
	return (
		<AbsoluteFill style={{opacity: p, transform: scale !== 1 ? `scale(${scale})` : undefined, backgroundColor: colors.bg}}>
			{FOOTAGE.has(shot.visual) && LOOKS[look] ? (
				<AbsoluteFill style={{filter: LOOKS[look]}}>
					<ShotBody shot={shot} />
					<AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 58%, rgba(0,0,0,0.42) 100%)'}} />
				</AbsoluteFill>
			) : (
				<ShotBody shot={shot} />
			)}
			{shot.where ? <Locator src={shot.where.src} label={shot.where.label} delay={tin + 8} until={shot.durationFrames - 6} /> : null}
			{shot.texts.map((t, k) => {
				if (t.kind === 'question') {
					return (
						<Sequence key={k} from={t.from} layout="none">
							<QuestionCard text={t.text} hold={t.hold ?? 120} />
						</Sequence>
					);
				}
				if (t.kind === 'chapter') {
					return (
						<Sequence key={k} from={t.from} layout="none">
							<ChapterTag text={t.text} hold={t.hold ?? 84} />
						</Sequence>
					);
				}
				const next = shot.texts.slice(k + 1).find((x) => x.kind !== 'question' && x.kind !== 'chapter');
				const hold = Math.min(96, (next ? next.from : shot.durationFrames) - t.from - 14);
				return hold > 20 ? (
					<Sequence key={k} from={t.from} layout="none">
						<OnScreenText text={t.text} countUp={t.countUp} delay={0} hold={hold} instant={t.instant} />
					</Sequence>
				) : null;
			})}
		</AbsoluteFill>
	);
};

export const Episode: React.FC<Timeline> = ({shots, words, showCaptions, look, width, height, uiScale}) => {
	setFrame(width, height, uiScale ?? 1); // before any map draws (see map/geometry.ts)
	return (
		<AbsoluteFill style={{backgroundColor: colors.bg}}>
			{shots.map((shot, i) => (
				<Sequence key={shot.id} from={shot.startFrame} durationInFrames={shot.durationFrames} layout="none">
					<ShotFrame shot={shot} index={i} look={look ?? 'none'} />
				</Sequence>
			))}
			{showCaptions ? <Captions words={words} /> : null}
		</AbsoluteFill>
	);
};
