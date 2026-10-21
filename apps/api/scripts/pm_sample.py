"""Explicit HUMAN-AUTHORED TEST FIXTURE. Never a runtime/provider fallback.

Used only by guarded test-data commands and deterministic contract tests.
It is never evidence that a model produced a plan.
"""

from orba.pm_schemas import ProductDocument


def human_document(actor_id, *, blocking_confirmation=False):
    source = {"kind": "human", "actor_id": str(actor_id)}

    def statement(key, text):
        return {"key": key, "text": text, "source": dict(source)}

    return ProductDocument.model_validate(
        {
            "schema_version": 1,
            "product_name": statement("name", "Habit journal — human-authored test fixture"),
            "summary": statement("summary", "Track a personal daily habit."),
            "problem_statement": statement(
                "problem", "A person needs a record of daily check-ins."
            ),
            "proposed_solution": statement("solution", "A dated check-in journal."),
            "target_users": [statement("user", "One person tracking a habit")],
            "user_goals": [statement("goal", "See whether today's habit is complete")],
            "in_scope": [statement("scope", "Daily check-ins")],
            "out_of_scope": [statement("out", "Social sharing")],
            "functional_requirements": [
                statement("fr_checkin", "Record one check-in per local day")
            ],
            "nonfunctional_requirements": [],
            "prerequisites": [],
            "assumptions": [statement("assumption", "A single local user is sufficient initially")],
            "risks": [],
            "open_questions": [],
            "confirmations": [
                {
                    **statement("confirmation_platform", "Confirm the first-release platform."),
                    "blocking": True,
                }
            ]
            if blocking_confirmation
            else [],
            "epics": [
                {
                    "key": "epic_checkin",
                    "title": "Daily journal",
                    "goal": "Record a daily habit",
                    "priority": "P1",
                    "source": dict(source),
                    "stories": [
                        {
                            "key": "story_checkin",
                            "title": "Record today's check-in",
                            "statement": "As a habit tracker, I want to record a daily check-in, so that I can review my progress.",
                            "description": "Keep the saved date and completion state.",
                            "priority": "P1",
                            "source": dict(source),
                            "requirement_refs": ["fr_checkin"],
                            "dependencies": [],
                            "acceptance_criteria": [
                                {
                                    "key": "criterion_checkin",
                                    "given": "Today's habit is incomplete",
                                    "when": "I record today's check-in",
                                    "then": "Today's habit is shown as complete after reload",
                                    "source": dict(source),
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    )
