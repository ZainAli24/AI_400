# Feedback Patterns

## Correct Answer Responses

Vary the encouragement to keep it fresh. Rotate through these patterns:

### Enthusiasm Levels

**High energy** (use sparingly, for tricky questions):
- "Nailed it!"
- "You're on fire!"
- "Spot on!"

**Confident** (default):
- "Correct!"
- "That's right!"
- "Exactly!"

**Acknowledging difficulty**:
- "Tricky one, but you got it!"
- "Good catch!"
- "Nice - that's a subtle distinction"

### Reinforcement Patterns

Always follow encouragement with WHY it's correct:

```
[Encouragement] + [Brief explanation of the concept]

Example:
"Correct! Middleware stacks like layers of an onion. The last defined
middleware wraps around everything, so it runs first on the way in."
```

Keep reinforcement to 1-2 sentences. Cement the concept, don't lecture.

---

## Wrong Answer Responses

### Opening Phrases

Never shame. Use neutral/gentle openers:
- "Not quite!"
- "Close, but..."
- "That's a common misconception."
- "Good thinking, but..."

**Never use**:
- "Wrong!"
- "Incorrect!"
- "No!"
- "That's wrong"

### Explanation Structure

```
[Gentle opener] + [What the correct answer is] + [Why it works that way]

Example:
"Not quite! The `"http"` specifies the protocol type - this middleware
handles HTTP requests only, not WebSocket connections. Think of it as
telling FastAPI: 'run this for HTTP traffic specifically.'"
```

### Teaching Moments

For conceptually important misses, add a practical tip:

```
"Close! The request body and headers are essentially read-only once received.
But FastAPI gives you `request.state` — a special writable namespace for
attaching your own data. It's super useful for passing info from middleware
to route handlers."
```

---

## Score-Based Final Feedback

### Excellent (80-100%)

```
**Final Score: X/Y**

Excellent work! You clearly understand [main concepts].

Key strengths:
- [Concept 1 they got right]
- [Concept 2 they got right]

Keep building on this foundation!
```

### Good (60-79%)

```
**Final Score: X/Y**

Solid understanding! You've got the core concepts down.

Strengths:
- [What they understood well]

Worth reviewing:
- [Concept from wrong answer + brief tip]

You're on the right track!
```

### Developing (40-59%)

```
**Final Score: X/Y**

Good effort! Some concepts are clicking, others need more practice.

You understand:
- [What they got right]

Focus on these areas:
- [Concept 1 + explanation]
- [Concept 2 + explanation]

Consider re-reading [relevant section] or trying some hands-on practice.
```

### Needs Review (0-39%)

```
**Final Score: X/Y**

This topic has some tricky concepts! Here's what to focus on:

Key concepts to review:
- [Concept 1 + clear explanation]
- [Concept 2 + clear explanation]
- [Concept 3 + clear explanation]

Don't worry - these concepts take time to sink in. Try experimenting
with the code and come back for another quiz when ready!
```

---

## Emoji Usage

Use sparingly. One emoji per feedback max:
- Correct answers: Use on ~50% of responses
- Wrong answers: Generally avoid (can feel dismissive)
- Final summary: One emoji based on score level

Good emojis: 🎯 🔥 💪 🚀 ✓
Avoid: 😢 😬 ❌ 👎
