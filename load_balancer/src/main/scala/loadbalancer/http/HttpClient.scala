package loadbalancer.http

import cats.effect.IO
import org.http4s.client.Client
import org.http4s.{Request, Uri}

trait HttpClient {
  def sendAndReceive(uri: Uri, request: Request[IO]): IO[String]
}

object HttpClient {
  def of(client: Client[IO]): HttpClient =
    (uri: Uri, request: Request[IO]) => client.expect[String](request.withUri(uri))
}
