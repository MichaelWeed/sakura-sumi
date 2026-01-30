# Right-Click Compression (macOS)

If you want to compress a folder from Finder without opening Terminal, you have a few options.

## Easiest: Double-click script

In the project, go to `scripts/` and find `compress_folder.command`. Double-click it and pick a folder when asked. You can also drag a folder onto that file.

No Automator setup. It just works.

## Terminal alias

If you live in the terminal, add this to `~/.zshrc`:

```bash
alias compress-code='bash /Users/johndoe/Projects/Sakura\ Sumi/scripts/compress_quick_action.sh'
```

Reload your config (`source ~/.zshrc`) and then run:

```bash
compress-code /path/to/your/folder
```

## Quick Action (Automator)

Quick Actions can be flaky. If you want to try anyway:

1. Open Automator and create a Quick Action.
2. Set it to receive **folders** in Finder.
3. Add "Run Shell Script". Set **Pass input** to **as arguments** (not stdin).
4. In the script box, put exactly:

```bash
/Users/johndoe/Projects/Sakura\ Sumi/scripts/compress_quick_action.sh "$@"
```

5. Save as something like "Compress with Sakura Sumi".

The `"$@"` is what passes the folder path. Without it, the script gets nothing.

If nothing happens when you use the Quick Action, check the log:

```bash
tail -50 ~/Library/Logs/sakura-sumi-quick-action.log
```

No new lines there usually means Automator isn’t running the script (wrong "Pass input" or path).

## Finder Service instead of Quick Action

Services often behave better than Quick Actions. In Automator, choose **Service** (not Quick Action), set it to receive **folders** in Finder, then use the same "Run Shell Script" step and script as above. Save the service; it’ll show up in the right-click menu. You can give it a keyboard shortcut under System Settings → Keyboard → Shortcuts → Services.
