using System.Net.Http.Json;
using System.Net.Http.Headers;
using System.Text.Json;
using Microsoft.AspNetCore.Components.Forms;
using NycAging.Web.Models;

namespace NycAging.Web.Services;

public sealed class PythonApiClient
{
    public const long MaxAttachmentBytes = 20 * 1024 * 1024;
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web)
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        DictionaryKeyPolicy = JsonNamingPolicy.SnakeCaseLower,
        PropertyNameCaseInsensitive = true
    };

    private readonly HttpClient _http;

    public PythonApiClient(HttpClient http)
    {
        _http = http;
    }

    public async Task<List<RecipeDto>> GetRecipesAsync(bool approvedOnly = false)
    {
        var path = approvedOnly ? "/recipes?approved_only=true" : "/recipes";
        return await _http.GetFromJsonAsync<List<RecipeDto>>(path, JsonOptions) ?? [];
    }

    public async Task<List<HomeUpdateDto>> GetHomeUpdatesAsync()
    {
        return await _http.GetFromJsonAsync<List<HomeUpdateDto>>("/home-updates", JsonOptions) ?? [];
    }

    public async Task<HomeUpdateDto?> GetHomeUpdateAsync(int updateId)
    {
        var response = await _http.GetAsync($"/home-updates/{updateId}");
        if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
        {
            return null;
        }

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<HomeUpdateDto>(JsonOptions);
    }

    public async Task<HomeUpdateDto> CreateHomeUpdateAsync(HomeUpdateCreateRequest update)
    {
        var response = await _http.PostAsJsonAsync("/home-updates", update, JsonOptions);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<HomeUpdateDto>(JsonOptions) ?? new HomeUpdateDto();
    }

    public async Task<List<RecipeHomeCategorySettingDto>> GetRecipeHomeCategorySettingsAsync()
    {
        return await _http.GetFromJsonAsync<List<RecipeHomeCategorySettingDto>>("/recipe-home-categories", JsonOptions) ?? [];
    }

    public async Task<RecipeHomeCategorySettingDto> UpdateRecipeHomeCategorySettingAsync(
        string categoryKey,
        bool isVisible,
        string? displayLabel = null,
        string? description = null)
    {
        var key = Uri.EscapeDataString(categoryKey);
        var response = await _http.PutAsJsonAsync(
            $"/recipe-home-categories/{key}",
            new { is_visible = isVisible, display_label = displayLabel, description },
            JsonOptions);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<RecipeHomeCategorySettingDto>(JsonOptions) ?? new RecipeHomeCategorySettingDto();
    }

    public async Task<List<RecipeDto>> SearchRecipesAsync(string query)
    {
        var encoded = Uri.EscapeDataString(query ?? string.Empty);
        return await _http.GetFromJsonAsync<List<RecipeDto>>($"/recipes/search?q={encoded}", JsonOptions) ?? [];
    }

    public async Task<RecipeDto?> GetRecipeAsync(int recipeId)
    {
        return await _http.GetFromJsonAsync<RecipeDto>($"/recipes/{recipeId}", JsonOptions);
    }

    public async Task<List<ResourceFileDto>> GetResourceFilesAsync()
    {
        return await _http.GetFromJsonAsync<List<ResourceFileDto>>("/resources", JsonOptions) ?? [];
    }

    public async Task<ResourceFileDto> UploadResourceFileAsync(
        string title,
        string resourceType,
        string description,
        string audience,
        DateTime lastUpdated,
        string uploadedBy,
        IBrowserFile file)
    {
        using var form = new MultipartFormDataContent();
        form.Add(new StringContent(title), "title");
        form.Add(new StringContent(resourceType), "resource_type");
        form.Add(new StringContent(description), "description");
        form.Add(new StringContent(audience), "audience");
        form.Add(new StringContent(lastUpdated.ToString("yyyy-MM-dd")), "last_updated");
        form.Add(new StringContent(uploadedBy), "uploaded_by");

        await using var stream = file.OpenReadStream(MaxAttachmentBytes);
        using var fileContent = new StreamContent(stream);
        fileContent.Headers.ContentType = MediaTypeHeaderValue.Parse(file.ContentType ?? "application/octet-stream");
        form.Add(fileContent, "file", file.Name);

        var response = await _http.PostAsync("/resources", form);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<ResourceFileDto>(JsonOptions) ?? new ResourceFileDto();
    }

    public async Task<FileDownload> DownloadResourceFileAsync(int resourceId, bool download)
    {
        var response = await _http.GetAsync($"/resources/{resourceId}/file?download={download.ToString().ToLowerInvariant()}");
        response.EnsureSuccessStatusCode();
        var fileName = response.Content.Headers.ContentDisposition?.FileNameStar
            ?? response.Content.Headers.ContentDisposition?.FileName
            ?? $"resource-{resourceId}";
        return new FileDownload(
            await response.Content.ReadAsByteArrayAsync(),
            response.Content.Headers.ContentType?.MediaType ?? "application/octet-stream",
            fileName.Trim('"'));
    }

    public async Task DeleteResourceFileAsync(int resourceId)
    {
        var response = await _http.DeleteAsync($"/resources/{resourceId}");
        response.EnsureSuccessStatusCode();
    }

    public async Task<RecipeDto> CreateRecipeAsync(RecipeCreateRequest recipe)
    {
        var response = await _http.PostAsJsonAsync("/recipes", recipe, JsonOptions);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<RecipeDto>(JsonOptions) ?? new RecipeDto();
    }

    public async Task<RecipeDto> UpdateRecipeAsync(int recipeId, RecipeDto recipe)
    {
        var response = await _http.PutAsJsonAsync($"/recipes/{recipeId}", recipe, JsonOptions);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<RecipeDto>(JsonOptions) ?? recipe;
    }

    public async Task<List<RecipeAttachmentDto>> GetRecipeAttachmentsAsync(int recipeId)
    {
        return await _http.GetFromJsonAsync<List<RecipeAttachmentDto>>($"/recipes/{recipeId}/attachments", JsonOptions) ?? [];
    }

    public async Task<RecipeAttachmentDto> UploadRecipeAttachmentAsync(int recipeId, string fileKind, IBrowserFile file)
    {
        using var form = new MultipartFormDataContent();
        await using var stream = file.OpenReadStream(MaxAttachmentBytes);
        using var fileContent = new StreamContent(stream);
        fileContent.Headers.ContentType = MediaTypeHeaderValue.Parse(file.ContentType ?? "application/octet-stream");
        form.Add(fileContent, "file", file.Name);
        var kind = Uri.EscapeDataString(fileKind);
        var response = await _http.PostAsync($"/recipes/{recipeId}/attachments?file_kind={kind}", form);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<RecipeAttachmentDto>(JsonOptions) ?? new RecipeAttachmentDto();
    }

    public async Task<FileDownload> DownloadRecipeAttachmentAsync(int recipeId, int attachmentId, bool download)
    {
        var response = await _http.GetAsync($"/recipes/{recipeId}/attachments/{attachmentId}?download={download.ToString().ToLowerInvariant()}");
        response.EnsureSuccessStatusCode();
        var fileName = response.Content.Headers.ContentDisposition?.FileNameStar
            ?? response.Content.Headers.ContentDisposition?.FileName
            ?? $"recipe-{recipeId}-attachment";
        return new FileDownload(
            await response.Content.ReadAsByteArrayAsync(),
            response.Content.Headers.ContentType?.MediaType ?? "application/octet-stream",
            fileName.Trim('"'));
    }

    public async Task<FileDownload> DownloadRecipeExportAsync(int recipeId, string exportType)
    {
        var safeType = exportType.Equals("nutrition", StringComparison.OrdinalIgnoreCase) ? "nutrition" : "submission";
        var response = await _http.GetAsync($"/recipes/{recipeId}/export/{safeType}.xlsx");
        response.EnsureSuccessStatusCode();
        var fileName = response.Content.Headers.ContentDisposition?.FileNameStar
            ?? response.Content.Headers.ContentDisposition?.FileName
            ?? $"recipe-{recipeId}-{safeType}.xlsx";
        return new FileDownload(
            await response.Content.ReadAsByteArrayAsync(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            fileName.Trim('"'));
    }

    public async Task<List<RecipeReviewCommentDto>> GetRecipeCommentsAsync(int recipeId)
    {
        return await _http.GetFromJsonAsync<List<RecipeReviewCommentDto>>($"/recipes/{recipeId}/comments", JsonOptions) ?? [];
    }

    public async Task<RecipeReviewCommentDto> CreateRecipeCommentAsync(int recipeId, RecipeReviewCommentCreateRequest request)
    {
        var response = await _http.PostAsJsonAsync($"/recipes/{recipeId}/comments", request, JsonOptions);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<RecipeReviewCommentDto>(JsonOptions) ?? new RecipeReviewCommentDto();
    }

    public async Task<MenuAnalysisDto> AnalyzeMenuAsync(MenuAnalysisRequest request)
    {
        var response = await _http.PostAsJsonAsync("/menus/analyze", request, JsonOptions);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<MenuAnalysisDto>(JsonOptions) ?? new MenuAnalysisDto();
    }

    public async Task<List<RecommendationItemDto>> GetAutocompleteAsync(List<int> selectedRecipeIds)
    {
        var response = await _http.PostAsJsonAsync("/recommendations/autocomplete", new { selected_recipe_ids = selectedRecipeIds, limit = 8 }, JsonOptions);
        response.EnsureSuccessStatusCode();
        var payload = await response.Content.ReadFromJsonAsync<Dictionary<string, List<RecommendationItemDto>>>(JsonOptions);
        return payload?["items"] ?? [];
    }

    public async Task<RevisionsResponseDto> GetRevisionsAsync(List<int> selectedRecipeIds)
    {
        var response = await _http.PostAsJsonAsync("/recommendations/revisions", new { selected_recipe_ids = selectedRecipeIds, limit = 8 }, JsonOptions);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<RevisionsResponseDto>(JsonOptions) ?? new RevisionsResponseDto();
    }

    public async Task<List<SimilarMenuDto>> GetSimilarMenusAsync(List<int> selectedRecipeIds)
    {
        var response = await _http.PostAsJsonAsync("/recommendations/similar-menus", new { selected_recipe_ids = selectedRecipeIds, limit = 5 }, JsonOptions);
        response.EnsureSuccessStatusCode();
        var payload = await response.Content.ReadFromJsonAsync<Dictionary<string, List<SimilarMenuDto>>>(JsonOptions);
        return payload?["items"] ?? [];
    }

    public async Task<MenuCreateResponse> CreateMenuAsync(MenuCreateRequest request)
    {
        var response = await _http.PostAsJsonAsync("/menus", request, JsonOptions);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<MenuCreateResponse>(JsonOptions) ?? new MenuCreateResponse();
    }

    public async Task<List<MenuSummaryDto>> GetMenusAsync()
    {
        return await _http.GetFromJsonAsync<List<MenuSummaryDto>>("/menus", JsonOptions) ?? [];
    }

    public async Task<MenuSummaryDto> SetMenuFavoriteAsync(int menuId, bool isFavorite)
    {
        var response = await _http.PatchAsJsonAsync($"/menus/{menuId}/favorite", new { is_favorite = isFavorite }, JsonOptions);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<MenuSummaryDto>(JsonOptions) ?? new MenuSummaryDto();
    }

    public async Task<List<MenuReviewCommentDto>> GetMenuCommentsAsync(int menuId)
    {
        return await _http.GetFromJsonAsync<List<MenuReviewCommentDto>>($"/menus/{menuId}/comments", JsonOptions) ?? [];
    }

    public async Task<MenuReviewCommentDto> CreateMenuCommentAsync(int menuId, MenuReviewCommentCreateRequest request)
    {
        var response = await _http.PostAsJsonAsync($"/menus/{menuId}/comments", request, JsonOptions);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<MenuReviewCommentDto>(JsonOptions) ?? new MenuReviewCommentDto();
    }

    public async Task<List<HistoricalMenuSummaryDto>> GetSampleMenusAsync()
    {
        return await _http.GetFromJsonAsync<List<HistoricalMenuSummaryDto>>("/sample-menus", JsonOptions) ?? [];
    }

    public async Task<HistoricalMenuDetailDto?> GetSampleMenuAsync(int id)
    {
        return await _http.GetFromJsonAsync<HistoricalMenuDetailDto>($"/sample-menus/{id}", JsonOptions);
    }

    public async Task<MenuDetailDto?> GetMenuAsync(int id)
    {
        return await _http.GetFromJsonAsync<MenuDetailDto>($"/menus/{id}", JsonOptions);
    }

    public async Task<AnalyticsDto> GetAnalyticsAsync()
    {
        return await _http.GetFromJsonAsync<AnalyticsDto>("/analytics", JsonOptions) ?? new AnalyticsDto();
    }
}

public sealed record FileDownload(byte[] Bytes, string ContentType, string FileName);
