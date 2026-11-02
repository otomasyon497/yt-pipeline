import React, {useMemo} from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {body, colors} from '../theme';
import type {Word} from '../types';

type Chunk = {words: Word[]; start: number; end: number};

// Short on-screen phrases: at most `max` words, break after punctuation, never across paragraphs.
const chunkWords = (words: Word[], max: number): Chunk[] => {
	const chunks: Chunk[] = [];
	let cur: Word[] = [];
	const flush = () => {
		if (cur.length) chunks.push({words: cur, start: cur[0].start, end: cur[cur.length - 1].end});
		cur = [];
	};
	for (const w of words) {
		if (cur.length && w.p !== cur[0].p) flush();
		cur.push(w);
		if (cur.length >= max || (cur.length >= Math.min(3, max - 2) && /[.,;:!?]$/.test(w.text))) flush();
	}
	flush();
	return chunks;
};

// Global overlay (absolute frames). A phrase stays until the next one starts, or briefly after its last word.
// Shorts (vertical): fewer, bigger words, above YouTube's title and buttons at the bottom of the phone screen.
export const Captions: React.FC<{words: Word[]}> = ({words}) => {
	const frame = useCurrentFrame();
	const {width, height} = useVideoConfig();
	const vertical = height > width;
	const chunks = useMemo(() => chunkWords(words, vertical ? 4 : 6), [words, vertical]);
	const idx = chunks.findIndex((c, i) => {
		const next = chunks[i + 1];
		const until = next && next.words[0].p === c.words[0].p ? next.start : c.end + 8;
		return frame >= c.start && frame < until;
	});
	if (idx < 0) return null;
	const chunk = chunks[idx];
	return (
		<AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: vertical ? 520 : 64}}>
			<div
				style={{
					backgroundColor: 'rgba(8,10,18,0.66)',
					borderRadius: 12,
					padding: vertical ? '12px 26px' : '10px 28px',
					fontFamily: body,
					fontWeight: 700,
					fontSize: vertical ? 64 : 50,
					lineHeight: 1.2,
					maxWidth: vertical ? 900 : 1500,
					textAlign: 'center',
				}}
			>
				{chunk.words.map((w, i) => {
					const active = frame >= w.start && frame < w.end;
					const spoken = frame >= w.end;
					return (
						<span
							key={i}
							style={{
								color: active ? colors.accent : spoken ? colors.text : 'rgba(244,241,234,0.62)',
								marginRight: i < chunk.words.length - 1 ? 12 : 0,
							}}
						>
							{w.text}
						</span>
					);
				})}
			</div>
		</AbsoluteFill>
	);
};
