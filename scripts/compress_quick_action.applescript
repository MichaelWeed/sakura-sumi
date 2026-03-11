-- AppleScript wrapper for Sakura Sumi Quick Action
-- This ensures reliable path handling in Automator

on run {input, parameters}
	try
		-- Get the first selected item (folder)
		set selectedItem to item 1 of input
		
		-- Convert to POSIX path
		set folderPath to POSIX path of selectedItem
		
		-- Get the script directory
		set scriptPath to POSIX path of (path to me)
		set scriptDir to do shell script "dirname " & quoted form of scriptPath
		set projectRoot to do shell script "dirname " & quoted form of scriptDir
		
		-- Build the full command
		set compressScript to quoted form of (projectRoot & "/scripts/compress_with_defaults.sh")
		set folderPathQuoted to quoted form of folderPath
		
		-- Run the compression script
		set result to do shell script compressScript & " " & folderPathQuoted & " 2>&1"
		
		-- Show completion notification
		display notification "Compression complete! Check output directory: " & folderPath & "_ocr_ready" with title "🌸 Sakura Sumi"
		
		return result
	on error errorMessage number errorNumber
		-- Show error notification
		display dialog "Sakura Sumi Error: " & errorMessage buttons {"OK"} default button "OK" with icon stop
		return errorMessage
	end try
end run
