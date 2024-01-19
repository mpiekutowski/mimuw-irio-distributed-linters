package loadbalancer.routers

import cats.effect.IO
import io.circe.generic.auto.*
import loadbalancer.domain.VersionRoundRobinRef
import loadbalancer.services.RatioUpdater
import org.http4s.circe.CirceEntityDecoder.*
import org.http4s.dsl.io.*
import org.http4s.{HttpRoutes, Request, Response}
object RatioUpdaterRouter {

  def routes(
      totalRatio: Int,
      javaVRR: VersionRoundRobinRef,
      pythonVRR: VersionRoundRobinRef
  ): HttpRoutes[IO] = {
    HttpRoutes.of[IO] { case req @ POST -> Root / "ratio" =>
      req.decode[UpdateRatioRequest](RatioUpdater.update(totalRatio, javaVRR, pythonVRR, _))
    }
  }

  case class UpdateRatioRequest(lang: String, versionRatio: Map[String, Int])
}
