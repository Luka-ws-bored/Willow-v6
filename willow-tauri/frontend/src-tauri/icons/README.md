# Icons Directory - Willow Desktop Application

## REQUIRED FILE

You MUST add an `icon.ico` file in this directory for the Windows build to succeed.

**File path required**: `icons/icon.ico`

## How to Create the Icon

### Method 1: Convert PNG to ICO online

1. Visit https://icoconvert.com/
2. Upload one of your PNG files (the willow leaf designs you provided work great)
3. Select "Convert to ICO" with these settings:
   - Size: 256x256 (recommended for Windows compatibility)
   - Format: Windows ICO
4. Download the generated `.ico` file
5. Rename it to `icon.ico` and place it in this directory

### Method 2: Alternative converters

- https://cloudconvert.com/png-to-ico
- https://convertio.co/png-ico/
- https://online-converting.com/image/convert2ico/

## IMPORTANT NOTES

⚠️ **Critical Requirements:**

- File MUST be named exactly `icon.ico`
- File MUST be a real Windows ICO format (not a PNG renamed as .ico)
- Recommended size: 256x256 pixels for best Windows compatibility
- The Tauri build will FAIL without this file

## Verification

After adding the icon:

1. Run `cargo clean` in the src-tauri directory
2. Run `npm run tauri:dev` to test the build
3. The Windows Resource Compiler should accept the icon without errors

## Suggested Icon Design

Use one of the willow leaf PNG designs you provided:

- The single leaf design works well for an application icon
- The multi-branch design could also work
- Green color scheme matches the Willow branding
- Simple, recognizable design at small sizes

Once you add the proper `icon.ico` file, the Tauri desktop application will build successfully!
