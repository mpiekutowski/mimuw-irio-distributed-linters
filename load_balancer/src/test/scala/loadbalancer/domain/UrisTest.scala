package loadbalancer.domain

import munit.FunSuite
import org.http4s.Uri
class UrisTest extends FunSuite {
  test("currentOpt should return first element") {
    // given
    val uris     = getSampleUris(1, 3)
    val expected = Uri.unsafeFromString("http://localhost:8081")

    // when
    val obtained = uris.currentOpt.get

    // then
    assertEquals(obtained, expected)
  }

  test("currentOpt should return None for empty list") {
    // given
    val uris     = Uris.empty()
    val expected = None

    // when
    val obtained = uris.currentOpt

    // then
    assertEquals(obtained, expected)
  }

  test("remove should drop first element") {
    // given
    val uris     = getSampleUris(1, 3)
    val expected = getSampleUris(2, 3)

    // when
    val obtained = uris.remove(Uri.unsafeFromString("http://localhost:8081"))

    // then
    assertEquals(obtained, expected)
  }

  test("add should append next element") {
    // given
    val uris     = getSampleUris(1, 2)
    val expected = getSampleUris(1, 3)

    // when
    val obtained = uris.add(Uri.unsafeFromString("http://localhost:8083"))

    // then
    assertEquals(obtained, expected)
  }

  private def getSampleUris(from: Int, to: Int): Uris = Uris {
    (from to to).map(i => Uri.unsafeFromString(s"http://localhost:808$i")).toVector
  }
}
