
import time

from prompts import (
    planning_prompt,
    generation_prompt,
    assessment_prompt,
    review_prompt,
    refinement_prompt,
)


def call_ai(client, model, prompt, stage_name, retries=3):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            text = getattr(response, "text", None)

            if text and text.strip():
                return text.strip(), None

            last_error = "The model returned an empty response."

        except Exception as exc:
            last_error = str(exc)

        if attempt < retries:
            time.sleep(1.5 * attempt)

    return None, f"{stage_name} failed after {retries} attempts: {last_error}"


def run_workflow(client, model, context, progress_callback=None):
    outputs = {}
    errors = []

    def progress(message):
        if progress_callback:
            progress_callback(message)

    progress("1/5 🧭 Planning the study pack...")
    plan, error = call_ai(
        client, model, planning_prompt(context), "Planning stage"
    )

    if error:
        errors.append(error)
        plan = (
            f"Fallback Plan:\n"
            f"- Teach {context['topic']} at {context['level']} level.\n"
            f"- Use {context['language']}.\n"
            f"- Follow foundations -> explanation -> examples -> revision.\n"
            f"- Include all requested sections.\n"
            f"- Focus on the learning goal: {context['goal']}."
        )

    outputs["plan"] = plan

    progress("2/5 ✍️ Generating first draft...")
    draft, error = call_ai(
        client, model, generation_prompt(context, plan),
        "Content generation stage"
    )

    if error:
        errors.append(error)
        outputs["draft"] = None
        return outputs, errors, None

    outputs["draft"] = draft

    progress("3/5 🧪 Assessing quality...")
    assessment, error = call_ai(
        client, model, assessment_prompt(context, plan, draft),
        "Assessment stage"
    )

    if error:
        errors.append(error)
        assessment = (
            "Automated assessment was unavailable. During refinement, "
            "independently check accuracy, coverage, clarity, learner level, "
            "requested sections, language, structure, examples, flashcards, "
            "and question quality."
        )

    outputs["assessment"] = assessment

    progress("4/5 🔎 Reviewing improvements...")
    review, error = call_ai(
        client, model, review_prompt(context, draft, assessment),
        "Review stage"
    )

    if error:
        errors.append(error)
        review = (
            "Perform a general editorial review: correct inaccuracies, "
            "fill missing sections, improve clarity, remove repetition, "
            "verify level appropriateness, and strengthen questions and answers."
        )

    outputs["review"] = review

    progress("5/5 ✨ Refining final study pack...")
    final_pack, error = call_ai(
        client, model,
        refinement_prompt(context, plan, draft, assessment, review),
        "Refinement stage"
    )

    if error:
        errors.append(error)
        final_pack = draft

    outputs["final"] = final_pack
    return outputs, errors, final_pack
