package edu.ucr.cs.riple.core.checkers.nullaway.codefix;

import edu.ucr.cs.riple.core.Context;
import edu.ucr.cs.riple.core.checkers.nullaway.NullAwayError;
import edu.ucr.cs.riple.injector.changes.RegionRewrite;
import java.util.Set;

public class AgentBaselineNullAwayCodeFix extends NullAwayCodeFix {
  public AgentBaselineNullAwayCodeFix(Context context) {
    super(context);
  }

  @Override
  public Set<RegionRewrite> fix(NullAwayError error) {
    return fixUsingAgent(error, context);
  }

  // TODO: Implement this integration of the Agent. Requires adequate logging and preprocessing.
  // Orient on ChatGPT.java.
  public Set<RegionRewrite> fixUsingAgent(NullAwayError error, Context context) {
    throw new UnsupportedOperationException();
  }
}
