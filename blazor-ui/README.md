# Blazor Server UI

This is the current web UI for the Simple Servings menu planning MVP.

It targets .NET 10 and talks to the Python FastAPI service in `../backend`.

## Run Locally

The easiest local run is from the repository root:

```bash
bash ./start-all.sh
```

To run only the UI:

```bash
dotnet restore
dotnet run -- --urls http://127.0.0.1:5050
```

Set `PythonApi__BaseUrl` when the backend is not running at the default URL:

```bash
PythonApi__BaseUrl=http://127.0.0.1:8000 dotnet run -- --urls http://127.0.0.1:5050
```

## Pages

- `/` - role-specific home
- `/recipes/home` - recipe home
- `/recipes` - recipe list
- `/recipes/new` - add recipe
- `/recipes/review` - admin recipe review
- `/recipes/favorites` - favorite recipes
- `/menus/list` - saved menu list
- `/menus/new/blank` - start a blank menu
- `/menus/new/sample` - choose a sample menu
- `/menus/new` - menu planner
- `/menus/drafts` - provider drafts and returned menus
- `/menus/{id}` - saved menu review/detail
- `/reports` - report catalog
- `/resources` - resource files

## Notes

- Role behavior is simulated through the header role switcher.
- The UI uses deterministic backend endpoints only. It does not call an LLM or generative AI API.
