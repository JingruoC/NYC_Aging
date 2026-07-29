FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build

WORKDIR /src

COPY blazor-ui/NycAging.Web.csproj blazor-ui/
RUN dotnet restore blazor-ui/NycAging.Web.csproj

COPY blazor-ui/ blazor-ui/
RUN dotnet publish blazor-ui/NycAging.Web.csproj -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime

WORKDIR /app
ENV ASPNETCORE_URLS=http://+:5050
EXPOSE 5050

COPY --from=build /app/publish .

ENTRYPOINT ["dotnet", "NycAging.Web.dll"]
