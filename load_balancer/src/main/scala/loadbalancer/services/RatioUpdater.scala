package loadbalancer.services

import cats.effect.IO
import loadbalancer.domain.{VersionRoundRobin, VersionRoundRobinRef}
import loadbalancer.routers.RatioUpdaterRouter.UpdateRatioRequest
import org.http4s.Response
import org.http4s.dsl.io.*

object RatioUpdater {
  def update(
      totalRatio: Int,
      javaVRR: VersionRoundRobinRef,
      pythonVRR: VersionRoundRobinRef,
      request: UpdateRatioRequest
  ): IO[Response[IO]] =
    request.versionRatio.values.sum match
      case `totalRatio` =>
        request.lang match
          case "java"   => updateRatio(request, javaVRR) *> Ok(s"Java ratio updated")
          case "python" => updateRatio(request, pythonVRR) *> Ok(s"Python ratio updated")
          case _        => BadRequest(s"Language: ${request.lang} not supported")
      case _ => BadRequest(s"Ratio parts should add up to $totalRatio")

  private def updateRatio(
      request: UpdateRatioRequest,
      roundRobinRef: VersionRoundRobinRef
  ): IO[Unit] =
    roundRobinRef.roundRobin.update(_ => VersionRoundRobin.initial(request.versionRatio))

}
