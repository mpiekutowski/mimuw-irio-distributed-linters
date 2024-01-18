package loadbalancer.errors

object Config {
  type InvalidConfig = InvalidConfig.type

  case object InvalidConfig extends Throwable {
    override def getMessage: String =
      "Invalid config"
  }

}
