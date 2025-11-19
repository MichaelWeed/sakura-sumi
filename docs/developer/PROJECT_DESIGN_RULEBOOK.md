# PROJECT DESIGN RULEBOOK

**Status**: Active - Design Specifications Migrated & Enhancements Implemented  
**Last Updated**: 2025-01-15  
**Purpose**: Single source of truth (SSOT) for all frontend design, styling, and UI implementation

---

This document is the single, non-negotiable source of truth for all frontend design, styling, and UI implementation for this project. Your primary goal is to adhere to these rules to ensure a consistent, polished, and high-quality user experience. Do not deviate from these principles without explicit instruction.

## 1. The Core Philosophy

**Simplicity First**: When in doubt, remove. The design must be clean, uncluttered, and free of any element that does not serve a clear purpose.

**Consistency is Key**: A user should never be surprised. Elements that look the same must behave the same. Elements that serve the same function must look the same.

**Clarity Above All**: The user must be able to understand the UI and its state at a glance. Avoid ambiguity.

## 2. Layout & Spacing (The "Grid")

This is the most critical set of rules for achieving polish.

### The Spacing Unit
All spacing (margins, padding, gaps) must be a multiple of a single base_unit. This is the holy grail of consistency.

- **base_unit**: **4px** (Tailwind CSS default)
- **Examples**: 0.5x (2px), 1x (4px), 2x (8px), 3x (12px), 4x (16px), 6x (24px), 8x (32px)
- **Rule**: There should be no arbitrary spacing values (e.g., 13px, 27px). All spacing must be multiples of 4px.

### Breathing Room
All content must be wrapped in containers with consistent internal padding. Never let text or interactive elements touch the edge of the screen or their container.

- **Default Page Padding**: **Horizontal: 16px (4x base_unit), Vertical: 32px (8x base_unit)** - Tailwind: `px-4 py-8`
- **Default Card/Box Padding**: **24px (6x base_unit)** - Tailwind: `p-6`
- **Form Input Padding**: **12px horizontal, 8px vertical (3x, 2x base_unit)** - Tailwind: `px-3 py-2`
- **Button Padding**: **16px horizontal, 8px vertical (4x, 2x base_unit)** - Tailwind: `px-4 py-2`

### Container Width
Content on wide screens must be constrained to a maximum width to ensure readability.

- **Max Content Width**: **896px (56rem)** - Tailwind: `max-w-4xl`
- **Container**: Centered with `mx-auto` utility class

## 3. Typography (The "Voice")

### Font Family
A maximum of two font families are allowed.

- **Primary (Body/UI)**: **System font stack** (Tailwind default: `ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif`)
- **Secondary (Headings)**: **Same as primary** (no secondary font family currently used)
- **Monospace (Code/Inputs)**: **System monospace** - Tailwind: `font-mono` (used for textarea inputs)

### Typographic Scale
All font sizes must be from a pre-defined scale. Do not invent new font sizes.

- **Heading 1 (H1)**: **36px (2.25rem)** - Tailwind: `text-4xl` - Used for page titles
- **Heading 2 (H2)**: **24px (1.5rem)** - Tailwind: `text-2xl` - Used for section headers
- **Heading 3 (H3)**: **18px (1.125rem)** - Tailwind: `text-lg` - Used for subsection headers
- **Body (Default)**: **16px (1rem)** - Tailwind default - Used for body text
- **Small**: **14px (0.875rem)** - Tailwind: `text-sm` - Used for labels, helper text
- **Extra Small**: **12px (0.75rem)** - Tailwind: `text-xs` - Used for table headers, fine print

### Font Weights

- **Bold**: `font-bold` (700) - Used for headings and emphasis
- **Semibold**: `font-semibold` (600) - Used for section headers (H2, H3)
- **Medium**: `font-medium` (500) - Used for labels and form field names
- **Normal**: Default (400) - Used for body text

### Readability

- **Body Line Height**: **1.5** (150%) - Tailwind default - Generous for easy reading
- **Tooltip Line Height**: **1.5** - Explicitly set for tooltip content
- **Line Length (Measure)**: Content constrained to max-width 896px ensures readable line length (approximately 60-80 characters per line)

## 4. Color Palette (The "Paint")

The color palette must be strictly limited. Colors are defined by their role, not just their value.

### Brand / Accent
The primary color for calls-to-action (buttons, links).

- **Primary**: **#2563EB** (Tailwind: `blue-600`) - Used for primary buttons, focus rings, progress bars
- **Primary (Hover)**: **#1D4ED8** (Tailwind: `blue-700`) - Used for button hover states
- **Primary (Focus Ring)**: **#2563EB** (Tailwind: `ring-blue-500`) - Used for focus states with 2px ring

### Background / Surface
The "paper" the content sits on.

- **Background (Page)**: **#F9FAFB** (Tailwind: `gray-50`) - Light gray page background
- **Surface (Cards/Modals)**: **#FFFFFF** (Tailwind: `white`) - White card backgrounds
- **Surface (Secondary)**: **#F9FAFB** (Tailwind: `gray-50`) - Used for log backgrounds, subtle sections
- **Surface (Table Header)**: **#F9FAFB** (Tailwind: `gray-50`) - Used for table header backgrounds

### Text / Content

- **Text (Headings)**: **#111827** (Tailwind: `gray-900`) - Dark gray for headings and primary text
- **Text (Body)**: **#111827** (Tailwind: `gray-900`) - Same as headings for consistency
- **Text (Muted)**: **#4B5563** (Tailwind: `gray-600`) - Medium gray for labels, helper text
- **Text (Secondary)**: **#6B7280** (Tailwind: `gray-500`) - Lighter gray for table headers, fine print
- **Text (Placeholder)**: Default browser placeholder color - Used for input placeholders

### Borders & Dividers

- **Border (Default)**: **#D1D5DB** (Tailwind: `gray-300`) - Used for input borders, dividers
- **Border (Table)**: **#E5E7EB** (Tailwind: `gray-200`) - Used for table row dividers

### Feedback (State)

- **Success**: **#16A34A** (Tailwind: `green-600`) - Used for success states, completed progress bars
- **Success (Hover)**: **#15803D** (Tailwind: `green-700`) - Used for success button hover
- **Success (Background)**: **#D1FAE5** (Tailwind: `green-100`) - Used for success badges
- **Success (Text)**: **#166534** (Tailwind: `green-800`) - Used for success badge text
- **Error / Danger**: **#EF4444** (Tailwind: `red-500`) - Used for error states, token bars (<10k tokens)
- **Error (Background)**: **#FEE2E2** (Tailwind: `red-100`) - Used for error badges
- **Error (Text)**: **#991B1B** (Tailwind: `red-800`) - Used for error badge text
- **Warning**: **#EAB308** (Tailwind: `yellow-500`) - Used for warning states, token bars (10k-50k tokens)
- **Warning (Background)**: **#FEF3C7** (Tailwind: `yellow-100`) - Used for warning badges
- **Warning (Text)**: **#854D0E** (Tailwind: `yellow-800`) - Used for warning badge text

### Token Bar Colors (Semantic)

- **Green Token Bar**: **#22C55E** (Tailwind: `green-500`) - Used for >50k tokens (significant savings)
- **Yellow Token Bar**: **#EAB308** (Tailwind: `yellow-500`) - Used for 10k-50k tokens (minimal savings)
- **Red Token Bar**: **#EF4444** (Tailwind: `red-500`) - Used for <10k tokens (not recommended)
- **Blue Token Bar**: **#3B82F6** (Tailwind: `blue-500`) - Used for "Before Compression" token bar

### Tooltip Colors

- **Tooltip Background**: **#1F2937** (Tailwind: `gray-800`) - Dark background for tooltips
- **Tooltip Text**: **#FFFFFF** (White) - White text on dark tooltip background
- **Tooltip Icon**: **#6B7280** (Tailwind: `gray-500`) - Default tooltip icon background
- **Tooltip Icon (Hover)**: **#4B5563** (Tailwind: `gray-600`) - Darker on hover
- **Tooltip Padding**: 12px (`p-3`) - Consistent with base_unit (3x)
- **Tooltip Max Width**: 320px - Aligned with spacing scale (80x base_unit = 320px)

## 5. Components & Interactivity (The "Feel")

### The Rule of One
There is only one visual style for each base component.

- **Primary Button**: All main "call to action" buttons must look identical.
  - Style: `bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium`
  - Font Size: 16px (default, `text-base` implicit)
  - Height: 40px (py-2 = 8px top/bottom + text height)
  - Border Radius: 6px (`rounded-md`)
  - Examples: "Start Compression" button, "Download Results" button

- **Secondary Button**: All "cancel" or "back" buttons must look identical.
  - Style: `bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500`
  - Font Size: 16px (default, `text-base` implicit)
  - Height: Matches primary button
  - Examples: "Browse..." buttons

- **Success Button**: Used for positive actions (e.g., download).
  - Style: `bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 font-medium`
  - Font Size: 16px (default, `text-base` implicit)
  - Examples: "Download Results (ZIP)" button

- **Small Button**: For less prominent actions (e.g., table actions).
  - Style: Same as primary/secondary but with `text-xs` (12px) and `px-3 py-1` padding
  - Font Size: 12px (`text-xs`)
  - Height: ~28px (py-1 = 4px top/bottom + text height)
  - Use Case: Table action buttons, inline actions, compact spaces
  - **Rationale**: Smaller buttons used in tables and compact layouts where full-size buttons would be too prominent

- **Text Inputs**: All text input fields must share the same style.
  - Style: `px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500`
  - Height: 36px (py-2 = 8px top/bottom + text height)
  - Border: 1px solid #D1D5DB
  - Border Radius: 6px (`rounded-md`)
  - Padding: 12px horizontal, 8px vertical

- **Textarea Inputs**: Multi-line text inputs.
  - Style: Same as text inputs + `w-full font-mono text-sm`
  - Monospace font for code/pattern input
  - Font size: 14px (`text-sm`)

- **Select Dropdowns**: Dropdown select inputs.
  - Style: Same as text inputs (`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500`)

- **Checkboxes**: Form checkboxes.
  - Style: Default browser checkbox with `mr-2` margin-right spacing
  - Label: `text-sm font-medium text-gray-700`

- **Cards/Containers**: Content containers.
  - Style: `bg-white rounded-lg shadow-md p-6`
  - Background: White
  - Border Radius: 8px (`rounded-lg`)
  - Shadow: Medium shadow (`shadow-md`)
  - Padding: 24px (`p-6`)

- **Progress Bars**: Progress indicators.
  - **Standard Progress Bars**: Height 10px (`h-2.5`)
    - Container: `w-full bg-gray-200 rounded-full h-2.5`
    - Bar: `bg-blue-600 h-2.5 rounded-full`
    - Use Case: Job progress, file processing status, general progress indicators
  - **Token Bars**: Height 16px (`h-4`)
    - Container: `w-full bg-gray-200 rounded-full h-4`
    - Bar: `h-4 rounded-full` (color varies: green/yellow/red/blue)
    - Use Case: Token estimation visualization, before/after comparisons
  - **Rationale**: Token bars are taller (16px) for better visibility of token count visualization. Standard progress bars are thinner (10px) for less visual weight in status displays.
  - Border Radius: Fully rounded (`rounded-full`)

- **Tables**: Data tables.
  - Header: `bg-gray-50` background, `px-4 py-4` padding (16px vertical, aligned with base_unit)
  - Cells: `px-4 py-4` padding (16px vertical, aligned with base_unit), `text-sm` font size
  - Dividers: `divide-y divide-gray-200`
  - Row Hover: `hover:bg-gray-50`
  - **Note**: Padding standardized to `py-4` (16px) to align with base_unit multiples

- **Links**: Text links (when used).
  - Style: `text-blue-600 hover:text-blue-800 underline hover:no-underline`
  - Focus: `focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`
  - Active: `active:text-blue-900`
  - Transition: `transition-colors duration-150`
  - **Note**: Currently no text links in UI, but this pattern applies when needed

- **Status Badges**: Status indicators for jobs, states, etc.
  - **Success**: `bg-green-100 text-green-800 px-2 py-1 text-xs font-semibold rounded`
  - **Error**: `bg-red-100 text-red-800 px-2 py-1 text-xs font-semibold rounded`
  - **Warning**: `bg-yellow-100 text-yellow-800 px-2 py-1 text-xs font-semibold rounded`
  - **Info**: `bg-blue-100 text-blue-800 px-2 py-1 text-xs font-semibold rounded`
  - **Neutral**: `bg-gray-100 text-gray-800 px-2 py-1 text-xs font-semibold rounded`
  - Padding: 8px horizontal (`px-2`), 4px vertical (`py-1`)
  - Font: 12px (`text-xs`), semibold weight
  - Border Radius: `rounded` (4px)

- **Loading Spinner**: For async operations (not yet implemented, but pattern defined).
  - **Style**: Circular spinner with border animation
  - **Size**: 24px default, 16px small, 32px large
  - **Color**: `border-blue-600` with transparent fill
  - **Animation**: Rotating border (360deg rotation, 1s linear infinite)
  - **Placement**: Centered in container or inline with text
  - **Note**: Currently uses progress bars instead; spinner pattern reserved for future use

- **Skeleton Screens**: Loading placeholders (not yet implemented, but pattern defined).
  - **Style**: `bg-gray-200 animate-pulse rounded`
  - **Height**: Match content height (e.g., `h-4` for text, `h-20` for cards)
  - **Width**: Variable based on content (e.g., `w-3/4` for text lines)
  - **Animation**: Pulse effect (opacity 0.5-1.0, 2s ease-in-out infinite)
  - **Use Case**: Show placeholder structure while content loads

- **Empty States**: When lists or data sets are empty.
  - **Container**: Centered content with padding
  - **Icon/Illustration**: Optional icon (see Icon System) or illustration
  - **Message**: `text-gray-500 text-sm` - Helpful, actionable message
  - **Action Button**: Optional primary button to take action
  - **Example**: "No jobs yet" in table, or "No results found. Try adjusting your filters."

- **Form Validation States**: Visual feedback for form errors.
  - **Error Field Border**: `border-red-500` (replaces default `border-gray-300`)
  - **Error Message**: `text-red-600 text-sm mt-1` - Displayed below field
  - **Error Icon**: Optional icon (⚠️ or ❌) before error message
  - **Success State**: `border-green-500` - Optional success indicator
  - **Focus State**: Maintains `focus:ring-2 focus:ring-blue-500` even when in error state
  - **Placement**: Error message appears immediately below input field

- **Toast Notifications**: Non-intrusive notifications (not yet implemented, but pattern defined).
  - **Position**: Top-right corner, fixed position
  - **Width**: 320px (aligned with tooltip max-width)
  - **Padding**: 16px (`p-4`)
  - **Background**: White with shadow (`bg-white shadow-lg`)
  - **Border**: Left border 4px wide (color matches type: green/red/yellow/blue)
  - **Animation**: Slide in from right, fade out after timeout
  - **Duration**: 5 seconds default, dismissible with close button
  - **Types**: Success (green), Error (red), Warning (yellow), Info (blue)
  - **Z-Index**: 1050 (above tooltips, below modals)

- **Modal/Dialog Components**: Overlay dialogs (not yet implemented, but pattern defined).
  - **Backdrop**: `bg-black bg-opacity-50 fixed inset-0` - Semi-transparent overlay
  - **Container**: `bg-white rounded-lg shadow-xl max-w-md mx-auto` - Centered modal
  - **Padding**: 24px (`p-6`)
  - **Header**: `text-xl font-semibold mb-4` - Modal title
  - **Body**: `text-gray-700` - Modal content
  - **Footer**: `flex justify-end gap-2 mt-6` - Action buttons
  - **Close Button**: Top-right corner, `text-gray-400 hover:text-gray-600`
  - **Z-Index**: 1100 (above toasts and tooltips)
  - **Animation**: Fade in backdrop, scale in modal (0.95 → 1.0)

- **Icon System**: Standardized icon usage.
  - **Library**: Unicode symbols currently used (▼, ▲, ✅, ⚠️, ❌)
  - **Sizes**: 
    - Small: 12px (`text-xs`) - Inline with text
    - Default: 16px (`text-sm`) - Standard size
    - Large: 20px (`text-base`) - Emphasized
    - Extra Large: 24px (`text-lg`) - Headings
  - **Color**: Inherits text color or explicit color class
  - **Spacing**: 4px margin (`ml-1` or `mr-1`) when inline with text
  - **Future Enhancement**: Consider icon library (Heroicons, Font Awesome) for consistency
  - **Current Icons**: 
    - ▼/▲: Collapse/expand indicators
    - ✅: Success/checkmark
    - ⚠️: Warning
    - ❌: Error/close

### Micro-interactions
All interactive elements (buttons, links, inputs) must provide subtle, immediate feedback on user interaction.

- **Hover State**: All clickable items must have a clear visual change on hover.
  - Buttons: Color darkens (e.g., `blue-600` → `blue-700`)
  - Links: Underline appears (for text links)
  - Tooltip Icons: Background darkens (`gray-500` → `gray-600`)
  - Table Rows: Background changes to `gray-50`

- **Active/Press State**: All clickable items must have a visual change when being pressed.
  - Buttons: Browser default active state (slightly darker)
  - No custom active styles currently defined (relies on browser defaults)

- **Focus State**: All inputs and links must have a highly visible focus ring for accessibility.
  - Style: `focus:outline-none focus:ring-2 focus:ring-blue-500`
  - Ring Width: 2px
  - Ring Color: Blue-500 (#3B82F6)
  - Applied to: All inputs, buttons, and interactive elements

- **Transitions**: All state changes must be smoothly animated.
  - **Progress Bars**: `transition: width 0.3s ease` - Smooth width changes
  - **Token Bars**: `transition: width 0.8s ease-in-out` - Slower, more noticeable animation
  - **Collapsible Content**: 
    - Collapse: `transition: max-height 0.3s ease-out`
    - Expand: `transition: max-height 0.5s ease-in`
  - **Tooltips**: `transition: opacity 0.2s ease-in-out` - Fade in/out
  - **General Rule**: Use `ease-out` for collapses, `ease-in` for expansions, `ease-in-out` for bidirectional animations

## 6. Visual States (The "Feedback")

The UI must explicitly communicate its state. Do not leave the user guessing.

- **Loading State**: Any time data is being fetched, a loading indicator must be displayed.
  - Progress bars show percentage completion
  - Status text updates: "Compressing... Please wait.", "Job queued...", etc.
  - Progress logs display timestamped messages
  - Button states: "Starting..." text replaces "Start Compression" when processing begins

- **Empty State**: When a list or data set is empty, do not show a blank void. Show a helpful message.
  - Job History: "No jobs yet" message displayed in centered table cell
  - Style: `text-center text-gray-500 text-sm`
  - Spans full table width with colspan

- **Error State**: When an action fails, show a clear, human-readable error message.
  - Alert dialogs: Browser `alert()` used for error messages
  - Error format: "Error: " + error message
  - Progress bars turn red (`bg-red-600`) on failure
  - Status badges: Red background (`bg-red-100 text-red-800`) for failed jobs

- **Success State**: When an action completes successfully, show clear confirmation.
  - Progress bars turn green (`bg-green-600`) on completion
  - Status badges: Green background (`bg-green-100 text-green-800`) for completed jobs
  - Results section displays with summary metrics

- **Hidden/Shown States**: Components can be conditionally displayed.
  - Hidden: `hidden` class (Tailwind: `display: none`)
  - Shown: Remove `hidden` class
  - Examples: Token estimation panel, progress view, results section, OCR options

## 7. Responsiveness (The "Fluidity")

- **Mobile First**: All designs must be implemented mobile-first. They must be perfectly usable on a small screen, and then adapted for larger screens.
  - Viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
  - Container uses responsive padding: `px-4` (16px) on all screen sizes
  - Grid layouts adapt: `grid-cols-1 md:grid-cols-2` for form fields
  - Token estimation grid: `grid-cols-3` (desktop) adapts to `grid-cols-2` (mobile) as documented

- **No Horizontal Scroll**: At no screen width shall a horizontal scrollbar ever be visible. Content must reflow gracefully.
  - Tables use `overflow-x-auto` wrapper for horizontal scrolling on small screens when necessary
  - Content constrained to max-width prevents excessive width
  - Text wraps naturally within containers

- **Touch Targets**: All clickable elements (buttons, links) must be large and have enough space around them to be easily tapped on a mobile device.
  - Buttons: Minimum 40px height (`py-2` = 8px + text height)
  - Tooltip icons: 16px × 16px with 4px margin-left spacing
  - Table cells: Adequate padding (`px-4 py-3`) for touch targets
  - Toggle buttons: Full header row is clickable for collapsible panels

- **Responsive Breakpoints** (Tailwind defaults):
  - **sm**: 640px - Small tablets
  - **md**: 768px - Tablets
  - **lg**: 1024px - Small desktops
  - **xl**: 1280px - Large desktops
  - **2xl**: 1536px - Extra large desktops

- **Current Responsive Patterns**:
  - Form grids: `grid-cols-1 md:grid-cols-2` - Single column on mobile, two columns on tablet+
  - Container: `max-w-4xl` - Constrained width on all screens, centered

---

## 8. Framework & Implementation

### CSS Framework

- **Primary Framework**: **Tailwind CSS** (via CDN: `https://cdn.tailwindcss.com`)
- **Custom CSS**: Inline `<style>` block in `index.html` for:
  - Progress bar transitions
  - Token bar animations
  - Collapsible content animations
  - Tooltip styles and positioning

### Design System Approach

- **Utility-First**: Tailwind CSS utility classes used throughout
- **Component Patterns**: Consistent class combinations form reusable component patterns
- **Custom Classes**: Minimal custom CSS, only for complex animations and tooltip positioning
- **No CSS Preprocessing**: Direct Tailwind CDN, no build step required

### Component-Specific Styles

#### Token Estimation Bar
- Animated width transitions (0.8s ease-in-out)
- Color-coded based on token thresholds
- Before/After comparison display
- Percentage savings calculation

#### Collapsible Insights Panel
- Smooth expand/collapse animation
- Max-height transition (0px → 1000px)
- Toggle icon (▼/▲) indicates state
- Summary view always visible, details collapsible

#### Tooltips
- Fixed positioning relative to viewport
- Dark background (#1F2937) with white text
- Fade in/out animation (0.2s opacity transition)
- Arrow indicator pointing to trigger element
- Auto-positioning to prevent off-screen placement
- Click-to-pin functionality (30-second timeout)

#### Progress Indicators
- Smooth width transitions (0.3s ease)
- Color changes based on state (blue → green/red)
- Percentage display with status text
- Log viewer with auto-scroll

---

## 9. Design Spec References (Legacy)

**Note**: The following files contain historical design information that has been migrated to this rulebook. These references are maintained for traceability but should not be used as the source of truth.

- **`docs/UI_IMPLEMENTATION.md`**: Contains UI component specifications, styling details, color coding, animations, and responsive design notes (migrated to sections 2-7 above)
- **`src/web/templates/index.html`**: Contains inline CSS styles, Tailwind CSS classes, and component markup (migrated to sections 2-8 above)
- **`docs/SOP.md`**: Section 3 previously contained design specifications (now references this rulebook for design specs, retains operational context only)

**Current Framework**: Tailwind CSS (via CDN) with custom CSS for animations and tooltips

**Operational Context**: For information about how components function (not how they look), see `docs/SOP.md` Section 3 (UI Component Usage).

---

## 10. Z-Index Scale (Layering System)

To ensure proper layering of overlapping elements, use the following z-index scale:

- **Base Content**: `z-0` (default, no z-index) - Page content, cards, containers
- **Sticky Headers**: `z-10` - Sticky navigation, headers
- **Dropdowns**: `z-20` - Dropdown menus, select options
- **Tooltips**: `z-30` (or `z-1000` for current implementation) - Tooltips, popovers
- **Modals**: `z-40` (or `z-1100` for future implementation) - Modal dialogs, overlays
- **Toasts**: `z-50` (or `z-1050` for future implementation) - Toast notifications

**Current Implementation**:
- Tooltips: `z-index: 1000` (maps to `z-30` in scale)
- **Recommendation**: Standardize to Tailwind z-index scale (`z-10` through `z-50`) for consistency

**Rule**: Higher z-index values indicate elements that should appear above lower values. Never use arbitrary z-index values outside this scale.

---

## 11. Design Pattern Gaps - Resolved

**Status**: All previously identified gaps have been addressed and documented in this rulebook.

### 11.1 Previously Undefined Patterns - Now Defined

✅ **Link Styling**: Defined in Section 5 (Components) - Hover, focus, active states specified  
✅ **Loading Spinners**: Defined in Section 5 (Components) - Pattern documented for future use  
✅ **Modal/Dialog Components**: Defined in Section 5 (Components) - Complete pattern specified  
✅ **Form Validation States**: Defined in Section 5 (Components) - Error states, messages, highlighting  
✅ **Toast Notifications**: Defined in Section 5 (Components) - Complete toast system pattern  
✅ **Skeleton Screens**: Defined in Section 5 (Components) - Loading placeholder pattern  
✅ **Empty State Patterns**: Defined in Section 5 (Components) - Empty state component pattern  
✅ **Status Badge System**: Defined in Section 5 (Components) - Complete badge variants  
✅ **Icon System**: Defined in Section 5 (Components) - Sizing, spacing, current icons documented  
✅ **Z-Index Scale**: Defined in Section 10 above - Complete layering system

### 11.2 Previously Identified Inconsistencies - Now Resolved

✅ **Progress Bar Heights**: Resolved in Section 5 (Components) - Rationale documented:
   - Standard progress bars: 10px (`h-2.5`) for general status
   - Token bars: 16px (`h-4`) for better visibility of token visualization

✅ **Button Sizing**: Resolved in Section 5 (Components) - Hierarchy established:
   - Primary/Secondary/Success buttons: 16px font (default)
   - Small buttons: 12px font (`text-xs`) for tables and compact spaces

✅ **Table Cell Padding**: Resolved in Section 5 (Components) - Standardized to `py-4` (16px):
   - Changed from `py-3` (12px) to `py-4` (16px) to align with base_unit multiples
   - Both header and cells now use `px-4 py-4` (16px/16px)

✅ **Tooltip Padding**: Resolved in Section 4 (Color Palette) - Max-width documented:
   - Padding: 12px (`p-3`) - Consistent with base_unit (3x)
   - Max-width: 320px - Aligned with spacing scale (80x base_unit = 320px)

### 11.3 Future Enhancements - ✅ IMPLEMENTED

The following recommendations have been **implemented** in `src/web/templates/index.html`:

1. ✅ **Icon Library Integration**: Migrated from Unicode symbols to inline SVG icons (Heroicons-style) for consistency
   - All icons (▼, ▲, ✅, ⚠️, ❌) replaced with inline SVG
   - Icons are consistent, scalable, and accessible

2. ✅ **Toast Notification System**: Replaced all browser `alert()` calls with styled toast notifications
   - Toast container with z-index 50 (top-right)
   - Four types: success, error, warning, info
   - Auto-dismiss after 5 seconds
   - Manual dismiss button
   - Slide-in animation

3. ✅ **Modal Components**: Created reusable modal component
   - Modal backdrop with z-index 40
   - Centered modal with scale-in animation
   - Close button and backdrop click to close
   - Ready for confirmations and detailed views

4. ✅ **Loading Spinners**: Added spinner component for async operations
   - Three sizes: small (16px), default (24px), large (32px)
   - Blue rotating border animation
   - `createSpinner(size)` helper function

5. ✅ **Skeleton Screens**: Added skeleton loading placeholders
   - Animated gradient background
   - `createSkeleton(height, width)` helper function
   - Ready for content placeholders

6. ✅ **Z-Index Standardization**: Migrated from arbitrary values to Tailwind scale
   - Tooltips: z-30 (was 1000)
   - Modals: z-40 (was 1100)
   - Toasts: z-50 (was 1050)
   - All values now align with Tailwind z-index scale

**Status**: All enhancements implemented and active. The design system is complete, consistent, and production-ready.

