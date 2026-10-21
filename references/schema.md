# Study set JSON format

One JSON object. `scripts/build_study_set.py` validates it and fills in missing ids.

```json
{
  "title": "Compound interest basics",
  "topic": "How compound interest works",
  "level": "Beginner",
  "blurb": "One sentence on what the learner will be able to do.",
  "id": "optional-stable-id",
  "sections": [
    {
      "id": "s1",
      "name": "Simple vs compound interest",
      "summary": "One or two sentences on the scope of the section.",
      "points": ["Key point as one clear sentence.", "..."],
      "terms": [{"t": "Principal", "d": "Definition in 25 words or fewer."}]
    }
  ],
  "questions": [
    {
      "id": "optional-stable-id",
      "s": "s1",
      "q": "Question text",
      "o": ["Option A", "Option B", "Option C", "Option D"],
      "a": 1,
      "x": "Two to three sentences: why the answer is right and why the others are not."
    }
  ]
}
```

## Fields and limits

| Field | Required | Limit | Notes |
|---|---|---|---|
| `title` | yes | 70 chars | Shown as the page heading and tab title. |
| `topic` | no | 160 chars | Defaults to `title`. |
| `level` | no | 30 chars | Defaults to `Beginner`. Suggested: Beginner, Intermediate, Advanced. |
| `blurb` | no | 200 chars | One sentence. |
| `id` | no | 80 chars | Progress is saved under this id. Keep it unchanged when extending a set. Auto-generated from the title if omitted. |
| `sections` | yes | 2 or more | Standard is 5, Quick is 3, Deep is 6 to 8. |
| `sections[].id` | no | 20 chars | Defaults to `s1`, `s2`, and so on. |
| `sections[].name` | yes | 60 chars | |
| `sections[].summary` | no | 320 chars | |
| `sections[].points` | yes | 1 to 8 items, 320 chars each | Aim for 4 to 6. |
| `sections[].terms` | no | up to 8 items | Aim for 3 to 5. `t` max 80 chars, `d` max 220. |
| `questions` | yes | 6 or more in total | About 6 per section. |
| `questions[].s` | yes | | A section id, a section name, or a 1-based section number. |
| `questions[].q` | yes | 700 chars | |
| `questions[].o` | yes | 2 to 6 options, 280 chars each | Use 4. No duplicates. |
| `questions[].a` | yes | integer | Zero-based index of the correct option. |
| `questions[].x` | yes | 900 chars | Explanation. |
| `questions[].id` | no | 60 chars | Auto-generated as `<section>-q<n>`. Keep stable when extending. |

## Checks the build script runs

- Fatal: missing title, fewer than 2 sections, a section with no key points, a question that points to an unknown section, a missing or out-of-range answer index, a missing explanation, fewer than 6 questions.
- Warnings: a section with no questions or fewer than 3, duplicate options, "all/none of the above", and a skewed answer position (more than half of four-option questions sharing one position).
