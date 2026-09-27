# Account brief evaluation

The shipped public brief is deterministic and has **no model or API calls**. It shows only claims whose source IDs exist and whose `verified_by_human` field is `Yes`. A service-fit inference is separately labelled, and gaps remain visible. Unit tests cover a verified-source acceptance and unverified-source rejection.

No 50-case LLM benchmark, reviewer usefulness score or preparation-time study has been run. The deck and README do not claim such results. An optional LLM research layer should be introduced only after a real, authorised source corpus exists. Before enabling it, freeze a 50-account evaluation set with similarly named institutions, missing facts and contradictory claims. Measure exact citation support, entity mixing, unsupported material statements, missing information and real reviewer usefulness; fail closed to the deterministic brief.
