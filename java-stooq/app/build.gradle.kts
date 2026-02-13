plugins {
    java
    // ZMIANA: Używamy naprawionego forka, bo oryginał johnrengelman jest porzucony
    id("io.github.goooler.shadow") version "8.1.8"
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.squareup.okhttp3:okhttp:4.11.0")
    implementation("com.opencsv:opencsv:5.7.1")
    implementation("org.knowm.xchart:xchart:3.8.2")
    testImplementation("org.junit.jupiter:junit-jupiter:5.12.1")
}

testing {
    suites {
        val test by getting(JvmTestSuite::class) {
            useJUnitJupiter("5.12.1")
        }
    }
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(23))
    }
}

tasks.withType<JavaCompile> {
    options.encoding = "UTF-8"
}

// Konfiguracja budowania pliku z bibliotekami
tasks.shadowJar {
    archiveBaseName.set("gpw-analizer")
    archiveClassifier.set("") 
    
    manifest {
        attributes(mapOf("Main-Class" to "org.example.App")) 
    }
    
    // Kluczowe przy bibliotekach kryptograficznych/podpisanych
    exclude("META-INF/*.SF", "META-INF/*.DSA", "META-INF/*.RSA")
    
    // Rozwiązanie konfliktu plików licencji (częsty błąd przy pakowaniu)
    mergeServiceFiles()
}

tasks.jar {
    manifest {
        attributes(mapOf("Main-Class" to "org.example.App"))
    }
}

tasks.build {
    dependsOn(tasks.shadowJar)
}