package loadbalancer.domain

import munit.FunSuite

import scala.annotation.tailrec
class VersionRoundRobitTest extends FunSuite {
  private val exampleVersionWeights = Map("1.0" -> 3, "2.0" -> 7)

  test("currentOpt should return current version to balance") {
    // given
    val vrr      = VersionRoundRobin.initial(exampleVersionWeights)
    val expected = "1.0"
    // when
    val obtained = vrr.currentOpt().get
    // then
    assertEquals(obtained, expected)
  }

  test("next state should update index when there is more than one version remaining") {
    // given
    val vrr      = VersionRoundRobin.initial(exampleVersionWeights)
    val expected = (1, 1)
    // when
    val obtained = getCurrents(vrr.nextState())
    // then
    assertEquals(obtained, expected)
  }

  test("next state should update weight when there are no more version remaining") {
    // given
    val vrr      = VersionRoundRobin(exampleVersionWeights, 1, 1)
    val expected = (2, 0)
    // when
    val obtained = getCurrents(vrr.nextState())
    // then
    assertEquals(obtained, expected)
  }

  test("next state should reset vrr when the whole round has been finished") {
    // given
    val vrr      = VersionRoundRobin(exampleVersionWeights, 7, 0)
    val expected = (1, 0)
    // when
    val obtained = getCurrents(vrr.nextState())
    // then
    assertEquals(obtained, expected)
  }

  test(
    "VersionRoundRobin should distribute ratio properly for different weights and many requests"
  ) {
    // given
    val vrr = VersionRoundRobin.initial(exampleVersionWeights)
    val expectedRequests =
      ((1 to 3).flatMap(_ => List("1.0", "2.0")) ++ (1 to 4).flatMap(_ => List("2.0"))).toList
    val expectedCurrents = (1, 0)
    // when
    val (obtainedRequests, obtainedVrr) = callRequests(10, vrr, List())
    // then
    assertEquals(expectedRequests, obtainedRequests)
    assertEquals(expectedCurrents, getCurrents(obtainedVrr))
  }

  private def getCurrents(vrr: VersionRoundRobin): (Int, Int) =
    (vrr.currentWeight, vrr.currentIndex)

  @tailrec
  private def callRequests(
      remaining: Int,
      vrr: VersionRoundRobin,
      acc: List[String]
  ): (List[String], VersionRoundRobin) =
    remaining match
      case 0 => (acc, vrr)
      case n => callRequests(n - 1, vrr.nextState(), acc :+ vrr.currentOpt().get)
}
