"""Demo 3: Tri-State Validation (ALLOW/DENY/UNKNOWN) with Why-Trace"""

from graphbrain.api import GraphbrainAPI

with GraphbrainAPI('medical_kb.hg') as api:
    # 1. Load foundation pack
    foundation = [
        {"s": "(contraindicated/P ibuprofen/C diabetes/C)",
         "attrs": {"layer": "foundation", "mandatory": True, "confidence": 0.98}},
        {"s": "(recommended/P metformin/C diabetes/C)",
         "attrs": {"layer": "foundation", "mandatory": False}},
        {"s": "(required/P allergy_test/C new_medication/C)",
         "attrs": {"layer": "foundation", "mandatory": True}},
    ]
    api.bulk_add(foundation)

    # 2. Add agent rules
    api.add_fact('high_risk_drug', 'requires', 'doctor_approval',
                 attrs={'layer': 'agent_rule', 'mandatory': True})

    # 3. Add user profile (patient conditions)
    api.add_user_fact('diabetes', session_id='patient-001')
    # Note: we don't add allergy_test result → will trigger UNKNOWN

    # 4. Enable layers
    api.toggle_layer('foundation', True)
    api.toggle_layer('agent_rule', True)
    api.toggle_layer('user', True)

    # 5. Propose plan
    plan = [
        '(takes/P patient/C ibuprofen/C)',      # DENY (contraindicated + diabetes)
        '(takes/P patient/C metformin/C)',      # ALLOW (recommended for diabetes)
        '(takes/P patient/C new_medication/C)', # UNKNOWN (needs allergy_test)
    ]

    print("=" * 70)
    print("TRI-STATE VALIDATION: ALLOW / DENY / UNKNOWN")
    print("=" * 70)
    print()

    for action in plan:
        result = api.validate_against_rules(
            proposed_edges=action,
            layers=['foundation', 'agent_rule', 'user']
        )

        decision = result['decision']
        symbol = "✓" if decision == "ALLOW" else "✗" if decision == "DENY" else "?"

        print(f"{symbol} {action}")
        print(f"  Decision: {decision}")

        if result['rejected']:
            item = result['rejected'][0]
            trace = item['why_trace'][0]
            print(f"  Reason: {item['reason']}")
            print(f"  Rule: {trace['rule']}")
            print(f"  Matched: {trace['matched_concepts']}")
            print(f"    • From action: {trace['direct_match']}")
            print(f"    • From user: {trace['user_context']}")

        elif result['unknown']:
            item = result['unknown'][0]
            print(f"  Reason: {item['reason']}")
            print(f"  Suggestions: {', '.join(item['suggestions'])}")

        elif result['kept']:
            item = result['kept'][0]
            if item['why_trace']:
                trace = item['why_trace'][0]
                print(f"  Supported by: {trace['rule']}")
        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("✓ ALLOW  : Safe action, can proceed")
    print("✗ DENY   : Blocked by mandatory contraindication")
    print("? UNKNOWN: Needs more information (elicitation)")
