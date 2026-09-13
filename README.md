# Technical-doc assistant


## Golden dataset

`data/eval/golden.jsonl` contains the dataset generated from the Pydantic documentation corpus. Each ground-truth data has the following format :

```json
{
    "query_id" : "v2-01",
    "query" : "<some-questions>",
    "category" : "v2-only",
    "expected-claims" : ["<claim-1>", "<claim-2>", ...],
    "relevant_chunk_ids" : [],
    "must_cite" : false
}
```

The queries have the following tags :

|Tag|Meaning|
|---|---|
|v2-only|Answer exists only in v2 docs; catches version confusion|
|migration|v1→v2 upgrade questions (BaseSettings moves, model_validator, etc.)|
|how-to|Common task questions ("how do I define a strict model?")|
|api-symbol|Precise class/function/validator semantics — the rows where dense retrieval is weakest and future BM25/hybrid should win|
|hard-ambiguous|Vague or under-specified queries with multiple plausible readings|
|unanswerable|Not in the corpus; correct behavior is abstention, graded on refusing|

- `relevant_chunk_ids` are deterministic `sha1` ids, which are generated after ingesting and chunking the entire corpus. They are useful for citations
- `must_cite` is by default set to `false`. If the evaluation judge needs to do a citation check per query, then set it to `true`

