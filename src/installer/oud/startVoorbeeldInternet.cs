// Source - https://stackoverflow.com/a
// Posted by Cyberclops, modified by community. See post 'Timeline' for change history
// Retrieved 2025-11-13, License - CC BY-SA 4.0

using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;

class Program
{
    static async Task Main(string[] args)
    {
        // Path to the PowerShell script
        string psScriptPath = @"C:\temp\LabcontrolInstallerv2.ps1";

        // Run the script and capture the output
        var result = await ExecutePowerShellScriptAsync(psScriptPath);

        // Display the captured output
        Console.WriteLine($"Exit Code: {result.ExitCode}");
        Console.WriteLine("PowerShell Script Output:");
        Console.WriteLine(result.Output);
    }

    // Function to execute the PowerShell script with elevation using Verb="runas" and capture output
    public static async Task<(string Output, int ExitCode)> ExecutePowerShellScriptAsync(string scriptPath)
    {
        try
        {
            // Create a temporary output file
            string tempOutputFile = Path.Combine(Path.GetTempPath(), $"ps_output_{Guid.NewGuid()}.txt");

            // Wrap PowerShell script with native PowerShell output capture
            string wrappedCommand = $@"
                try {{
                    $ErrorActionPreference = 'Continue'
                    $output = & '{scriptPath}' 2>&1 | Out-String
                    $exitCode = $LASTEXITCODE
                    if ($null -eq $exitCode) {{ $exitCode = 0 }}
                    $output | Out-File -FilePath '{tempOutputFile}' -Encoding utf8
                    [System.Environment]::ExitCode = $exitCode
                }} catch {{
                    $_ | Out-File -FilePath '{tempOutputFile}' -Encoding utf8 -Append
                    [System.Environment]::ExitCode = 1
                }}
            ";

            // StartInfo setings to run the script with elevation
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = "powershell.exe",
                Arguments = $"-ExecutionPolicy Bypass -Command \"{wrappedCommand}\"",
                Verb = "runas", // This is the key property for elevation
                UseShellExecute = true, // Required for the Verb property to work
                WindowStyle = ProcessWindowStyle.Hidden // Hide the window
            };

            using (Process process = Process.Start(psi))
            {
                // Wait for the process to exit
                await process.WaitForExitAsync();

                // Load the output from the temporary file
                string output = "";
                if (File.Exists(tempOutputFile))
                {
                    // Give the file system a moment to complete writing
                    await Task.Delay(100);

                    // Read temporary file contents
                    output = await File.ReadAllTextAsync(tempOutputFile);

                    // Remove temporary file
                    File.Delete(tempOutputFile);
                }

                // Return output and exit code  
                return (output, process.ExitCode);
            }
        }
        catch (Exception ex)
        {
            // Give error information and return code
            return ($"Exception: {ex.Message}", -1);
        }
    }
}

//onderstaane gejat van internet zie: https://learn.microsoft.com/en-us/answers/questions/1334905/c-process-how-to-execute-powershell-command-with-a
/*
var processInfo = new System.Diagnostics.ProcessStartInfo
            {
                Verb = "runas",
                LoadUserProfile = true,
                FileName = "powershell.exe",
                Arguments = "Start-sleep -seconds 10",
                RedirectStandardOutput = false,
                UseShellExecute = true,
                CreateNoWindow = true
            };

            var p = System.Diagnostics.Process.Start(processInfo);
            */