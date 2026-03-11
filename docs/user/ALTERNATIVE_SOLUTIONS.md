# Other Ways to Run the Compressor

The right-click Quick Action doesn’t always play nice with Automator. Here are alternatives that do.

**Double-click script** — In `scripts/`, double-click `compress_folder.command` and choose a folder (or drag a folder onto it). Easiest and most reliable.

**Terminal** — From the project root, run:

```bash
bash scripts/compress_quick_action.sh /path/to/folder
```

Or add the `compress-code` alias to your shell config (see [Right-Click Compression](RIGHT_CLICK_COMPRESS.md)).

**Finder Service** — In Automator, create a **Service** that receives folders in Finder and runs the same shell script as in the Quick Action section. Services tend to be more reliable than Quick Actions and you can assign a keyboard shortcut.

More detail on each of these is in [RIGHT_CLICK_COMPRESS.md](RIGHT_CLICK_COMPRESS.md).
