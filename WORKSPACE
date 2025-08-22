workspace(name = "wikipedia")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

_KOTLIN_COMPILER_VERSION = "1.8.0"

_KOTLIN_COMPILER_SHA = "0bb9419fac9832a56a3a19cad282f8f2d6f1237d2d467dc8dfe9bd4a2a43c42e"

http_archive(
    name = "rules_jvm_external",
    sha256 = "b17d7388feb9bfa7f2fa09031b32707df529f26c91ab9e5d909eb1676badd9a6",
    strip_prefix = "rules_jvm_external-4.5",
    urls = ["https://github.com/bazelbuild/rules_jvm_external/archive/4.5.zip"],
)

load("@rules_jvm_external//:repositories.bzl", "rules_jvm_external_deps")
rules_jvm_external_deps()

load("@rules_jvm_external//:setup.bzl", "rules_jvm_external_setup")
rules_jvm_external_setup()

load("@rules_jvm_external//:defs.bzl", "maven_install")

maven_install(
    artifacts = [
        "androidx.navigation:navigation-compose:2.9.3",
        "androidx.room:room-compiler:2.7.2",
        "androidx.room:room-ktx:2.7.2",
        "androidx.room:room-runtime:2.7.2",
        "com.github.skydoves:balloon:1.6.12",
        "androidx.browser:browser:1.8.0",
        "io.coil-kt.coil3:coil-gif:3.2.0",
        "com.google.android.gms:play-services-wallet:19.4.0",
        "com.google.firebase:firebase-messaging-ktx:24.1.2",
        "com.google.mlkit:language-id:17.0.6",
        "org.apache.commons:commons-lang3:3.18.0",
        "androidx.constraintlayout:constraintlayout:2.2.1",
        "androidx.core:core-ktx:1.16.0",
        "androidx.appcompat:appcompat:1.7.1",
        "com.android.tools:desugar_jdk_libs:2.1.5",
        "androidx.drawerlayout:drawerlayout:1.2.0",
        "com.google.android.flexbox:flexbox:3.0.0",
        "androidx.fragment:fragment-ktx:1.8.8",
        "com.google.gms:google-services:4.4.3",
        "com.android.installreferrer:installreferrer:2.2",
        "org.jsoup:jsoup:1.21.1",
        "junit:junit:4.13.2",
        "org.jetbrains.kotlin:kotlin-serialization:2.1.0",
        "org.jetbrains.kotlin:kotlin-stdlib-jdk8:2.1.0",
        "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.2",
        "org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2",
        "org.jetbrains.kotlinx:kotlinx-serialization-json:1.9.0",
        "com.squareup.leakcanary:leakcanary-android:2.14",
        "com.google.android.material:material:1.12.0",
        "org.wikimedia.metrics:metrics-platform:2.9",
        "com.squareup.okhttp3:okhttp-tls:4.12.0",
        "com.squareup.okhttp3:logging-interceptor:4.12.0",
        "com.squareup.okhttp3:okhttp:4.12.0",
        "androidx.palette:palette-ktx:1.0.0",
        "androidx.paging:paging-runtime-ktx:3.3.6",
        "io.getstream:photoview:1.0.3",
        "com.squareup.leakcanary:plumber-android:2.14",
        "androidx.preference:preference-ktx:1.2.1",
        "androidx.recyclerview:recyclerview:1.4.0",
        "com.squareup.retrofit2:retrofit:2.11.0",
        "com.squareup.retrofit2:converter-kotlinx-serialization:2.11.0",
        "androidx.swiperefreshlayout:swiperefreshlayout:1.1.0",
        "androidx.viewpager2:viewpager2:1.1.0",
        "androidx.work:work-runtime-ktx:2.10.3",
        "androidx.activity:activity-compose:1.10.1",
        "androidx.lifecycle:lifecycle-viewmodel-compose:2.9.2",
        "androidx.compose.material3:material3:1.3.2",
        "androidx.compose.ui:ui:1.8.3",
        "androidx.compose.ui:ui-tooling-preview:1.8.3",
        "androidx.compose.ui:ui-tooling:1.8.3",
        "org.jetbrains.kotlin:kotlin-compose-compiler-plugin-embeddable:2.1.0",
        "org.jetbrains.kotlin:kotlin-parcelize-compiler:2.1.0",
        "org.jetbrains.kotlin:kotlin-parcelize-runtime:2.1.0",
        "androidx.databinding:databinding-runtime:8.9.1",
        "io.coil-kt.coil3:coil-core-android:3.2.0",
        "io.coil-kt.coil3:coil-compose-android:3.2.0",
        "io.coil-kt.coil3:coil-network-okhttp-jvm:3.2.0",
        "io.coil-kt.coil3:coil-svg-android:3.2.0",
        "com.google.protobuf:protobuf-java-util:4.27.2",
    ],
    repositories = [
        "file:///Users/b41z33d/Library/Caches/Coursier/v1/https/repo1.maven.org/maven2",
        "file:///Users/b41z33d/Library/Caches/Coursier/v1/https/maven.google.com",
        "https://repo1.maven.org/maven2",
        "https://maven.google.com",
    ],
)

http_archive(
    name = "build_bazel_rules_android",
    sha256 = "cd06d15dd8bb59926e4d65f9003bfc20f9da4b2519985c27e190cddc8b7a7806",
    strip_prefix = "rules_android-0.1.1",
    urls = ["https://github.com/bazelbuild/rules_android/archive/v0.1.1.zip"],
)

load("@build_bazel_rules_android//android:rules.bzl", "android_sdk_repository")
android_sdk_repository(name = "androidsdk")

rules_kotlin_version = "1.9.0"
rules_kotlin_sha = "5766f1e599acf551aa56f49dab9ab9108269b03c557496c54acaf41f98e2b8d6"

http_archive(
    name = "rules_kotlin",
    urls = ["https://github.com/bazelbuild/rules_kotlin/releases/download/v%s/rules_kotlin-v%s.tar.gz" % (rules_kotlin_version, rules_kotlin_version)],
    sha256 = rules_kotlin_sha,
)

load("@rules_kotlin//kotlin:repositories.bzl", "kotlin_repositories", "kotlinc_version")
kotlin_repositories(
    compiler_release = kotlinc_version(
        release = _KOTLIN_COMPILER_VERSION,
        sha256 = _KOTLIN_COMPILER_SHA,
    ),
)

load("@rules_kotlin//kotlin:core.bzl", "kt_register_toolchains")
kt_register_toolchains()
