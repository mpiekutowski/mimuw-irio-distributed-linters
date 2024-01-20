package loadbalancer

import cats.effect.{IO, IOApp}
import com.comcast.ip4s.{Host, Port}
import loadbalancer.domain.*
import loadbalancer.http.HttpServer
import org.typelevel.log4cats.Logger
import org.typelevel.log4cats.slf4j.Slf4jLogger
import org.typelevel.log4cats.syntax.LoggerInterpolator
import pureconfig.ConfigSource

object Main extends IOApp.Simple {
  implicit def logger: Logger[IO] = Slf4jLogger.getLogger[IO]

  override def run: IO[Unit] =
    for {
      urisRef   <- IO.ref(Uris.empty())
      javaVRR   <- IO.ref(VersionRoundRobin.initial(Map.empty))
      pythonVRR <- IO.ref(VersionRoundRobin.initial(Map.empty))
      config     = ConfigSource.default.loadOrThrow[Config]
      host       = Host.fromString(config.host).get
      port       = Port.fromInt(config.port).get
      totalRatio = config.totalRatio
      secretKey  = config.secretKey

      _ <- info"Starting server on $host:$port"
      _ <- HttpServer.start(
        host,
        port,
        totalRatio,
        secretKey,
        UrisRef(urisRef),
        VersionRoundRobinRef(javaVRR),
        VersionRoundRobinRef(pythonVRR)
      )
    } yield ()

}
