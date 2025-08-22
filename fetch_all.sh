#!/bin/zsh
set -euo pipefail

REPOS=(-r https://repo1.maven.org/maven2 -r https://maven.google.com)

COMMON_OVERRIDES=(
  -V org.jetbrains.kotlin:kotlin-stdlib:2.1.0 -V org.jetbrains.kotlin:kotlin-stdlib-common:2.1.0 -V org.jetbrains.kotlin:kotlin-stdlib-jdk7:2.1.0 -V org.jetbrains.kotlin:kotlin-stdlib-jdk8:2.1.0 -V androidx.lifecycle:lifecycle-common:2.9.2 -V androidx.lifecycle:lifecycle-runtime:2.9.2 -V androidx.emoji2:emoji2:1.4.0 -V androidx.collection:collection:1.5.0 -V androidx.compose.runtime:runtime:1.8.3 -V androidx.compose.ui:ui-geometry:1.8.3 -V androidx.compose.ui:ui-graphics:1.8.3 -V androidx.compose.ui:ui-text:1.8.3 -V androidx.compose.ui:ui-unit:1.8.3 -V androidx.compose.ui:ui-util:1.8.3 -V androidx.lifecycle:lifecycle-viewmodel:2.9.2 -V androidx.savedstate:savedstate:1.3.1 -V androidx.collection:collection-jvm:1.5.0 -V androidx.compose.animation:animation-core:1.8.3
)

COMPLETED=(
  "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.2"
  "org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2"
  "org.jetbrains.kotlinx:kotlinx-serialization-json:1.9.0"
  "com.squareup.leakcanary:leakcanary-android:2.14,type=aar"
  "com.google.android.material:material:1.12.0,type=aar"
  "org.wikimedia.metrics:metrics-platform:2.9"
  "com.squareup.okhttp3:okhttp-tls:4.12.0"
  "com.squareup.okhttp3:logging-interceptor:4.12.0"
  "com.squareup.okhttp3:okhttp:4.12.0"
  "androidx.palette:palette-ktx:1.0.0,type=aar"
  "androidx.paging:paging-runtime-ktx:3.3.6,type=aar"
  "io.getstream:photoview:1.0.3,type=aar"
  "com.squareup.leakcanary:plumber-android:2.14,type=aar"
  "androidx.preference:preference-ktx:1.2.1,type=aar"
  "androidx.recyclerview:recyclerview:1.4.0,type=aar"
  "com.squareup.retrofit2:retrofit:2.11.0"
  "com.squareup.retrofit2:converter-kotlinx-serialization:2.11.0"
  "androidx.swiperefreshlayout:swiperefreshlayout:1.1.0,type=aar"
  "androidx.viewpager2:viewpager2:1.1.0,type=aar"
  "androidx.work:work-runtime-ktx:2.10.3,type=aar"
  "androidx.activity:activity-compose:1.10.1,type=aar"
  "androidx.lifecycle:lifecycle-viewmodel-compose:2.9.2,type=aar"
  "androidx.compose.material3:material3:1.3.2,type=aar"
  "androidx.compose.ui:ui:1.8.3,type=aar"
  "androidx.compose.ui:ui-tooling-preview:1.8.3,type=aar"
  "androidx.compose.ui:ui-tooling:1.8.3,type=aar"
  "org.jetbrains.kotlin:kotlin-compose-compiler-plugin-embeddable:2.1.0"
  "org.jetbrains.kotlin:kotlin-parcelize-compiler:2.1.0"
  "org.jetbrains.kotlin:kotlin-parcelize-runtime:2.1.0"
  "androidx.databinding:databinding-runtime:8.9.1,type=aar"
  "io.coil-kt.coil3:coil-core-android:3.2.0,type=aar"
  "io.coil-kt.coil3:coil-compose-android:3.2.0,type=aar"
  "io.coil-kt.coil3:coil-network-okhttp-jvm:3.2.0"
  "io.coil-kt.coil3:coil-svg-android:3.2.0,type=aar"
)

ARTIFACTS=(
  "org.maplibre.gl:android-sdk:11.13.0,type=aar"
  "org.maplibre.gl:android-plugin-annotation-v9:3.0.2,type=aar"
  "androidx.navigation:navigation-compose:2.9.3,type=aar"
  "androidx.room:room-compiler:2.7.2"
  "androidx.room:room-ktx:2.7.2,type=aar"
  "androidx.room:room-runtime:2.7.2,type=aar"
  "com.github.skydoves:balloon:1.6.12,type=aar"
  "androidx.browser:browser:1.8.0,type=aar"
  "io.coil-kt.coil3:coil-gif:3.2.0,type=aar"
  "com.google.android.gms:play-services-wallet:19.4.0,type=aar"
  "com.google.firebase:firebase-messaging-ktx:24.1.2,type=aar"
  "com.google.mlkit:language-id:17.0.6,type=aar"
  "org.apache.commons:commons-lang3:3.18.0"
  "androidx.constraintlayout:constraintlayout:2.2.1,type=aar"
  "androidx.core:core-ktx:1.16.0,type=aar"
  "androidx.appcompat:appcompat:1.7.1,type=aar"
  "com.android.tools:desugar_jdk_libs:2.1.5"
  "androidx.drawerlayout:drawerlayout:1.2.0,type=aar"
  "com.google.android.flexbox:flexbox:3.0.0,type=aar"
  "androidx.fragment:fragment-ktx:1.8.8,type=aar"
  "com.google.gms:google-services:4.4.3"
  "com.android.installreferrer:installreferrer:2.2,type=aar"
  "org.jsoup:jsoup:1.21.1"
  "junit:junit:4.13.2"
  "org.jetbrains.kotlin:kotlin-serialization:2.1.0"
  "org.jetbrains.kotlin:kotlin-stdlib-jdk8:2.1.0"
)

for artifact in "${COMPLETED[@]}"; do
  echo "Fetching $artifact ..."
  eval coursier fetch $artifact "${REPOS[@]}" "${COMMON_OVERRIDES[@]} --artifact-type=aar,jar,pom" \
    || { echo "❌ Failed: $artifact"; exit 1; }
done

echo "✅ All artifacts fetched into Coursier cache."
