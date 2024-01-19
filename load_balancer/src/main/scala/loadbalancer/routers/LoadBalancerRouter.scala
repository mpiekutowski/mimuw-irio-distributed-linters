package loadbalancer.routers

import cats.effect.IO
import loadbalancer.domain.{UrisRef, VersionRoundRobinRef}
import loadbalancer.http.HttpClient
import loadbalancer.services.LoadBalancer
import org.http4s.HttpRoutes
import org.http4s.dsl.io.*

object LoadBalancerRouter {
  def routes(
      urisRef: UrisRef,
      javaVRR: VersionRoundRobinRef,
      pythonVRR: VersionRoundRobinRef,
      httpClient: HttpClient
  ): HttpRoutes[IO] =
    HttpRoutes.of[IO] { case req @ POST -> Root / "lint" / lang =>
      lang match
        case "java"   => LoadBalancer.forwardRequest(urisRef, javaVRR, httpClient, lang, req)
        case "python" => LoadBalancer.forwardRequest(urisRef, pythonVRR, httpClient, lang, req)
        case _        => BadRequest(s"Language: $lang is not supported")

    }
}
