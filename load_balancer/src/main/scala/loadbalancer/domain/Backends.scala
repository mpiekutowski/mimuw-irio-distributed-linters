package loadbalancer.domain

import cats.effect.{IO, Ref}

case class Backends(uris: Ref[IO, Uris])
