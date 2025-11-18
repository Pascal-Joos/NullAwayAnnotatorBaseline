/*
 * MIT License
 *
 * Copyright (c) 2023 Nima Karimipour
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

package edu.ucr.cs.riple.core.util;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

/** Tests for Utility class. */
@RunWith(JUnit4.class)
public class UtilityTest {

  @Test
  public void testExecuteCommandAndCaptureOutput_Success() {
    // Execute a simple command that outputs to stdout
    Utility.CommandResult result = Utility.executeCommandAndCaptureOutput(null, "echo 'Hello World'");

    // Verify the exit code is 0 (success)
    assertEquals(0, result.exitCode);

    // Verify the output contains our expected text
    assertNotNull(result.output);
    assertTrue(result.output.contains("Hello World"));
  }

  @Test
  public void testExecuteCommandAndCaptureOutput_Failure() {
    // Execute a command that will fail
    Utility.CommandResult result = Utility.executeCommandAndCaptureOutput(null, "exit 1");

    // Verify the exit code is non-zero (failure)
    assertEquals(1, result.exitCode);

    // Output should be non-null (even if empty)
    assertNotNull(result.output);
  }

  @Test
  public void testExecuteCommandAndCaptureOutput_CapturesStderr() {
    // Execute a command that outputs to stderr (which should be merged with stdout)
    Utility.CommandResult result = Utility.executeCommandAndCaptureOutput(null, "echo 'Error Message' >&2");

    // Verify the exit code is 0 (success)
    assertEquals(0, result.exitCode);

    // Verify the output contains our expected error message
    assertNotNull(result.output);
    assertTrue(result.output.contains("Error Message"));
  }

  @Test
  public void testExecuteCommandAndCaptureOutput_MultilineOutput() {
    // Execute a command that produces multiple lines of output
    Utility.CommandResult result = Utility.executeCommandAndCaptureOutput(null, "echo 'Line1'; echo 'Line2'");

    // Verify the exit code is 0 (success)
    assertEquals(0, result.exitCode);

    // Verify the output contains both lines
    assertNotNull(result.output);
    assertTrue(result.output.contains("Line1"));
    assertTrue(result.output.contains("Line2"));
  }
}
