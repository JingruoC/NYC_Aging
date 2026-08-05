using NycAging.Web.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();
builder.Services.AddScoped<MenuDraftService>();
builder.Services.AddScoped<AppModeService>();
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
app.MapBlazorHub();
app.MapFallbackToPage("/_Host");

app.Run();
