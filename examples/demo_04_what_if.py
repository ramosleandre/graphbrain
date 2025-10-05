"""Demo 4: What-If Analysis - Compare Scenarios"""

from graphbrain.api import GraphbrainAPI

def validate_plan(api, plan_name, actions, user_conditions):
    """Validate a plan and return summary."""
    print(f"\n{'='*60}")
    print(f"SCENARIO: {plan_name}")
    print(f"{'='*60}")

    # Add user conditions
    for condition in user_conditions:
        api.add_user_fact(condition, session_id='what-if-analysis')

    print(f"Patient conditions: {', '.join(user_conditions)}")
    print()

    results = []
    for action in actions:
        result = api.validate_against_rules(
            proposed_edges=action,
            layers=['foundation', 'user']
        )
        results.append((action, result['decision']))

        symbol = "✓" if result['decision'] == "ALLOW" else "✗" if result['decision'] == "DENY" else "?"
        print(f"  {symbol} {action} → {result['decision']}")

        if result['rejected']:
            trace = result['rejected'][0]['why_trace'][0]
            print(f"      Why: {trace['rule']}")

    return results


with GraphbrainAPI('medical_kb.hg') as api:
    # Load foundation
    foundation = [
        {"s": "(contraindicated/P ibuprofen/C diabetes/C)",
         "attrs": {"layer": "foundation", "mandatory": True}},
        {"s": "(contraindicated/P aspirin/C pregnancy/C)",
         "attrs": {"layer": "foundation", "mandatory": True}},
        {"s": "(recommended/P metformin/C diabetes/C)",
         "attrs": {"layer": "foundation", "mandatory": False}},
    ]
    api.bulk_add(foundation)
    api.toggle_layer('foundation', True)
    api.toggle_layer('user', True)

    # Treatment plan
    treatment_plan = [
        '(takes/P patient/C ibuprofen/C)',
        '(takes/P patient/C metformin/C)',
        '(takes/P patient/C aspirin/C)',
    ]

    print("\n" + "="*60)
    print("WHAT-IF ANALYSIS: Compare Patient Scenarios")
    print("="*60)

    # Scenario 1: Diabetic patient
    scenario1 = validate_plan(
        api,
        "Diabetic Patient",
        treatment_plan,
        ['diabetes']
    )

    # Clean user layer for next scenario
    user_edges = []
    for edge in list(api.all_edges()):
        attrs = api.get_attrs(edge)
        if attrs and attrs.get('layer') == 'user':
            user_edges.append(edge)
    for edge in user_edges:
        api.remove(edge)

    # Scenario 2: Pregnant patient
    scenario2 = validate_plan(
        api,
        "Pregnant Patient",
        treatment_plan,
        ['pregnancy']
    )

    # Clean user layer
    user_edges = []
    for edge in list(api.all_edges()):
        attrs = api.get_attrs(edge)
        if attrs and attrs.get('layer') == 'user':
            user_edges.append(edge)
    for edge in user_edges:
        api.remove(edge)

    # Scenario 3: Diabetic + Pregnant
    scenario3 = validate_plan(
        api,
        "Diabetic + Pregnant Patient",
        treatment_plan,
        ['diabetes', 'pregnancy']
    )

    # Summary comparison
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"{'Action':<40} | Diabetes | Pregnant | Both")
    print("-" * 60)

    for i, action in enumerate(treatment_plan):
        action_short = action.split()[0].replace('(takes/P', '').strip()
        s1 = "✓" if scenario1[i][1] == "ALLOW" else "✗"
        s2 = "✓" if scenario2[i][1] == "ALLOW" else "✗"
        s3 = "✓" if scenario3[i][1] == "ALLOW" else "✗"
        print(f"{action:<40} | {s1:^8} | {s2:^8} | {s3:^4}")

    print("\n💡 What-If Analysis helps compare treatment safety across scenarios!")
