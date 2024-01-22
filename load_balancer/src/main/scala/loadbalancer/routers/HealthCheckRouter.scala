package loadbalancer.routers

import cats.effect.IO
import org.http4s.HttpRoutes
import org.http4s.Method.GET
import org.http4s.dsl.io.*

object HealthCheckRouter {
  def routes(): HttpRoutes[IO] = {
    HttpRoutes.of[IO] { case GET -> Root / "health" => Ok("") }
  }
}
