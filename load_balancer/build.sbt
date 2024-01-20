version := "1.0"

scalaVersion := "3.3.0"

enablePlugins(
  JavaAppPackaging,
  DockerPlugin
)

Compile / mainClass  := Some("loadbalancer.Main")
Docker / packageName := "load_balancer"
dockerBaseImage      := "openjdk:19"

val Http4sVersion          = "0.23.23"
val MunitVersion           = "0.7.29"
val MunitCatsEffectVersion = "1.0.7"
val LogbackVersion         = "1.4.12"
val PureconfigVersion      = "0.17.4"
val CirceVersion           = "0.14.5"

lazy val root = (project in file("."))
  .settings(
    name         := "load-balancer",
    scalaVersion := "3.3.0",
    libraryDependencies ++= Seq(
      "org.http4s"            %% "http4s-ember-server" % Http4sVersion,
      "org.http4s"            %% "http4s-ember-client" % Http4sVersion,
      "org.http4s"            %% "http4s-dsl"          % Http4sVersion,
      "org.scalameta"         %% "munit"               % MunitVersion           % Test,
      "org.typelevel"         %% "munit-cats-effect-3" % MunitCatsEffectVersion % Test,
      "ch.qos.logback"         % "logback-classic"     % LogbackVersion         % Runtime,
      "com.github.pureconfig" %% "pureconfig-core"     % PureconfigVersion,
      "org.http4s"            %% "http4s-circe"        % Http4sVersion,
      "io.circe"              %% "circe-generic"       % CirceVersion
    )
  )
