package loadbalancer.services

import cats.syntax.either.*
import loadbalancer.services.ParseUri.InvalidUri
import org.http4s.Uri

trait ParseUri {
  def apply(uri: String): Either[InvalidUri, Uri]
}

object ParseUri {
  final case class InvalidUri(uri: String)

  object Impl extends ParseUri {
    override def apply(uri: String): Either[InvalidUri, Uri] =
      Uri.fromString(uri).leftMap(_ => InvalidUri(uri))
  }
}
