comp_def_a:
loads from profile_aa and profile_ab
profile_aa loads ac-1 and ac-2
profile_ab loads ac-2.1 and at-1

```
component comp_aa and comp_ab

comp_aa:
top_shared_rule_1 and comp_rule_aa_1 comp_rule_aa_2

top_shared_rule_1 has shared_param_1
set_param shared_param_1

imp_req ac-1 uses top_rule_aa_1
part a uses comp_rule_aa_1
comp_rule_aa_2 not used

comp_ab:
top_shared_rule_1 (same as above)
comp_rule_ab_1 comp_rule_ab_2
param shared_param_1

imp_req at-1 uses top_shared_rule_1
part b uses comp_rule_ab_1
```

comp_def_b:
loads from profile_ba and profile_bb
profile_ba loads ac-1 and ac-4
profile_bb loads ac-4 and at-2

```
component comp_ba and comp_bb
top level rule_ba and rule_bb

top level params rule_ba_param and rule_ba_param

comp_ba sets ac-1 and ac-4
comp_bb sets ac-4 and at-2
```
