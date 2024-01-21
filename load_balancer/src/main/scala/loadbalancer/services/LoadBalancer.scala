package loadbalancer.services

import cats.effect.IO
import cats.syntax.applicative.*
import loadbalancer.domain.{BackendKind, UrisRef, VersionRoundRobinRef}
import loadbalancer.http.HttpClient
import org.http4s.client.UnexpectedStatus
import org.http4s.dsl.io.*
import org.http4s.implicits.*
import org.http4s.{Request, Response, Uri}
import org.typelevel.log4cats.Logger
import org.typelevel.log4cats.slf4j.Slf4jLogger
import org.typelevel.log4cats.syntax.*

import scala.util.Try
object LoadBalancer {
  implicit def logger: Logger[IO] = Slf4jLogger.getLogger[IO]

  def forwardRequest(
      urisRef: UrisRef,
      roundRobinRef: VersionRoundRobinRef,
      httpClient: HttpClient,
      lang: String,
      req: Request[IO]
  ): IO[Response[IO]] =
    getNextUri(lang, urisRef, roundRobinRef).flatMap {
      _.fold(ServiceUnavailable("No available linters")) { uri =>
        for {
          response <- send(httpClient, req, uri.withPath(path"/lint"))
          result   <- Ok(response)
        } yield result
      }
    }

  private def getNextUri(
      lang: String,
      urisRef: UrisRef,
      roundRobinRef: VersionRoundRobinRef
  ): IO[Option[Uri]] =
    for {
      version <- versionRoundRobin(roundRobinRef)
      uri     <- version.fold(IO.pure(None))(v => uriRoundRobin(urisRef, BackendKind(lang, v)))
    } yield uri

  private def versionRoundRobin(roundRobinRef: VersionRoundRobinRef): IO[Option[String]] =
    roundRobinRef.roundRobin.getAndUpdate(_.nextState()).map(_.currentOpt())
  private def uriRoundRobin(urisRef: UrisRef, kind: BackendKind): IO[Option[Uri]] =
    urisRef.uris
      .getAndUpdate(uris => Try(uris.spin(kind)).getOrElse(uris))
      .map(_.currentOpt(kind))

  private def send(httpClient: HttpClient, req: Request[IO], uri: Uri): IO[String] =
    info"sending request to $uri" *>
      httpClient.sendAndReceive(uri, req).handleErrorWith {
        case UnexpectedStatus(org.http4s.Status.NotFound, _, _) =>
          s"resource not found".pure[IO].flatTap(msg => warn"$msg")
        case _ =>
          s"cannot forward request: $req to uri: $uri".pure[IO].flatTap(msg => warn"$msg")
      }
}
