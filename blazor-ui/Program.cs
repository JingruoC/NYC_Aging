using NycAging.Web.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();
builder.Services.AddScoped<MenuDraftService>();
builder.Services.AddScoped<AppModeService>();
builder.Services.AddScoped<PrintQueueService>();
builder.Services.AddHttpClient<PythonApiClient>(client =>
{
    var baseUrl = builder.Configuration["PythonApi:BaseUrl"] ?? "http://localhost:8000";
    client.BaseAddress = new Uri(baseUrl);
});

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
    if (builder.Configuration.GetValue("EnableHttpsRedirect", false))
    {
        app.UseHttpsRedirection();
    }
}

app.UseStaticFiles();
app.UseRouting();

app.MapGet("/health", () => Results.Ok(new { status = "ok" }));
app.MapGet("/downloads/recipes/{recipeId:int}/attachments/{attachmentId:int}", async (
    int recipeId,
    int attachmentId,
    bool download,
    PythonApiClient api) =>
{
    var file = await api.DownloadRecipeAttachmentAsync(recipeId, attachmentId, download);
    return Results.File(file.Bytes, file.ContentType, download ? file.FileName : null, enableRangeProcessing: true);
});
app.MapGet("/downloads/recipes/{recipeId:int}/exports/{exportType}", async (
    int recipeId,
    string exportType,
    PythonApiClient api) =>
{
    var file = await api.DownloadRecipeExportAsync(recipeId, exportType);
    return Results.File(file.Bytes, file.ContentType, file.FileName);
});
app.MapGet("/downloads/resources/{resourceId:int}", async (
    int resourceId,
    bool download,
    PythonApiClient api) =>
{
    var file = await api.DownloadResourceFileAsync(resourceId, download);
    return Results.File(file.Bytes, file.ContentType, download ? file.FileName : null, enableRangeProcessing: true);
});
app.MapBlazorHub();
app.MapFallbackToPage("/_Host");

app.Run();
