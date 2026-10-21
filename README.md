# Claude Scholar

Type a topic into Claude and get a study set: section notes, key terms, and a practice quiz in one HTML file.

## What you get

- Notes for each section, with key points and tap-to-reveal terms.
- A readiness score with an 80% target.
- Timed test, weak-spot drill, missed-question retry, and one-section quizzes, each with an explanation after every answer.
- A review of every answer at the end of a session.

The file works offline. Nothing is sent anywhere. Your progress is saved only in the browser you use to open it, so it does not follow you to another device or browser.

## How to use it

1. Add the skill to Claude from your settings (see Anthropic's help center for the steps on your plan), using the zip you were given.
2. Ask Claude something like:
   - "Make me a study set on how vaccines train the immune system"
   - "Help me prepare for the AWS AI Practitioner exam, intermediate level"
   - "Create a quick study set on SQL joins"
3. Open the HTML file Claude gives you in any browser.
4. To grow a set, ask Claude to "add 10 more questions to my compound interest study set" and open the new file. Progress carries over.

## Good to know

- Claude writes the content, so it can contain mistakes. Check anything important against a trusted source, especially for exams, medicine, law, or money.
- This is study material, not professional advice.
- The study set is designed for teens and adults. Review it first if a younger child will use it.
- Clearing your browser data erases your saved progress.

## What is inside the zip

| Path | Purpose |
|---|---|
| `SKILL.md` | The instructions Claude follows |
| `scripts/build_study_set.py` | Checks the content and builds the HTML file (needs Python 3, no extra packages) |
| `assets/study-set-template.html` | The page design |
| `references/schema.md` | The data format |
| `examples/` | A finished sample: `compound-interest.html` |
