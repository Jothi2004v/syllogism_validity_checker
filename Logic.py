import streamlit as st
import copy

def _normalize_copula(c):
    """Treat 'is' the same as 'are' (singular vs plural phrasing)."""
    c = c.lower().strip()
    if c == "is":
        return "are"
    elif c == "being":
        return "are"
    return c


def _find_pair(venns, a, b):
    """Return the venn dict for pair (a, b), checking BOTH key orders,
    since the AB (overlap/disjoint) region is symmetric regardless of
    which term was stored first. Returns None if neither exists."""
    if (a, b) in venns:
        return venns[(a, b)]
    if (b, a) in venns:
        return venns[(b, a)]
    return None


def _get_ab(venns, a, b):
    venn = _find_pair(venns, a, b)
    return venn["AB"] if venn else "unknown"


def _set_ab_shaded(venns, a, b):
    """Assert 'No a are b' (a, b disjoint). Returns False on contradiction."""
    venn = _find_pair(venns, a, b)
    if venn is None:
        venns[(a, b)] = {"A_only": "unknown", "AB": "shaded", "B_only": "unknown"}
        return True
    if venn["AB"] == "X":
        return False
    venn["AB"] = "shaded"
    return True


def _set_ab_x(venns, a, b):
    """Assert 'Some a are b' (a, b overlap). Returns False on contradiction."""
    venn = _find_pair(venns, a, b)
    if venn is None:
        venns[(a, b)] = {"A_only": "unknown", "AB": "X", "B_only": "unknown"}
        return True
    if venn["AB"] == "shaded":
        return False
    if venn["AB"] == "unknown":
        venn["AB"] = "X"
    return True


def _get_pair_exact(venns, a, b):
    """A_only is directional, so this only ever looks at the exact (a, b)
    key - never the reversed one - creating it if needed."""
    if (a, b) not in venns:
        venns[(a, b)] = {"A_only": "unknown", "AB": "unknown", "B_only": "unknown"}
    return venns[(a, b)]


def _run_closure(venns, detect_contradictions=False):
    """
    Run Rules 1-5 to a fixpoint on `venns`, in place, using the symmetric
    helpers above so facts get merged correctly no matter which term
    order they were originally stored in (e.g. a "No pen are car" fact
    and a "No car are pen" fact are recognized as the same thing).

    If detect_contradictions is True, returns False the moment a new
    derivation would conflict with an already-established fact (used for
    hypothetical "is this possible" checks). If False (the default, used
    for the real premises), conflicting derivations are just skipped
    rather than raising - direct premise contradictions are already
    reported separately when the premises are first applied.
    """
    changed = True
    while changed:
        changed = False
        current = list(venns.items())

        # AB (overlap/disjoint) is symmetric, but the matching below only
        # pattern-matches on literal stored key order (b == x). So a fact
        # stored as (pen, car) would never be found when looking for
        # something ending in "car". Add mirrored copies - same AB value,
        # A_only left unknown since that field genuinely IS directional
        # and can't be mirrored - purely so the matching below can find
        # them from either side.
        existing_keys = set(venns.keys())
        mirrors = []
        for (a, b), venn in current:
            if venn["AB"] != "unknown" and (b, a) not in existing_keys:
                mirrors.append(((b, a), {"A_only": "unknown", "AB": venn["AB"], "B_only": "unknown"}))
        current = current + mirrors

        for (a, b), venn1 in current:
            for (x, c), venn2 in current:
                if b == x and a != c:

                    # Rule 1: All A are B + No B are C => No A are C
                    if venn1["A_only"] == "shaded" and venn2["AB"] == "shaded":
                        existing = _get_ab(venns, a, c)
                        if existing == "X":
                            if detect_contradictions:
                                return False
                        elif existing != "shaded":
                            if not _set_ab_shaded(venns, a, c):
                                if detect_contradictions:
                                    return False
                            else:
                                changed = True

                    # Rule 2: All A are B + All B are C => All A are C
                    if venn1["A_only"] == "shaded" and venn2["A_only"] == "shaded":
                        if _get_ab(venns, a, c) == "shaded":
                            if detect_contradictions:
                                return False
                        else:
                            dest = _get_pair_exact(venns, a, c)
                            if dest["A_only"] == "X":
                                if detect_contradictions:
                                    return False
                            elif dest["A_only"] != "shaded":
                                dest["A_only"] = "shaded"
                                if dest["AB"] == "unknown":
                                    _set_ab_x(venns, a, c)
                                changed = True

                    # Rule 3: Some A are B + No B are C => Some A are not C
                    if venn1["AB"] == "X" and venn2["AB"] == "shaded":
                        dest = _get_pair_exact(venns, a, c)
                        if dest["A_only"] == "shaded":
                            if detect_contradictions:
                                return False
                        elif dest["A_only"] != "X":
                            dest["A_only"] = "X"
                            changed = True

                    # Rule 5: Some A are B + All B are C => Some A are C
                    if venn1["AB"] == "X" and venn2["A_only"] == "shaded":
                        if _get_ab(venns, a, c) == "shaded":
                            if detect_contradictions:
                                return False
                        elif _get_ab(venns, a, c) != "X":
                            _set_ab_x(venns, a, c)
                            changed = True

        # Rule 4 (shares the subject term): Some A are not B + All A are C
        # => Some C are not B
        for (a, b), venn1 in current:
            for (x, c), venn2 in current:
                if a == x and b != c:
                    if venn1["A_only"] == "X" and venn2["A_only"] == "shaded":
                        dest = _get_pair_exact(venns, c, b)
                        if dest["A_only"] == "shaded":
                            if detect_contradictions:
                                return False
                        elif dest["A_only"] != "X":
                            dest["A_only"] = "X"
                            changed = True

    return True


def _is_possible(base_venns, s, cop, p):
    """
    Check whether asserting 's cop p' (e.g. "All s are p") is consistent
    with everything already established in base_venns, by actually adding
    it as a hypothetical premise and re-running the same transitive
    closure the real premises go through - watching for any contradiction,
    direct or several steps away. Returns True (a genuine possibility) or
    False (ruled out).
    """
    venns = copy.deepcopy(base_venns)

    if cop == "all":
        venn = _get_pair_exact(venns, s, p)
        if venn["A_only"] == "shaded":
            return False   # already necessarily true, not merely possible
        if venn["A_only"] == "X":
            return False   # contradicted: "Some s are not p" is established
        if _get_ab(venns, s, p) == "shaded":
            return False   # contradicted: "No s are p" is established
        venn["A_only"] = "shaded"
        if _get_ab(venns, s, p) == "unknown":
            if not _set_ab_x(venns, s, p):
                return False

    elif cop == "no":
        if _get_ab(venns, s, p) == "shaded":
            return False   # already necessarily true
        if _get_ab(venns, s, p) == "X":
            return False   # contradicted: "Some s are p" is established
        venn = _get_pair_exact(venns, s, p)
        if venn["A_only"] == "shaded":
            return False   # contradicted: "All s are p" is established
        if not _set_ab_shaded(venns, s, p):
            return False

    elif cop == "some":
        if _get_ab(venns, s, p) == "X":
            return False   # already necessarily true, not merely possible
        if not _set_ab_x(venns, s, p):
            return False

    elif cop == "some_not":
        venn = _get_pair_exact(venns, s, p)
        if venn["A_only"] == "X":
            return False   # already necessarily true, not merely possible
        if venn["A_only"] == "shaded":
            return False   # contradicted: "All s are p" is established
        venn["A_only"] = "X"

    return _run_closure(venns, detect_contradictions=True)


def _is_definite(venns, c_q, c_c, c_s, c_p):
    """
    Definite (non-possibility) follow-check for a single quantifier
    statement, reading directly off the closed venn diagram. This is the
    same logic used for plain ("none" / "is a definite") conclusions,
    pulled out here so it can be reused by the complementary-pair check.
    """
    key = (c_s, c_p)
    reverse_key = (c_p, c_s)

    if key in venns:
        venn = venns[key]
        if c_q == "all" and c_c == "are":
            return venn["A_only"] == "shaded"
        elif c_q == "some" and c_c == "are":
            return venn["AB"] == "X"
        elif c_q == "some" and c_c == "are not":
            return venn["A_only"] == "X"
        elif c_q == "no" and c_c == "are":
            return venn["AB"] == "shaded"

    elif reverse_key in venns:
        venn = venns[reverse_key]
        if c_q == "some" and c_c == "are":
            return venn["AB"] == "X"
        elif c_q == "no" and c_c == "are":
            return venn["AB"] == "shaded"

    return False


def _find_complementary_pairs(conclusions):
    """
    Identify conclusions that form a complementary "Some X are Y" / "No X
    are Y" pair (same two terms, contradictory quantifiers - order of the
    terms doesn't matter for "No", since "No pen is paper" and "No paper
    is pen" mean the same thing). Returns a list of
    (some_index, no_index, subject, predicate) tuples.
    """
    parsed = []
    for idx, c in enumerate(conclusions):
        q = c["quantifier"].lower().strip()
        cop = _normalize_copula(c["copula"])
        s = c["subject"].lower().strip()
        p = c["predicate"].lower().strip()
        parsed.append((idx, q, cop, s, p))

    pairs = []
    used = set()
    for i, qi, copi, si, pi in parsed:
        if i in used or qi != "some" or copi != "are":
            continue
        for j, qj, copj, sj, pj in parsed:
            if j in used or j == i or qj != "no" or copj != "are":
                continue
            if {si, pi} == {sj, pj} and si != pi:
                pairs.append((i, j, si, pi))
                used.add(i)
                used.add(j)
                break
    return pairs


def check(premises, conclusions):
    st.subheader("✅ Results")
    venns = {}
# Apply Premises
    for p in premises:

        p_q = p["quantifier"].lower().strip()
        p_s = p["subject"].lower().strip()
        p_c = _normalize_copula(p["copula"])
        p_p = p["predicate"].lower().strip()

        key = (p_s, p_p)

        if key not in venns:
            venns[key] = {
                "A_only": "unknown",
                "AB": "unknown",
                "B_only": "unknown"
            }

        venn = venns[key]

        if p_q == "all" and p_c == "are":
            if venn["A_only"] == "X":
                st.error(f"Contradiction: All {p_s} are {p_p} conflicts with Some {p_s} are not {p_p}.")
            elif venn["AB"] == "shaded":
                st.error(f"Contradiction: All {p_s} are {p_p} conflicts with No {p_s} are {p_p}.")
            else:
                venn["A_only"] = "shaded"
# Traditional syllogism (existential) assumption
                if venn["AB"] == "unknown":
                    venn["AB"] = "X"

        elif p_q == "no" and p_c == "are":
            if venn["AB"] == "X":
                st.error(f"Contradiction: No {p_s} are {p_p} conflicts with Some {p_s} are {p_p}.")
            elif venn["A_only"] == "shaded":
                st.error(f"Contradiction: No {p_s} are {p_p} conflicts with All {p_s} are {p_p}.")
            else:
                venn["AB"] = "shaded"

        elif p_q == "some" and p_c == "are":
            if venn["AB"] == "shaded":
                st.error(f"Contradiction: Some {p_s} are {p_p} conflicts with No {p_s} are {p_p}.")
            else:
                venn["AB"] = "X"

        elif p_q == "some" and p_c == "are not":
            if venn["A_only"] == "shaded":
                st.error(f"Contradiction: Some {p_s} are not {p_p} conflicts with All {p_s} are {p_p}.")
            else:
                venn["A_only"] = "X"

        else:
            st.warning(
                f"Unrecognized premise form: '{p_q} {p_s} {p_c} {p_p}'. "
                "This premise was skipped."
            )
    
# Transitive closure (chaining through shared middle term)
    _run_closure(venns)

    # Check Conclusions
    results = []
    for c in conclusions:

        c_q = c["quantifier"].lower().strip()
        c_s = c["subject"].lower().strip()
        c_c = _normalize_copula(c["copula"])
        c_p = c["predicate"].lower().strip()
        c_m = c["modifier"].lower().strip()

        key = (c_s, c_p)
        reverse_key = (c_p, c_s)
        follows = False

        if c_m == "is a possibility":
            cop_map = {
                ("all", "are"): "all",
                ("some", "are"): "some",
                ("no", "are"): "no",
                ("some", "are not"): "some_not",
            }
            cop = cop_map.get((c_q, c_c))
            if cop is None:
                # Unrecognized quantifier/copula combo - fall back to
                # "not ruled out" behaviour.
                follows = True
            else:
                follows = _is_possible(venns, c_s, cop, c_p)

        else:
            follows = _is_definite(venns, c_q, c_c, c_s, c_p)

        results.append(follows)

    # Complementary pair rule: "Some X are Y" vs "No X are Y" are
    # contradictories - exactly one must be true. Check the "No" side
    # against both the definite diagram and the possibility diagram to
    # decide which one (or whether it's genuinely undetermined). Rendering
    # is left to the caller (app.py) - this just reports what happened.
    pair_info = []
    for (i_some, i_no, s, p) in _find_complementary_pairs(conclusions):
        definite_no = _is_definite(venns, "no", "are", s, p)
        possible_no = _is_possible(venns, s, "no", p)

        if definite_no:
            results[i_some] = False
            results[i_no] = True
            status = "no_definite"

        elif not possible_no:
            results[i_some] = True
            results[i_no] = False
            status = "some_definite"

        else:
            results[i_some] = True
            results[i_no] = True
            status = "either"

        pair_info.append({
            "some_index": i_some,
            "no_index": i_no,
            "subject": s,
            "predicate": p,
            "status": status,
        })

    return results, pair_info