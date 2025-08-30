
# STAGE 1: Build the application

FROM --platform=${BUILDPLATFORM} mcr.microsoft.com/dotnet/sdk:7.0 AS build

# Optional build-time args for logging/debug
ARG TARGETPLATFORM
ARG TARGETARCH
ARG BUILDPLATFORM

# Just for visibility in CI logs
RUN echo "Building on ${BUILDPLATFORM}, targeting ${TARGETPLATFORM} (${TARGETARCH})"

WORKDIR /src

# Copy csproj and restore dependencies (better layer caching)
COPY *.csproj ./
RUN dotnet restore -a ${TARGETARCH}

# Copy everything else and build
COPY . ./
RUN dotnet publish -c Release -o /app -a ${TARGETARCH} --self-contained false --no-restore



# STAGE 2: Runtime image (minimal & secure)
FROM mcr.microsoft.com/dotnet/runtime:7.0

# Using a non root user for better security 
RUN useradd -m appuser
USER appuser

WORKDIR /app
COPY --from=build /app .

# Copy health checks and make them executable
COPY healthchecks/ /app/healthchecks/
RUN chmod +x /app/healthchecks/*.sh

# environment variables (can be overridden at runtime)
ENV DOTNET_EnableDiagnostics=0 \
    DOTNET_GCHeapHardLimit=0 \
    DOTNET_GCHeapHardLimitPercent=75 \
    DOTNET_GCTieredCompilation=1

ENTRYPOINT ["dotnet", "Worker.dll"]
