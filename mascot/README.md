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

## Office set v2 (used by the reel from v006)
Five full-body images supplied by the client in `office-v2/` (side, back, front smile, explaining with a marker,
surprised with open hands), all in the same framing. `office-v2/cutout/` holds the background-removed versions.
The reel uses only these; the angry and seated poses in `office-v1/` are no longer used.

## Character file (used by the reel from v009)
`character/` holds the client's three pose sheets (`refs/`), 17 cutouts on one shared canvas (`poses/`) and
`CHARACTER.md`, which lists every pose, what it is for and the rules. The office-v1 and office-v2 sets are no
longer used by the reel.

## Asset library (from v011, in progress)
Request (user, 2026-11-13): the v010 puppet rig is smoother but the arms look unnatural and the single front face
and body angle are too stiff. The work is now a video series, so stop rendering and build a reusable asset library
with ChatGPT through the GPT bridge (GPT + Gemini, not Muse, Canva or fal): expressions, head/body angles
(front, 3/4, profile), clean arm/hand pieces, head-less torsos, organized in the repo for assembling any future script.

Everything is in `mascot/library/` (read its README for names, anchors and how a script picks assets).
Identity references for every generation: `rig/source.webp` + `character/refs/sheet1-3.jpg`.

### Generators found in this environment (2026-11-13)
- ChatGPT bridge `https://zarkhaiz.duckdns.org` (token injected by the proxy): `GET /health`; `POST /jobs {"prompt"}`
  → `{"id"}`; `GET /jobs/<id>` → `{status, reply, files}`; `GET /jobs/<id>/files/<name>` downloads an output. It runs
  Codex (ChatGPT plan sign-in) which has an `image_gen` tool; tested OK (1536x1024 PNG). It takes no uploads and its
  shell sandbox fails (bwrap), so reference images are passed as public raw GitHub URLs.
  After a few test jobs it hit the ChatGPT plan usage limit ("try again at 3:16 PM").
- OpenAI API (gpt-image-2 edits with the refs uploaded): `insufficient_quota`, no credits.
- Gemini API: 401. This environment ("AI Tools") stores the Gemini key under the `Authorization` header, but
  the Gemini API needs it in `x-goog-api-key` (as the `zarkhaiz` environment has it). Fix it in the environment's
  network secrets to use Gemini here.

### Status (2026-11-13, later)
Pipeline written and dry-run tested (`library/tools/`): 28 generation jobs (10 head sheets of 6 expressions,
2 body turnaround sheets, 12 acting poses, 2 hand sheets, 1 arm sheet). No library image is generated yet.
- The user fixed the Gemini key header (`x-goog-api-key`): auth works and the image models are listed, but every
  image model answers 429 "free tier limit: 0". Billing must be enabled on the AI Studio key.
- The bridge quota came back (13:39 UTC), but the bridge cannot pass reference images to Codex (Codex cannot
  load URLs; the bridge accepts only `{"prompt"}`), so it would draw the man from text alone and drift.
  The bridge change needed is in `library/README.md` ("Bridge upgrade").
- User decision: providers must fall back automatically when one runs out. `gen.py` now does
  gemini → openai → bridge with saved cool-downs (`library/README.md`, "Providers and automatic fallback").
- The user added a new OpenAI API key (replaced the old one in the "AI Tools" environment, 2026-11-13). Tested twice,
  a minute apart: still `credit_balance_exhausted`, so that OpenAI account has no credits either (check
  platform.openai.com → Settings → Billing). A second ChatGPT account would go on the bridge as a second `CODEX_HOME`.
Next: once any provider has quota with references, run `gen.py`, check every image for face/outfit drift
(regenerate with `--only <job> --redo`), run `post.py`, review the contact sheets, commit.
