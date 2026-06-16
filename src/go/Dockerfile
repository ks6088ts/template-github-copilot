FROM golang:1.26 AS build

ARG GIT_REVISION="0000000"
ARG GIT_TAG="x.x.x"

WORKDIR /go/src/app
COPY . .

RUN make build OUTPUT=/go/bin/app

FROM gcr.io/distroless/static-debian12:nonroot

COPY --from=build /go/bin/app /
CMD ["/app"]
