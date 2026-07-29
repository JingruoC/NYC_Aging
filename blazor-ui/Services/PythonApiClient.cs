using System.Net.Http.Json;
using System.Text.Json;
using NycAging.Web.Models;

namespace NycAging.Web.Services;

public sealed class PythonApiClient
{
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

    public async Task<List<RecipeDto>> SearchRecipesAsync(string query)
    {
        var encoded = Uri.EscapeDataString(query ?? string.Empty);
        return await _http.GetFromJsonAsync<List<RecipeDto>>($"/recipes/search?q={encoded}", JsonOptions) ?? [];
    }

    public async Task<RecipeDto?> GetRecipeAsync(int recipeId)
    {
        return await _http.GetFromJsonAsync<RecipeDto>($"/recipes/{recipeId}", JsonOptions);
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
