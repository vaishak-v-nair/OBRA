"""HUMAN-AUTHORED deterministic test data only. Never a runtime model fallback."""

from orba.architect_schemas import ArchitectureDocument


def controlled_document():
    """An explicitly controlled provider response for application behavior tests."""
    return ArchitectureDocument.model_validate(
        {
            "schema_version": 1,
            "overview": {
                "title": "Habit journal — controlled test proposal",
                "summary": "A single-user daily journal.",
                "architectural_style": "Modular monolith",
                "design_goals": ["Persist dated check-ins"],
                "constraints": ["Local first release"],
                "assumptions": ["One user"],
                "non_goals": ["Social sharing"],
            },
            "technologies": [
                {
                    "technology": "PostgreSQL",
                    "responsibility": "Store check-ins",
                    "reason": "Unique daily records",
                    "alternatives": ["Embedded storage"],
                    "tradeoffs": ["Requires a database service"],
                    "constraints": [],
                    "basis": "recommendation",
                }
            ],
            "components": [
                {
                    "key": "journal",
                    "name": "Journal service",
                    "responsibility": "Validate and save daily entries",
                    "inputs": ["Date and completion state"],
                    "outputs": ["Saved check-in"],
                    "dependencies": [],
                    "story_refs": ["story_checkin"],
                    "security_considerations": ["Enforce user ownership"],
                }
            ],
            "database_design": {
                "notes": "Proposed logical storage; not an applied migration.",
                "entities": [
                    {
                        "key": "checkin",
                        "name": "Check-in",
                        "fields": [
                            {"name": "day", "logical_type": "date", "constraints": ["Required"]}
                        ],
                        "constraints": ["Unique day per owner"],
                        "indexes": ["Owner and day"],
                        "data_ownership": "Local user",
                        "privacy_considerations": ["Private habit history"],
                    }
                ],
                "relationships": [],
            },
            "api_design": {
                "notes": "Proposed API; no endpoint has been implemented by this agent.",
                "endpoints": [
                    {
                        "key": "save_checkin",
                        "status": "proposed",
                        "method": "POST",
                        "route": "/checkins",
                        "purpose": "Save a daily check-in",
                        "request_contract": "Date and completion boolean",
                        "response_contract": "Saved date and completion state",
                        "authentication": "Local authenticated user",
                        "authorization": "Only the owning user",
                        "error_behavior": ["Reject invalid dates"],
                    }
                ],
            },
            "security": {
                "trust_boundaries": ["Browser to authenticated API"],
                "authentication_assumptions": "Existing user session",
                "authorization_model": "User-owned records",
                "sensitive_data": ["Habit history"],
                "external_integrations": [],
                "secret_management": "Server-only environment configuration",
                "threats": [
                    {
                        "threat": "Unauthorized read",
                        "mitigation": "Check ownership on every request",
                    }
                ],
            },
            "deployment": {
                "topology": "One local application and PostgreSQL",
                "infrastructure_requirements": ["Local database"],
                "operational_considerations": ["Back up personal records"],
                "uncertain_choices": ["Hosted deployment is undecided"],
            },
            "risks": ["Date boundaries require user confirmation"],
            "open_decisions": [],
            "tasks": [
                {
                    "key": "storage",
                    "title": "Persist daily check-ins",
                    "description": "Add a dated check-in record.",
                    "scope": "Storage and validation",
                    "deliverables": ["Persistence operation"],
                    "acceptance_criteria": [
                        "Given an incomplete day, when saved, then the check-in remains complete after reload."
                    ],
                    "priority": "P1",
                    "category": "backend",
                    "complexity_estimate": "small",
                    "planning_state": "proposed",
                    "story_refs": ["story_checkin"],
                    "requirement_refs": ["fr_checkin"],
                    "criterion_refs": ["criterion_checkin"],
                    "component_refs": ["journal"],
                    "dependencies": [],
                },
                {
                    "key": "screen",
                    "title": "Display saved check-ins",
                    "description": "Show saved state after reload.",
                    "scope": "Daily journal UI",
                    "deliverables": ["Check-in form"],
                    "acceptance_criteria": ["Reload displays the saved completion state."],
                    "priority": "P1",
                    "category": "frontend",
                    "complexity_estimate": "small",
                    "planning_state": "proposed",
                    "story_refs": ["story_checkin"],
                    "requirement_refs": ["fr_checkin"],
                    "criterion_refs": ["criterion_checkin"],
                    "component_refs": ["journal"],
                    "dependencies": ["storage"],
                },
            ],
            "coverage_exceptions": [],
        }
    )
