package loadbalancer.domain

import munit.FunSuite
import org.http4s.Uri
class UrisTest extends FunSuite {
  private val backendKind = BackendKind("java", "1.0")

  test("currentOpt should return first element of kind") {
    // given
    val uris     = getSampleUris(1, 3)
    val expected = Uri.unsafeFromString("http://localhost:8081")

    // when
    val obtained = uris.currentOpt(backendKind).get

    // then
    assertEquals(obtained, expected)
  }

  test("currentOpt should return None for empty list") {
    // given
    val uris     = Uris.empty()
    val expected = None

    // when
    val obtained = uris.currentOpt(backendKind)

    // then
    assertEquals(obtained, expected)
  }

  test("remove should remove specified element from kind") {
    // given
    val uris     = getSampleUris(1, 3)
    val expected = getSampleUris(2, 3)

    // when
    val obtained = uris.remove(Uri.unsafeFromString("http://localhost:8081"))

    // then
    assertEquals(obtained, expected)
  }

  test("add should add specified element to kind") {
    // given
    val uris     = getSampleUris(1, 2)
    val expected = getSampleUris(1, 3)

    // when
    val obtained = uris.add(backendKind, Uri.unsafeFromString("http://localhost:8083"))

    // then
    assertEquals(obtained, expected)
  }

  test("spin should move first element to last position") {
    // given
    val uris = getSampleUris(1, 4)
    val expected =
      Uris(
        Map(
          backendKind -> Vector(getSampleUri(2), getSampleUri(3), getSampleUri(4), getSampleUri(1))
        )
      )

    // when
    val obtained = uris.spin(backendKind)

    // then
    assertEquals(obtained, expected)
  }

  private def getSampleUris(from: Int, to: Int): Uris =
    Uris(Map(backendKind -> (from to to).map(getSampleUri).toVector))

  private def getSampleUri(i: Int): Uri =
    Uri.unsafeFromString(s"http://localhost:808$i")
}
