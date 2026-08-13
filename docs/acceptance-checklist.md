# MVP Acceptance Checklist

This checklist records the status of the August 2026 prototype review. It distinguishes implemented prototype behavior from production integration work.

## Home and resources

- Complete: admins can publish announcements or long-form stories with optional pictures.
- Complete: full stories open on a dedicated detail page, and updates appear before shortcuts.
- Complete: resource files sort ascending or descending when `Updated` is selected.
- Complete: recipes, menus, sample menus, reports, and resources can be collected in the session print queue.

## Recipes

- Complete: recipe review opens or downloads uploaded label and analysis files.
- Complete: recipe submissions and normalized nutrition values export to Excel.
- Complete: admins control which Recipe Home categories are visible and can add category tiles.
- Complete: recipe list and planner gallery support multiple simultaneous tag filters using AND matching.
- Complete: admins can add tags while editing a recipe.
- Complete: recipe list sorts by upload date, uses `Include archived` instead of the unclear `Show Dead Recipes`, and displays a concise recipe description instead of nutrient columns.
- Complete: recipe detail includes contributor, public/private status, scaling, printing, editable tags for admins, and a full FDA-style nutrition panel at the bottom.
- Complete: providers receive a submission form and read-only catalog view; admins receive direct catalog-entry and review tools.
- Prototype limitation: uploaded Nutritionist Pro workbooks are retained byte-for-byte, and normalized nutrition fields are stored separately. Automatic mapping of every proprietary workbook field is not implemented.
- Compliance limitation: the label visually follows the FDA Nutrition Facts hierarchy, but it is not a certified regulatory-label generator.

## Menus

- Complete: sample previews show a full service week with entree, side, and vegetable only and omit calories.
- Complete: saved and sample menus can be duplicated into a new draft.
- Complete: the planner supports five- or seven-day service, six cycle weeks, whole-week copy, whole-week swap, day swap, and copying one recipe to another week.
- Complete: the calendar starts on Monday; week tabs advance dates by seven days; deselected service days are removed from the board.
- Complete: `Clear selected day` uses an explicit day selector.
- Complete: admins can select multiple contracts; a provider is locked to its own contract.
- Complete: recipe names wrap, card actions remain inside the cell, and occupied cells reject accidental replacement.
- Complete: selecting a component cell and choosing `Add` places the recipe; clicking `View` opens the full recipe modal.
- Complete: a week cannot be marked complete until all required visible cells are filled and nutrition/meal checks pass.
- Complete: nutrition is available in compact and full-screen views.
- Complete: admin menu review supports linked cell/recipe comments, overall comments, provider-facing summaries, review history, repeated-recipe checks, and provider-specific review perspectives.
- Manual QA item: pointer drag/drop should still be checked on each supported browser and touch device. The keyboard/click placement path is the reliable accessibility fallback and is covered by browser QA.

## Prototype boundaries

- Role switching simulates authorization; production identity and role enforcement are not connected.
- The print queue is scoped to the active browser session and invokes browser printing; it is not an operating-system print spooler.
- Render demo uploads and SQLite data are ephemeral.
- Menu cycle weeks are persisted as weekly menu records rather than under a normalized parent-cycle entity.
