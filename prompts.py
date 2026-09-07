
def sections_text(sections):
    return "\n".join(f"- {item}" for item in sections)


def planning_prompt(context):
    return f'''
You are the PLANNING AGENT in a multi-stage AI study-pack workflow.

Do NOT write the final study pack yet.

STUDENT CONTEXT
Topic: {context['topic']}
Level: {context['level']}
Language: {context['language']}
Learning Duration: {context['learning_duration']}
Include Quiz: {context['include_quiz']}
Quiz Questions: {context['quiz_questions']}
Learning Goal: {context['goal']}
Preferences: {context['preferences']}

Requested Sections:
{sections_text(context['sections'])}

Create a clear study-pack plan containing:
1. Learning objectives
2. Logical teaching order
3. Key concepts that must be covered
4. Appropriate depth for the selected level
5. Assessment strategy
6. Common mistakes or misconceptions
7. Instructions for the content-generation stage

Adjust the amount and depth of the study material so it can realistically
be completed within the selected learning duration.

If Include Quiz is True, plan a quiz with exactly the requested number
of questions.

If Include Quiz is False, do not plan a quiz.

Keep the plan practical and concise.
'''
    
def generation_prompt(context, plan):
    return f'''
You are the CONTENT GENERATION AGENT.

Create the FIRST COMPLETE DRAFT of a personalized study pack.

STUDENT CONTEXT
Topic: {context['topic']}
Level: {context['level']}
Language: {context['language']}
Learning Duration: {context['learning_duration']}
Include Quiz: {context['include_quiz']}
Quiz Questions: {context['quiz_questions']}
Learning Goal: {context['goal']}
Preferences: {context['preferences']}

Requested Sections:
{sections_text(context['sections'])}

PLANNING OUTPUT
---------------
{plan}
---------------

RULES
- Follow the planner's structure.
- Match the selected learner level.
- Write in the selected language.
- Use clear Markdown headings.
- Explain concepts before testing them.
- Avoid unnecessary repetition.
- For MCQs, provide four options and clearly show the correct answer.
- For flashcards, use Question -> Answer format.
- For worked examples, explain the steps clearly.

- Adjust the amount of content according to the selected learning duration.
- If Include Quiz is True, include exactly the requested number of quiz
questions.
- If Include Quiz is False, do not include a quiz section.

Return only the complete first draft.
'''

def assessment_prompt(context, plan, draft):
    return f'''
You are the ASSESSMENT AGENT.

Do NOT rewrite the whole study pack.

STUDENT CONTEXT
Topic: {context['topic']}
Level: {context['level']}
Language: {context['language']}
Learning Duration: {context['learning_duration']}
Include Quiz: {context['include_quiz']}
Quiz Questions: {context['quiz_questions']}
Learning Goal: {context['goal']}

Requested Sections:
{sections_text(context['sections'])}

PLAN
----
{plan}
----

DRAFT
-----
{draft}
-----

Evaluate the draft for:
- Coverage
- Accuracy and conceptual consistency
- Clarity
- Level appropriateness
- Structure
- Usefulness for revision
- Quality of questions and flashcards
- Compliance with requested sections and language
- Whether the content fits the selected learning duration
- Whether the quiz settings were followed correctly

Return:
1. Score out of 100
2. Strong areas
3. Weak or missing areas
4. Specific corrections needed
5. PASS or NEEDS REFINEMENT
'''

def review_prompt(context, draft, assessment):
    return f'''
You are the REVIEW AGENT.

Do NOT rewrite the full study pack.

TOPIC: {context['topic']}
LEVEL: {context['level']}
Learning Duration: {context['learning_duration']}
Include Quiz: {context['include_quiz']}
Quiz Questions: {context['quiz_questions']}
PREFERENCES: {context['preferences']}

DRAFT
-----
{draft}
-----

ASSESSMENT
----------
{assessment}
----------

Create an actionable editorial review containing:
1. What should be preserved
2. What should be corrected
3. What should be added
4. What should be simplified or clarified
5. What should be removed
6. How assessment questions or flashcards should improve
7. A prioritized refinement checklist

Check whether the study pack length matches the selected learning duration.

If a quiz is requested, verify that the quiz contains the correct number
of questions.

If a quiz is not requested, make sure no quiz is included.
'''

def refinement_prompt(context, plan, draft, assessment, review):
    return f'''
You are the FINAL REFINEMENT AGENT.

Produce the FINAL POLISHED STUDY PACK.

STUDENT CONTEXT
Topic: {context['topic']}
Level: {context['level']}
Language: {context['language']}
Learning Duration: {context['learning_duration']}
Include Quiz: {context['include_quiz']}
Quiz Questions: {context['quiz_questions']}
Learning Goal: {context['goal']}
Preferences: {context['preferences']}

Requested Sections:
{sections_text(context['sections'])}

PLAN
----
{plan}
----

FIRST DRAFT
-----------
{draft}
-----------

ASSESSMENT
----------
{assessment}
----------

REVIEW
------
{review}
------

FINAL RULES
- Fix the weaknesses identified by the assessor and reviewer.
- Preserve strong content.
- Include every requested section.
- Match the learner level and selected language.
- Keep the final result self-contained.
- Use clean Markdown headings.
- Remove workflow commentary and internal notes.
- Do not mention agents, prompts, assessment scores, drafts, or refinement.

- Keep the final study pack appropriate for the selected learning duration.
- If Include Quiz is True, include exactly the requested number of quiz
questions.
- If Include Quiz is False, do not include a quiz.

Return only the final polished study pack.
'''
