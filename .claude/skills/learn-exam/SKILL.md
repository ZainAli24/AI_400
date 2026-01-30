---
name: learn-exam
description: |
  Interactive quiz generator that tests understanding of code and concepts.
  This skill should be used when users want to test their knowledge after
  learning something new, review code they've written, or practice concepts.
  Reads user's code/context, generates MCQ questions one-by-one, provides
  encouraging feedback, and tracks scores.
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Learn Exam

Generate interactive quizzes to test understanding of code, concepts, or topics.

## What This Skill Does

- Analyzes user's code or specified topic to generate relevant questions
- Presents MCQ questions ONE AT A TIME using AskUserQuestion
- Randomizes correct answer positions (avoid predictable patterns)
- Provides immediate feedback after each answer
- Tracks score and delivers final summary with learning insights

## What This Skill Does NOT Do

- Generate written/essay questions (MCQ only)
- Test unrelated topics (questions must be contextual)
- Skip feedback (every answer gets a response)

---

## Workflow

### Phase 1: Context Gathering

| Source | What to Gather |
|--------|----------------|
| User's code | Read files mentioned or recently discussed |
| Conversation | Topic they just learned, concepts covered |
| User request | Number of questions (default: 5-8, max: 10) |

**Determine quiz focus**: What concept/technology/pattern should questions test?

### Phase 2: Question Generation

Generate questions that test UNDERSTANDING, not memorization:

| Question Type | Tests | Example |
|---------------|-------|---------|
| **Conceptual** | Why something works | "What does `call_next()` do?" |
| **Behavioral** | What happens when... | "If you remove `return response`..." |
| **Order/Flow** | Execution sequence | "What order do middleware run?" |
| **Edge Cases** | Error handling | "If an exception is raised..." |
| **Best Practice** | Correct approach | "Why use `request.state`?" |

### Phase 3: Question Delivery

For EACH question, use AskUserQuestion with these rules:

```
1. Randomize correct answer position (rotate through positions 1-4)
2. Make wrong answers plausible (not obviously wrong)
3. Keep options concise (1-5 words for label)
4. Use description for additional context
5. Wait for answer before proceeding
```

**Question Structure**:
```
header: "Q1", "Q2", etc. (short, ≤12 chars)
question: Clear, specific question ending with "?"
options: 4 choices with label + description
multiSelect: false (single answer)
```

### Phase 4: Feedback Delivery

**After EACH answer**, provide immediate feedback:

| Result | Response Pattern |
|--------|------------------|
| **Correct** | Encouragement + brief reinforcement of why it's right |
| **Wrong** | Gentle correction + clear explanation + the correct concept |

See `references/feedback-patterns.md` for templates.

### Phase 5: Final Summary

After all questions, provide:

```
Score: X/Y

Strengths:
- Concepts they demonstrated understanding of

Areas to Review:
- Concepts from wrong answers (with brief explanations)

Encouragement:
- Positive closing based on performance level
```

---

## Answer Position Randomization

**Critical**: Avoid predictable patterns. Track positions used:

```
Q1: Correct = position 2
Q2: Correct = position 4
Q3: Correct = position 1
Q4: Correct = position 3
Q5: Correct = position 2
...
```

Distribute roughly evenly. Never put correct answer in same position 3+ times in a row.

---

## Difficulty Calibration

| Performance | Adjustment |
|-------------|------------|
| 0-40% correct | Simplify remaining questions, focus on fundamentals |
| 40-70% correct | Maintain current difficulty |
| 70-100% correct | Can increase complexity slightly |

---

## Before Starting Quiz

Confirm with user:
1. Topic/code to quiz on (or infer from context)
2. Number of questions (suggest 5-8 based on topic complexity)
3. Any specific areas they want to focus on

Then proceed question-by-question. Do NOT show all questions at once.
