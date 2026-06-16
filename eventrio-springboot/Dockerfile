# Multi-stage build – build ALL modules once, then pick one JAR per service image.
# Single service: docker build --build-arg MODULE=eventrio-user-service -t eventrio-user-service .
# Full stack:    docker compose up -d --build

FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /build

# Copy POMs first so dependency download is cached when only source changes
COPY pom.xml .
COPY eventrio-common/pom.xml eventrio-common/
COPY eventrio-gateway/pom.xml eventrio-gateway/
COPY eventrio-web-service/pom.xml eventrio-web-service/
COPY eventrio-user-service/pom.xml eventrio-user-service/
COPY eventrio-organization-service/pom.xml eventrio-organization-service/
COPY eventrio-event-service/pom.xml eventrio-event-service/
COPY eventrio-collaboration-service/pom.xml eventrio-collaboration-service/
COPY eventrio-ticketing-service/pom.xml eventrio-ticketing-service/
COPY eventrio-payment-service/pom.xml eventrio-payment-service/
COPY eventrio-notification-service/pom.xml eventrio-notification-service/
COPY eventrio-ai-orchestrator-service/pom.xml eventrio-ai-orchestrator-service/

RUN --mount=type=cache,target=/root/.m2 \
    mvn dependency:go-offline -B -q || true

COPY eventrio-common eventrio-common
COPY eventrio-gateway eventrio-gateway
COPY eventrio-web-service eventrio-web-service
COPY eventrio-user-service eventrio-user-service
COPY eventrio-organization-service eventrio-organization-service
COPY eventrio-event-service eventrio-event-service
COPY eventrio-collaboration-service eventrio-collaboration-service
COPY eventrio-ticketing-service eventrio-ticketing-service
COPY eventrio-payment-service eventrio-payment-service
COPY eventrio-notification-service eventrio-notification-service
COPY eventrio-ai-orchestrator-service eventrio-ai-orchestrator-service

# Build every module in one Maven invocation (shared by all 10 service images via BuildKit cache)
RUN --mount=type=cache,target=/root/.m2 \
    mvn package -DskipTests -B -q -T 1C

FROM eclipse-temurin:17-jre AS runtime
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

ARG MODULE=eventrio-gateway
COPY --from=build /build/${MODULE}/target/${MODULE}-*.jar /app/app.jar

ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
EXPOSE 8080

ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -jar /app/app.jar"]
