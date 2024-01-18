package loadbalancer.domain

import org.http4s.Uri

import scala.util.Try

final case class Uris(values: Vector[Uri]) extends AnyVal {
  def currentOpt: Option[Uri]    = Try(currentUnsafe).toOption
  private def currentUnsafe: Uri = values.head
  def remove(uri: Uri): Uris     = copy(values.filter(_ != uri))
  def add(uri: Uri): Uris        = copy((values :+ uri).distinct)
}

object Uris {
  def empty(): Uris = Uris(Vector.empty)
}
