package loadbalancer.domain

import cats.effect.{IO, Ref}
import org.http4s.Uri

import scala.util.Try

final case class UrisRef(uris: Ref[IO, Uris])

final case class Uris(queueMap: Map[BackendKind, Vector[Uri]]) extends AnyVal {
  def currentOpt(kind: BackendKind): Option[Uri]    = Try(currentUnsafe(kind)).toOption
  private def currentUnsafe(kind: BackendKind): Uri = queueMap(kind).head
  def remove(uri: Uri): Uris = copy {
    queueMap
      .map((k, v) => (k, v.filter(_ != uri)))
      .filterNot((k, v) => v.isEmpty)
  }

  def add(kind: BackendKind, uri: Uri): Uris = copy {
    val updatedUris = (queueMap.getOrElse(kind, Vector()) :+ uri).distinct
    queueMap.updated(kind, updatedUris)
  }

  def spin(kind: BackendKind): Uris = copy {
    val kindUris = queueMap(kind)
    queueMap.updated(kind, kindUris.tail :+ kindUris.head)
  }
}

object Uris {
  def empty(): Uris = Uris(Map.empty)
}
