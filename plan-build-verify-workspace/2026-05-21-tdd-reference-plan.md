# TDD Reference Cleanup Plan
## Recommendation
Reference only `/tdd` as the TDD workflow for `plan-build-verify`.

Why:

- `/Users/gannonhall/skiller/tdd/SKILL.md` is shorter and better suited for composition.
  
- It uses progressive disclosure through focused reference files: `tests.md`, `mocking.md`, `interface-design.md`, `deep-modules.md`, and `refactoring.md`.
  
- It emphasizes behavior through public interfaces, vertical slices, and tracer bullets, which fits the Plan → Build → Verify model.
  
- It keeps `plan-build-verify` focused on orchestration instead of duplicating testing doctrine.
  

`/Users/gannonhall/skiller/test-driven-development/SKILL.md` is stronger as a strict enforcement document, but it is too self-contained and duplicative for this skill. We should not reference it from `plan-build-verify`.
## Proposed changes
1. Update `plan-build-verify/references/build.md`
  
  - Replace local TDD guidance with an instruction to use `/tdd` for implementation tasks.
    
  - Remove fallback wording for `test-driven-development`.
    
  - Keep Build focused on orchestration, task dispatch, review gates, and phase handoff.
    
2. Normalize Build into step-by-step Markdown
  
  - Reduce reliance on the large process diagram.
    
  - Convert the core flow into numbered Markdown steps an agent can follow directly.
    
  - Keep the diagram only if it remains useful as a secondary overview, or remove it if the numbered workflow fully replaces it.
    
  - Make the per-task loop explicit: preflight, implementer dispatch, spec review, quality review, fixes, task completion.
    
3. Update `plan-build-verify/references/implementer-prompt.md`
  
  - Tell implementer subagents to use `/tdd` before writing implementation code.
    
  - Remove duplicated TDD process details if present.
    
4. Remove embedded testing references from `plan-build-verify`
  
  - Delete `plan-build-verify/references/test-driven-development.md`.
    
  - Delete `plan-build-verify/references/testing-anti-patterns.md`.
    
  - Update all internal references that pointed to those files.
    
5. Add a short dependency note
  
  - In `plan-build-verify/references/build.md`, state that Build expects `/tdd` to be available for implementation tasks.
    
  - If `/tdd` is unavailable, stop and alert the user rather than substituting another TDD workflow.
    
6. Update evals later
  
  - Add a Build eval that checks the skill delegates TDD to `/tdd` instead of embedding test instructions.
    
  - Add a regression check that no local `test-driven-development.md` or `testing-anti-patterns.md` files are required by `plan-build-verify`.
    
  - Add a Build eval that checks the workflow is expressed as step-by-step Markdown, not primarily as a diagram.
    
## Approval question
{==Approve this revised change plan?  
  
==}{>>yes, but I wanted a plan with ALL of the chnages not just TDD<<}{id="c1" by="user" at="2026-05-21T17:56:46.833Z"}
