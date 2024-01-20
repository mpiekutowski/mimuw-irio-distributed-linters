package loadbalancer.services

import cats.effect.IO
import loadbalancer.domain.*
import loadbalancer.routers.UriManagerRouter.{AddUriRequest, RemoveUriRequest}
import org.http4s.dsl.io.*
import org.http4s.{Response, Uri}

object UriManager {
  def add(secretKey: String, request: AddUriRequest, urisRef: UrisRef): IO[Response[IO]] =
    request.secretKey match
      case `secretKey` =>
        Uri.fromString(request.uri) match
          case Right(uri) =>
            request.lang match
              case "java" | "python" =>
                addUri(urisRef, request.lang, request.version, uri) *> Ok("Addition completed")
              case _ => BadRequest(s"Language: ${request.lang} not supported")
          case Left(invalid) =>
            BadRequest(s"Invalid uri: ${request.uri}")
      case _ => Forbidden()

  private def addUri(urisRef: UrisRef, lang: String, version: String, uri: Uri): IO[Unit] =
    urisRef.uris.update(_.add(BackendKind(lang, version), uri))

  def remove(secretKey: String, request: RemoveUriRequest, urisRef: UrisRef): IO[Response[IO]] =
    request.secretKey match
      case `secretKey` =>
        Uri.fromString(request.uri) match
          case Right(uri) =>
            removeUri(urisRef, uri) *> Ok("Removal completed")
          case Left(invalid) =>
            BadRequest(s"Invalid uri: ${request.uri}")
      case _ => Forbidden()

  private def removeUri(urisRef: UrisRef, uri: Uri): IO[Unit] =
    urisRef.uris.update(_.remove(uri))

}
