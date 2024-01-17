package loadbalancer.services

import cats.effect.IO
import cats.syntax.applicative.*
import loadbalancer.http.HttpClient
import org.http4s.client.UnexpectedStatus
import org.http4s.{Request, Uri}
import org.typelevel.log4cats.Logger
import org.typelevel.log4cats.slf4j.Slf4jLogger
import org.typelevel.log4cats.syntax.*

trait SendAndExpect[A] {
  def apply(uri: Uri): IO[A]

}

object SendAndExpect {
  implicit def logger: Logger[IO] = Slf4jLogger.getLogger[IO]

  def toBackend(httpClient: HttpClient, req: Request[IO]): SendAndExpect[String] =
    (uri: Uri) =>
      info"sending request to $uri" *>
        httpClient.sendAndReceive(uri, req).handleErrorWith {
          case UnexpectedStatus(org.http4s.Status.NotFound, _, _) =>
            s"resource not found".pure[IO].flatTap(msg => warn"$msg")
          case _ =>
            s"cannot forward request: $req to uri: $uri".pure[IO].flatTap(msg => warn"$msg")
        }
}
