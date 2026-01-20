FROM alpine:latest
WORKDIR /app
COPY main .
COPY schema.prisma .
COPY prisma-query-engine .
RUN chmod +x main prisma-query-engine
ENV PRISMA_QUERY_ENGINE_BINARY=/app/prisma-query-engine
CMD ["./main"]
