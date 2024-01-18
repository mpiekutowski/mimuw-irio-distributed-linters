package loadbalancer.routers

import cats.effect.IO
import io.circe.generic.auto.*
import loadbalancer.domain.Backends
import loadbalancer.services.UpdateBackends.BackendOperation.{Add, Remove}
import loadbalancer.services.{ParseUri, UpdateBackends}
import org.http4s.circe.CirceEntityDecoder.*
import org.http4s.dsl.io.*
import org.http4s.{HttpRoutes, Request}

object BackendManager {
  def routes(backends: Backends, parseUri: ParseUri, updateBackends: UpdateBackends): HttpRoutes[IO] = {
    HttpRoutes.of[IO] {
      case req @ POST -> Root / "add" =>
        req.decode[AddRequest] { addReq =>
          parseUri(addReq.uri) match
            case Left(invalid) => BadRequest(s"Invalid uri: ${invalid.uri}")
            case Right(uri) => for {
              _ <- updateBackends(backends, uri, Add)
              response <- Ok(s"Addition completed")
            } yield response
        }
      case req @ POST -> Root / "remove" =>
        req.decode[RemoveRequest] { removeReq =>
          parseUri(removeReq.uri) match
            case Left(invalid) => BadRequest(s"Invalid uri: ${invalid.uri}")
            case Right(uri) => for {
              _ <- updateBackends(backends, uri, Remove)
              response <- Ok(s"Removal completed")
            } yield response
        }
    }
  }

  private case class AddRequest(uri: String)
  private case class RemoveRequest(uri: String)
}
