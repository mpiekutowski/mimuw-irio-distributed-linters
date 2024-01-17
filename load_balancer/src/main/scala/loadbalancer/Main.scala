package loadbalancer

import cats.effect.{IO, IOApp}
import cats.implicits.catsSyntaxTuple2Semigroupal
import com.comcast.ip4s.{Host, Port}
import loadbalancer.domain.{Backends, Config, Uris}
import loadbalancer.errors.Config.InvalidConfig
import loadbalancer.http.HttpServer
import loadbalancer.services.{ParseUri, RoundRobin, UpdateBackends}
import org.typelevel.log4cats.Logger
import org.typelevel.log4cats.slf4j.Slf4jLogger
import org.typelevel.log4cats.syntax.LoggerInterpolator
import pureconfig.ConfigSource

object Main extends IOApp.Simple {
  implicit def logger: Logger[IO] = Slf4jLogger.getLogger[IO]

  override def run: IO[Unit] =
    for {
      config <- IO(ConfigSource.default.loadOrThrow[Config])
      backendUris = Uris(Vector())
      backends    <- IO.ref(backendUris)
      hostAndPort <- IO.fromEither(hostAndPort(config.host, config.port))
      (host, port) = hostAndPort
      _ <- info"Starting server on $host:$port"
      _ <- HttpServer.start(
        Backends(backends),
        port,
        host,
        ParseUri.Impl,
        RoundRobin.getNextBackend,
        UpdateBackends.Impl
      )
    } yield ()

  private def hostAndPort(
      host: String,
      port: Int
  ): Either[InvalidConfig, (Host, Port)] =
    (
      Host.fromString(host),
      Port.fromInt(port)
    ).tupled.toRight(InvalidConfig)
}
