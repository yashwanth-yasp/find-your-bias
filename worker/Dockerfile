# ---------------------------------------------------------
# STAGE 1: Build the application
# ---------------------------------------------------------
# Always build on amd64 unless you override with --platform
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


# ---------------------------------------------------------
# STAGE 2: Runtime image (minimal & secure)
# ---------------------------------------------------------
FROM mcr.microsoft.com/dotnet/runtime:7.0

# Always use a non-root user in production
# (1000 is arbitrary, you can match Kubernetes/OpenShift guidelines)
RUN useradd -m appuser
USER appuser

WORKDIR /app
COPY --from=build /app .

# Optional: environment variables (can be overridden at runtime)
ENV DOTNET_EnableDiagnostics=0 \
    DOTNET_GCHeapHardLimit=0 \
    DOTNET_GCHeapHardLimitPercent=75 \
    DOTNET_GCTieredCompilation=1

# ENTRYPOINT is strict: always run the worker
ENTRYPOINT ["dotnet", "Worker.dll"]
