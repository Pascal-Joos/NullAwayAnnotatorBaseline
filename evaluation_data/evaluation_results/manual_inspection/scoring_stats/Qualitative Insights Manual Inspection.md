# Qualitative Insights Manual Inspection


## Hypotheses

### Why do baselines produce more resolving patches:

#### Baselines aggressively use guard conditions and suppressions that silence errors without addressing the underlying cause. (paper)(green color)
(explicitly throwing null-pointer exceptions, where actual call-sites handle the possibility that it returns null)

Example:
libgdx 103:

Caller expects to find null if channel not yet created and creates it on demand. Throwing, breaks the code. Actually the method should be changed to allow returning @Nullable and then one call site would need an additional missing null check. 

#### Baselines sometimes guess default values for fields, without knowing if they are meaningful. This might lead to silent and hard to debug bugs, when this default is used.(blue color) (FIELD_NO_INIT)

Example: 
conductor 20:
a status = null might encode that there is no status yet.
status = Status.SCHEDULED as initialization is wrong, as it is not scheduled on creation of the Task object.


#### Dirty fixes. Breaking some code semantics that are intended to resolve the warning. NullRepair tries more suffisticated changes but fails. (red color)

Example:
libgdx 390:
JsonWriter writer is inferred as @nonnull field, but has @nullable assignment during cleanup of the Writer (set null to prevent memory leak). Fix removes that which is wrong.

### Wrongly raised METHOD_NO_INIT cases by NullAway. Actually it is initialized on all paths. No idea how we could suppress such cases. (yellow color)

Example:
libgdx 65:
Initialization happens inside a called method (always). NullAway seems to not fully reason about that.

### Why reviewers preferred NullRepair patches:

#### Semantic precision and alignment with the program's intent. Rather than failing at the site of the error (or setting unmeaningful defaults), NullRepair often applied coordinated changes across the codebase to safely propagate null-handling logic. Deeper understanding of surrounding logic and more idiomatic and robust. (paper) (violet color)

Examples:  
glide 16 (proper handling)  
libgdx 63: NullRepair propagates null-handling. Others set unmeaningful defaults.  
libgdx 249: Across 2 files  
litiengine 97: Across 2 files  
glide 17: Basic sets unmeaningful default  
libgdx 355: Baselines set unmeaningful defaults. NullRepair propagates changed annotation  
libgdx 181: Handling across 2 files. Baselines set non-meaningful defaults



#### More idiomatic handling of false positives (e.g., suppression instead of bail-out or handling) (Better alignment with the program's intent). In some cases baselines do not recognize it as a false positive at all (blue color)

Examples:  
litiengine 30  
libgdx 318  
libgdx 364  
wala-util 17  
libgdx 191  
litiengine  
libgdx 83  
litiengine 118  
litiengine 117  
jadx 98  
libgdx 183  
jadx 84  
litiengine 56  
libgdx 41  
litiengine 110  
libgdx 128  
libgdx 415  
libgdx 288  
zuul 19  
glide 77  
glide 67


### Why reviewers sometimes preferred one of the baselines:

#### Error is genuine nullability issue and baselines produce fail-fast local fix to ensure safety (or reasonable default values if null). NullRepair is too complex or incorrect (e.g., wrong FP assumption). (paper) (red color)

Examples:  
eureka 1: Fix attempt by NullRepair is too complex, and propagates the error to reference locations instead of failing fast on site. The simpler failing by the baselines is correct here.  
litiengine 22: NullRepair is too complex  
spring-boot 32: Wrong FP assumption by NullRepair  
litiengine 78: Wrong FP assumption by NullRepair  
libgdx 113: NullRepair is too complex and not idiomatic. Others are not perfect either but better.  
jadx 9: All not good, but fail fast better than NullRepair.  
glide 9: NullRepair introduces an unrelated change  
glide 45: NullRepair introduces an unrelated change  
litiengine 76: Basic silently returns  
libgdx 363: NullRepair introduces an unrelated change  
zuul 10: NullRepair is not quite idiomatic, as it introduces nearly unnecessary variable  
gson 2: NullRepair only moves the warning weirdly.  
litiengine 130: NullRepair introduces an unrelated change (superfluous, wrong check)  
eureka 13: NullRepair doesn't add the needed logging in the case.  
glide 10: NullRepair adds functionality when variable is null that is not intended  
libgdx 100: Wrong decision of making nullable. Basic sets meaningful default  
wala-util 31: Wrong FP assumption by NullRepair  
gson 19: NullRepair introduces an unrelated change. Clutters with null-checks.  
litiengine 100: NullRepair introduces an unrelated change.  
wala-util 35: FP where baseline created more idiomatic fix
gson 7: NullRepair wrongly decided TP. Basline created more idiomatic fix.

Further classification:

Too complex:  
eureka 1: Fix attempt by NullRepair is too complex, and propagates the error to reference locations instead of failing fast on site. The simpler failing by the baselines is correct here.  
litiengine 22: NullRepair is too complex  
libgdx 113: NullRepair is too complex and not idiomatic. Others are not perfect either but better.  

Baseline more idiomatic:  
jadx 9: All not good, but fail fast better than NullRepair.  
litiengine 76: Basic silently returns  
zuul 10: NullRepair is not quite idiomatic, as it introduces nearly unnecessary variable  
gson 2: NullRepair only moves the warning weirdly.  
eureka 13: NullRepair doesn't add the needed logging in the case.  
libgdx 100: Wrong decision of making nullable. Basic sets meaningful default  
wala-util 35: FP where baseline created more idiomatic fix

Unrelated change:  
glide 9: NullRepair introduces an unrelated change  
glide 45: NullRepair introduces an unrelated change  
libgdx 363: NullRepair introduces an unrelated change  
litiengine 130: NullRepair introduces an unrelated change (superfluous, wrong check)  
glide 10: NullRepair adds functionality when variable is null that is not intended  
gson 19: NullRepair introduces an unrelated change. Clutters with null-checks.  
litiengine 100: NullRepair introduces an unrelated change.  

Wrong FP decision:  
spring-boot 32: Wrong FP assumption by NullRepair
litiengine 78: Wrong FP assumption by NullRepair  
wala-util 31: Wrong FP assumption by NullRepair  
gson 7: NullRepair wrongly decided TP. Baseline created more idiomatic fix.






### Why reviewers scored as tie:

#### All approaches sometimes fail to recognize complex initialization or assignment patterns, leading to incomplete or unnecessary changes. (non-recognized FP) (paper) (orange color)

Examples:  
libgdx 437  
litiengine 114  
libgdx 360  
libgdx 331  
libgdx 309  
libgdx 322  
litiengine 85: Correct track but both NullRepair and agent_baseline are incomplete  
libgdx 319  
libgdx 175: Not quite complete (both NullRepair and basic)  
glide 36  

#### Sometimes made changes contradict NullAway annotations => Correcting the annotations would be needed (yellow color)

Examples:  
libgdx 102   
jadx 61: Nullable should be removed  
libgdx 214  
libgdx 67 Nullable should be removed  
spring-boot 17 Nullable should be removed  


#### Sometimes (all three) produce similarly effective local edits with minimal context required. (paper) (green color)

Examples:  
libgdx 252  
litiengine 29  
spring-boot 56  
eureka 4  
libgdx 442  
jadx 89: Actually NullRepair is best here with suppression, but still scored as 2, as developers might not like it.  
litiengine 4  
spring-boot 20  
libgdx 42: NullRepair and Agent baseline both 1.  


#### Baselines are completely off track. NullRepair is closer, but makes unnecessary or incomplete changes and therefore has the same score. (grey color)

Examples:  
libgdx 196  
libgdx 445  

merged into first (orange color)






### Agent_baseline vs Basic

The two baselines often produce very similar fixes. Especially, if fixes are simple/local.  
NullRepair can be quite different as it uses a more methodical approach in creating fixes.


### Correctness of classifications

Correct TP: 27  

Correct FP: 33  

Incorrect TP: 9  

Incorrect FP: 6  

Recall: 0.8182  
Precision: 0.75  
Accuracy: 0.8  
F1-Score: 0.7826  

4 Incorrect classifications where reviewers were uncertain about the classification.  
