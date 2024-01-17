package loadbalancer.services

import cats.effect.IO
import loadbalancer.domain.{Backends, Uris}
import loadbalancer.services.UpdateBackends.BackendOperation
import loadbalancer.services.UpdateBackends.BackendOperation.{Add, Remove}
import org.http4s.Uri

trait UpdateBackends {
  def apply(backends: Backends, uri: Uri, operation: BackendOperation): IO[Uris]
}

object UpdateBackends {

  object Impl extends UpdateBackends {
    override def apply(backends: Backends, uri: Uri, operation: BackendOperation): IO[Uris] =
      backends.uris.updateAndGet { uris =>
        operation match
          case Add => uris.add(uri)
          case Remove => uris.remove(uri)
      }
  }

  enum BackendOperation {
    case Add, Remove
  }
}
