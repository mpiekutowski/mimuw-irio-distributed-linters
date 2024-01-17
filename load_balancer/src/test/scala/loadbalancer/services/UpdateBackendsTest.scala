package loadbalancer.services

import cats.effect.IO
import loadbalancer.domain.{Backends, Uris}
import loadbalancer.services.UpdateBackends.BackendOperation.{Add, Remove}
import munit.CatsEffectSuite
import org.http4s.Uri

class UpdateBackendsTest extends CatsEffectSuite {
  private val updateBackends = UpdateBackends.Impl
  private val sampleUri      = Uri.unsafeFromString("http://localhost:8083")
  private val initialUrls    = Vector("localhost:8081", "localhost:8082").map(Uri.unsafeFromString)

  test("Should return urls with added url") {
    // given
    val urls = Uris(initialUrls)
    val expected = Uris(initialUrls :+ sampleUri)

    // when
    val obtained = for
      ref <- IO.ref(urls)
      updated <- updateBackends(Backends(ref), sampleUri, Add)
    yield updated

    // then
    assertIO(obtained, expected)

  }

  test("Should return urls without removed url") {
    // given
    val urls = Uris(initialUrls :+ sampleUri)
    val expected = Uris(initialUrls)

    // when
    val obtained = for
      ref <- IO.ref(urls)
      updated <- updateBackends(Backends(ref), sampleUri, Remove)
    yield updated

    // then
    assertIO(obtained, expected)
  }
}
