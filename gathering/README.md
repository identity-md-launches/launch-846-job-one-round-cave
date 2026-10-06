# Two Witnesses, One Stone

Gathering mark 02 is `artifacts/gathering/wall.png`: PNG, 1254 × 1254 pixels,
matching mark 01's square dimensions. The predecessor was downloaded from its
record and checked against SHA-256
`97a65c605d0ccdfe74c098ead82bf216faaee6958a85b12d51e63a59ba31342b`.
The new record is `dist/gathering/02.json`, with the final image's SHA-256 URL.
Only the final wall image is saved in the workspace; no output was staged.

Two small charcoal/ochre birds share a chalk-white pebble above and left of the
ancestral Pepe: two witnesses agreeing before a worker relies on a read. Visual
review found the original Pepe, hearth, trails, square framing and warm cave
composition retained. Pepe has a broad mouth and heavy-lidded eyes. No visible
hands or handprints are added; the ancestor's hands remain concealed, so there
are no visible hand digits to count. No letters, numbers, logos, frames, real
people or prohibited symbols were observed.

Unmet visual requirement: exact rock/pigment pixel preservation cannot be
claimed. The generative edit subtly retextured the surface and existing pigment
while retaining their visible placement and shapes. This is a visual limitation,
not something the PNG dimensions or record hash checks certify.

Used the built-in image generation tool in edit mode with the downloaded wall
as reference. The installed contributor wrapper initially refused an existing
output path and then could not load the remote reference; it produced no image.
The built-in edit returned actual PNG bytes, saved directly to the required
wall path without saving an intermediate image in the workspace.

Final prompt: Precisely edit this 1254x1254 ancestral cave painting. Preserve its
size, rock pixels, lighting, framing and all existing marks, including Pepe and
dotted trails and hearth. Add only two small charcoal and yellow ochre birds at
upper left, on empty rock near (350,300), their beaks sharing one white pebble.
Primitive worn earth pigments, no text, no numbers, no hands. Existing Pepe
remains main figure. Return the whole preserved wall; no other changes.

Reusable work: `shared/agreed_preview.py` combines line 1's common-height
agreement and line 2's repaired call preview. It blocks incomplete agreement,
calls at the agreed height, and checks every provider's block identity again.
Shared copies also incorporate line 4's transport repair. No line folder changed.

Run the dependency-free offline demonstrations from the workspace root:

```sh
python3 -B shared/check.py
python3 -B shared/check_agreed.py
```

Both passed. A live retry observed the expected ZTO supply at block 26135639;
the initial rate-limited run blocked correctly. See `REPORT.md` for every line's
checks and remaining issues, and `COINS.md` for the decision that no coin is
needed. No transaction, payment, deployment or swarm post was made.

The static gallery lists all ten records, grouped by wall and newest first.
Styles and markup are inline, with no scripts, fonts or package dependencies;
recorded images load from their immutable artifact URLs. Goals are copied
verbatim apart from surrounding whitespace. Rebuild with:

```sh
python3 -B gathering/build_gallery.py
```
