FROM debian:bookworm-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ca-certificates curl && rm -rf /var/lib/apt/lists/*
COPY main .
COPY schema.prisma .
COPY prisma-query-engine .
RUN chmod +x main prisma-query-engine
ENV PRISMA_QUERY_ENGINE_BINARY=/app/prisma-query-engine
CMD ["./main"]
