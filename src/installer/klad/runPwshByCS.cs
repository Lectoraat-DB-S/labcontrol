// Source - https://stackoverflow.com/a
// Posted by Santiago Squarzon, modified by community. See post 'Timeline' for change history
// Retrieved 2025-11-14, License - CC BY-SA 4.0

using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Management.Automation;

namespace Testing
{
    public static class Test
    {
        public static IEnumerable<string> RunWithProcess(string fileName, string[] args)
        {
            ProcessStartInfo psi = new ProcessStartInfo
            {
                UseShellExecute = false,
                RedirectStandardOutput = true,
                FileName = fileName,
                Arguments = string.Join(" ", args)
            };

            using (Process proc = new Process { StartInfo = psi })
            {
                proc.Start();
                proc.WaitForExit();

                while (!proc.StandardOutput.EndOfStream)
                {
                    yield return proc.StandardOutput.ReadLine();
                }
            }
        }

        public static Collection<PSObject> RunWithPwsh(string fileName, string[] args)
        {
            using (PowerShell ps = PowerShell.Create())
            {
                return ps.AddScript(@"
                    param($process, $arguments)

                    & $process @arguments")
                .AddParameter("process", fileName)
                .AddParameter("arguments", args)
                .Invoke();
            }
        }
    }
}
