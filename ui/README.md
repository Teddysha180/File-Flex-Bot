# UI Editing Guide

This folder is the easiest place to customize the bot without touching processing logic.

## Edit text content

Use [text.py](/c:/Users/lenovo/Downloads/File%20Flex%20Bot/ui/text.py) for:

- welcome text
- help text
- tool prompts
- success and error messages
- admin copy
- access and sharing messages

## Edit button names and menu order

Use [labels.py](/c:/Users/lenovo/Downloads/File%20Flex%20Bot/ui/labels.py) for:

- button labels
- home menu order
- conversion button order
- admin menu layout

## Files that still contain logic

- [handlers/files.py](/c:/Users/lenovo/Downloads/File%20Flex%20Bot/handlers/files.py): processing flow
- [handlers/admin.py](/c:/Users/lenovo/Downloads/File%20Flex%20Bot/handlers/admin.py): admin flow
- [handlers/access.py](/c:/Users/lenovo/Downloads/File%20Flex%20Bot/handlers/access.py): channel access flow
- [handlers/commands.py](/c:/Users/lenovo/Downloads/File%20Flex%20Bot/handlers/commands.py): `/start` and `/help`

If you want to change the look and wording only, start in the `ui` folder first.
