package loadbalancer.http

import cats.effect.IO
import com.comcast.ip4s.{Host, Port}
import loadbalancer.domain.Backends
import loadbalancer.routers.{BackendManager, LoadBalancer}
import loadbalancer.services.*
import org.http4s.HttpApp
import org.http4s.ember.client.EmberClientBuilder
import org.http4s.ember.server.EmberServerBuilder
import org.http4s.server.middleware.Logger

object HttpServer {
  def start(
      backends: Backends,
      port: Port,
      host: Host,
      parseUri: ParseUri,
      roundRobin: RoundRobin,
      updateBackends: UpdateBackends
  ): IO[Unit] = (
    for {
      client <- EmberClientBuilder.default[IO].build
      httpClient = HttpClient.of(client)
      httpApp = Logger.httpApp(logHeaders = false, logBody = true)(
        allRoutesComplete(backends, httpClient, parseUri, roundRobin, updateBackends)
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
      backends: Backends,
      httpClient: HttpClient,
      parseUri: ParseUri,
      roundRobin: RoundRobin,
      updateBackends: UpdateBackends
  ): HttpApp[IO] = {
    import cats.syntax.semigroupk.*

    val allRoutes = LoadBalancer.routes(
      backends = backends,
      sendAndExpect = SendAndExpect.toBackend(httpClient, _),
      roundRobin = roundRobin
    ) <+> BackendManager.routes(
      backends = backends,
      parseUri = parseUri,
      updateBackends = updateBackends
    )

    allRoutes.orNotFound
  }
}
