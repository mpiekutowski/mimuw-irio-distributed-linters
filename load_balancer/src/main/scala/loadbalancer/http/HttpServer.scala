package loadbalancer.http

import cats.effect.IO
import com.comcast.ip4s.{Host, Port}
import loadbalancer.domain.{UrisRef, VersionRoundRobinRef}
import loadbalancer.routers.{HealthCheckRouter, LoadBalancerRouter, RatioUpdaterRouter, UriManagerRouter}
import org.http4s.HttpApp
import org.http4s.ember.client.EmberClientBuilder
import org.http4s.ember.server.EmberServerBuilder
import org.http4s.server.middleware.Logger

object HttpServer {
  def start(
      host: Host,
      port: Port,
      totalRatio: Int,
      secretKey: String,
      urisRef: UrisRef,
      javaVRR: VersionRoundRobinRef,
      pythonVRR: VersionRoundRobinRef
  ): IO[Unit] = (
    for {
      client <- EmberClientBuilder.default[IO].build
      httpClient = HttpClient.of(client)
      httpApp = Logger.httpApp(logHeaders = false, logBody = true)(
        allRoutesComplete(urisRef, javaVRR, pythonVRR, httpClient, totalRatio, secretKey)
      )
      _ <- EmberServerBuilder
        .default[IO]
        .withHost(host)
        .withPort(port)
        .withHttpApp(httpApp)
        .build
    } yield ()
  ).useForever

  private def allRoutesComplete(
      urisRef: UrisRef,
      javaVRR: VersionRoundRobinRef,
      pythonVRR: VersionRoundRobinRef,
      httpClient: HttpClient,
      totalRatio: Int,
      secretKey: String
  ): HttpApp[IO] = {
    import cats.syntax.semigroupk.*

    val allRoutes =
      LoadBalancerRouter.routes(urisRef, javaVRR, pythonVRR, httpClient) <+>
        UriManagerRouter.routes(secretKey, urisRef) <+>
        RatioUpdaterRouter.routes(totalRatio, secretKey, javaVRR, pythonVRR) <+>
        HealthCheckRouter.routes()

    allRoutes.orNotFound
  }
}
