package loadbalancer.domain

import cats.effect.{IO, Ref}

final case class VersionRoundRobinRef(roundRobin: Ref[IO, VersionRoundRobin])
final case class VersionRoundRobin(
    versionWeights: Map[String, Int],
    currentWeight: Int,
    currentIndex: Int
) {
  def currentOpt(): Option[String] = currentVersions().lift(currentIndex)

  private def currentVersions(): List[String] =
    versionWeights.filter((version, weight) => weight >= currentWeight).keys.toList

  def nextState(): VersionRoundRobin = {
    if (currentIndex + 1 >= currentVersions().size)
      nextWeight()
    else
      copy(versionWeights, currentWeight, currentIndex + 1)
  }

  private def nextWeight(): VersionRoundRobin =
    if (currentWeight + 1 > versionWeights.values.maxOption.getOrElse(0)) {
      VersionRoundRobin.initial(versionWeights)
    } else {
      copy(versionWeights, currentWeight + 1, currentIndex = 0)
    }
}

object VersionRoundRobin {
  def initial(versionWeight: Map[String, Int]): VersionRoundRobin =
    VersionRoundRobin(versionWeight, currentWeight = 1, currentIndex = 0)
}
