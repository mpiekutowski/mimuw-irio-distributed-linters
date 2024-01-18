package loadbalancer.services

import cats.syntax.either.*
import loadbalancer.services.ParseUri.InvalidUri
import munit.FunSuite
import org.http4s.Uri

class ParseUriTest extends FunSuite {
  val parseUri: ParseUri.Impl.type = ParseUri.Impl

  test("Valid URI should be parsed properly") {
    // given
    val uri      = "localhost:8081"
    val expected = Uri.unsafeFromString(uri).asRight

    // when
    val obtained = parseUri(uri)

    // then
    assertEquals(obtained, expected)
  }

  test("Invalid URI should be parsed to InvalidUri(...)") {
    // given
    val uri      = "Surely I'm not a correct URI"
    val expected = InvalidUri(uri).asLeft

    // when
    val obtained = parseUri(uri)

    // then
    assertEquals(obtained, expected)
  }
}
