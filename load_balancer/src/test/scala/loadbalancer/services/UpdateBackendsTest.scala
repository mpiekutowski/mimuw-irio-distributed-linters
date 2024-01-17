package loadbalancer.services

import cats.effect.IO
import loadbalancer.domain.{Backends, Uris}
import loadbalancer.services.UpdateBackends.BackendOperation.{Add, Remove}
import munit.CatsEffectSuite
import org.http4s.Uri

class UpdateBackendsTest extends CatsEffectSuite {
  private val updateBackends = UpdateBackends.Impl
  private val sampleUri      = Uri.unsafeFromString("http://localhost:8083")
  private val initialUris    = Vector("localhost:8081", "localhost:8082").map(Uri.unsafeFromString)

  test("Should return uris with added uri") {
    // given
    val uris = Uris(initialUris)
    val expected = Uris(initialUris :+ sampleUri)

    // when
    val obtained = for
      ref <- IO.ref(uris)
      updated <- updateBackends(Backends(ref), sampleUri, Add)
    yield updated

    // then
    assertIO(obtained, expected)

  }

  test("Should return uris without removed uri") {
    // given
    val uris = Uris(initialUris :+ sampleUri)
    val expected = Uris(initialUris)

    // when
    val obtained = for
      ref <- IO.ref(uris)
      updated <- updateBackends(Backends(ref), sampleUri, Remove)
    yield updated

    // then
    assertIO(obtained, expected)
  }
}
