package loadbalancer.services

import cats.effect.IO
import loadbalancer.domain.*
import loadbalancer.routers.UriManagerRouter.{AddUriRequest, RemoveUriRequest}
import org.http4s.dsl.io.*
import org.http4s.{Response, Uri}

object UriManager {
  def add(request: AddUriRequest, urisRef: UrisRef): IO[Response[IO]] =
    Uri.fromString(request.uri) match
      case Left(invalid) =>
        BadRequest(s"Invalid uri: ${request.uri}")
      case Right(uri) =>
        request.lang match
          case "java" | "python" =>
            addUri(urisRef, request.lang, request.version, uri) *> Ok("Addition completed")
          case _ => BadRequest(s"Language: ${request.lang} not supported")

  private def addUri(urisRef: UrisRef, lang: String, version: String, uri: Uri): IO[Unit] =
    urisRef.uris.update(_.add(BackendKind(lang, version), uri))

  def remove(request: RemoveUriRequest, urisRef: UrisRef): IO[Response[IO]] =
    Uri.fromString(request.uri) match
      case Left(invalid) =>
        BadRequest(s"Invalid uri: ${request.uri}")
      case Right(uri) =>
        removeUri(urisRef, uri) *> Ok("Removal completed")

  private def removeUri(urisRef: UrisRef, uri: Uri): IO[Unit] =
    urisRef.uris.update(_.remove(uri))

}
