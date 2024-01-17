package loadbalancer.routers

import cats.effect.IO
import loadbalancer.domain.Backends
import loadbalancer.services.{RoundRobin, SendAndExpect}
import org.http4s.dsl.io.*
import org.http4s.implicits.*
import org.http4s.{HttpRoutes, Request}
object LoadBalancer {
  def routes(
      backends: Backends,
      sendAndExpect: Request[IO] => SendAndExpect[String],
      roundRobin: RoundRobin
  ): HttpRoutes[IO] = {

    HttpRoutes.of[IO] { case req @ POST -> Root / "lint" =>
      roundRobin(backends).flatMap {
        _.fold(Ok("No available backends")) { backendUri =>
          val uri = backendUri.withPath(path"/lint")
          for {
            response <- sendAndExpect(req)(uri)
            result   <- Ok(response)
          } yield result
        }
      }
    }
  }
}
