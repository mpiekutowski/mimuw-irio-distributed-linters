package loadbalancer.services

import cats.effect.IO
import loadbalancer.domain.{Backends, Uris}
import org.http4s.Uri

import scala.util.Try

trait RoundRobin {
  def apply(backends: Backends): IO[Option[Uri]]
}

object RoundRobin {
  def getNextBackend: RoundRobin =
    (backends: Backends) => backends.uris.getAndUpdate(cycle).map(_.currentOpt)

  private def cycle(uris: Uris): Uris =
    Try(Uris(uris.values.tail :+ uris.values.head)).getOrElse(Uris.empty())
}
