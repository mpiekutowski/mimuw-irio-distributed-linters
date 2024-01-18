package loadbalancer.domain

import pureconfig.*
import pureconfig.generic.derivation.default.*

final case class Config(
    port: Int,
    host: String
) derives ConfigReader
