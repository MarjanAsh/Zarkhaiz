# Zarkhaiz 3D mascot

Request: a 3D mascot of Muhammad Zarkhaiz Ashar (instagram.com/zarkhaizofficial), head to toe,
formal and simple: dress pants, dress shirt, black coat. Same face and body as him,
full expressions, 3-4 angles, 3-4 suits.

## Identity lock (every image)
South Asian man, fair-wheatish skin, thick voluminous jet-black hair swept up and back,
thick dark eyebrows, full neatly groomed black beard and moustache, thin clear/silver
rectangular-round glasses, round full face, broad slightly heavy build, average height.
Do not slim him down or make him look younger.

## Style
High-end 3D animated feature-film character, soft skin shading, detailed fabric,
studio lighting, plain soft grey background with a light floor shadow, full body, nothing cropped.

## Set
1. Base: Suit A, front, relaxed confident smile (approve first)
2. Suits (front, full body)
   - A Classic: black two-piece, white shirt, slim black tie, black oxfords
   - B Three-piece: black suit + waistcoat, white shirt, silver-grey tie, white pocket square
   - C Tuxedo: satin peak lapels, black bow tie, patent shoes
   - D Smart open-collar: black blazer, light sky-blue shirt, no tie, charcoal pants, loafers
3. Angles (Suit A): front, 3/4 left, side profile, back
4. Expressions: warm smile, big laugh, confident smirk, thinking (hand on beard), surprised, wink
   Poses: thumbs up, arms crossed, waving hello

## Reference photos (from his public Instagram, imported to Canva)
| Canva media id | Photo |
|---|---|
| MAHaQphas6M | front portrait (B/W, HD) |
| MAHaQutzJOE | full body (HD) |
| MAHaQp0kA6g | 3/4 left |
| MAHaQnwk_O0 | front with glasses |
| MAHaQnRwRsI | front selfie |
| MAHaQguyAjA | front, looking up |

## Tools
- fal (nano-banana edit): blocked, connected account has no credits
- Hugging Face ZeroGPU (FLUX Kontext): daily free quota used up
- Canva generate-image with the 6 reference photos: used for this set

Previews are versioned `_v001`, `_v002`... in `preview/`.

## Results (final, consistent set)
Every image uses one master character (base v003), so the face, hair, glasses, beard,
body proportions and outfit (black suit, white shirt, black tie) match across the set.
Full-size files are in Canva (open the link, then Share > Download). The PNGs in `preview/`
are small previews only: this cloud session cannot download from Canva's export host.

| Image | Size | Canva |
|---|---|---|
| Base / master, front, classic black suit (v003) | 944x1680 | https://www.canva.com/M/MAHaQsk-h78 |
| Four suits (v004) | 1680x944 | https://www.canva.com/M/MAHaQ1SmN2s |
| Four angles: front, 3/4, side, back (v005) | 1680x944 | https://www.canva.com/M/MAHaQx5F8PY |
| Six expressions (v003) | 1536x1024 | https://www.canva.com/M/MAHaQokMF_U |
| Three poses: thumbs up, arms crossed, waving (v003) | 1680x944 | https://www.canva.com/M/MAHaQofIQBQ |

Deck with everything ("Zarkhaiz Mascot", 11 pages; pages 7-11 are each image at full size):
https://www.canva.com/design/DAHaQrkD2Vs/edit

### How consistency was kept
1. Master: base v003 was generated from the four-suit lineup so it copies that character exactly.
2. Expressions and poses were generated from the master plus the suit lineup.
3. Suits v004 and angles v005 were regenerated from the master plus the poses/expressions,
   with the hair fixed as straight and swept up (earlier versions came out curly).
For any new image, use the master (MAHaQsk-h78) plus suits v004 as references.

### Older versions (not consistent with each other, kept for reference)
- v002: base MAHaQuMCk_8, suits MAHaQt5CMQg, angles MAHaQlX5tVQ, expressions MAHaQpusyvM,
  poses MAHaQsCxT7M (black shirt, no tie). Previews in `preview/v002/`.
- v003 angles: MAHaQsVwbbY; v004 angles: MAHaQ84tQU4 (curly hair).
- v001 (photo-realistic): base MAHaQj5ke-k, suits MAHaQszrDUw, angles MAHaQvBnCwo,
  expressions MAHaQoyoSa0, first all-in-one sheet MAHaQmsHZU4.
