package loadbalancer.routers

import cats.effect.IO
import io.circe.generic.auto.*
import loadbalancer.domain.UrisRef
import loadbalancer.services.UriManager
import org.http4s.HttpRoutes
import org.http4s.circe.CirceEntityDecoder.*
import org.http4s.dsl.io.*

object UriManagerRouter {
  def routes(urisRef: UrisRef): HttpRoutes[IO] = {
    HttpRoutes.of[IO] {
      case req @ POST -> Root / "add" =>
        req.decode[AddUriRequest](UriManager.add(_, urisRef))
      case req @ POST -> Root / "remove" =>
        req.decode[RemoveUriRequest](UriManager.remove(_, urisRef))
    }
  }

  case class AddUriRequest(lang: String, version: String, uri: String)
  case class RemoveUriRequest(uri: String)
}
