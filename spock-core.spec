Name:		spock-core
Version:	2.4.groovy.4.0
Release:	1
Summary:	Spock specification framework
Group:		Development/Java
License:	Apache-2.0
URL:		https://spockframework.org/
# Tag spock-2.4, Groovy 4 variant. The catalog coordinate is
# org.spockframework:spock-core 2.4-groovy-4.0. RPM rejects two hyphens,
# so the package version is dotted. norm() makes the two strings equal.
# The Gradle wrapper jar is not in this archive. Java sources are
# compiled with javac. Groovy sources are compiled with
# FileSystemCompiler. The Gradle tool is not invoked.
Source0:	spock-core-%{version}.tar.gz
# Mockito 5.24's createMock requires MockHandler<T> to match
# MockCreationSettings<T>. Upstream builds a wildcard settings object
# and passes SpockMockHandler, which is MockHandler<Object>.
Patch0:		spock-core-mockito-5.24.patch

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	apache-groovy >= 4.0.33-2
BuildRequires:	picocli
BuildRequires:	jansi
BuildRequires:	antlr4
BuildRequires:	objectweb-asm
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	mvn(org.junit.platform:junit-platform-commons) = 6.0.3
BuildRequires:	mvn(org.junit.platform:junit-platform-engine) = 6.0.3
BuildRequires:	mvn(org.junit.platform:junit-platform-launcher) = 6.0.3
BuildRequires:	mvn(org.junit.platform:junit-platform-testkit) = 6.0.3
BuildRequires:	mvn(org.opentest4j:opentest4j)
BuildRequires:	mvn(org.hamcrest:hamcrest)
BuildRequires:	mvn(io.leangen.geantyref:geantyref) = 1.3.16
BuildRequires:	mvn(org.jetbrains:annotations)
BuildRequires:	mvn(net.bytebuddy:byte-buddy)
BuildRequires:	mvn(cglib:cglib) = 3.3.0
BuildRequires:	mvn(org.objenesis:objenesis) = 3.6
BuildRequires:	mvn(org.mockito:mockito-core) = 5.24.0
BuildRequires:	mvn(org.assertj:assertj-core)
BuildRequires:	mvn(org.apiguardian:apiguardian-api)
BuildRequires:	mvn(org.jspecify:jspecify)

%description
org.spockframework:spock-core for Groovy 4. EmbeddedSpecRunner compiles
a specification body and runs it through EngineTestKit. The Java
sources are release 8 because Specification declares a public field
named underscore, which is a keyword from Java 9. The seven Groovy
sources are bytecode 11. The runtime properties file keeps upstream's
version string 2.4-groovy-4.0.

%prep
%autosetup -n spock-spock-2.4 -p1
find . -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries.list
find . -type d -name '*.jar' -print >> binaries.list
if [ -s binaries.list ]; then
	cat binaries.list
	exit 1
fi
find spock-core/src/main/java -name '*.java' | sort > java.list
find spock-core/src/main/groovy -name '*.groovy' | sort > groovy.list
test "$(wc -l < java.list)" -eq 525
test "$(wc -l < groovy.list)" -eq 7
grep -qx 'version=@version@' spock-core/src/main/resources/org/spockframework/util/SpockReleaseInfo.properties

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
CP=%{_javadir}/apache-groovy.jar
for extra in \
	%{_javadir}/apache-groovy-xml.jar \
	%{_javadir}/apache-groovy-json.jar \
	%{_javadir}/apache-groovy-templates.jar \
	%{_javadir}/antlr4-runtime.jar \
	%{_javadir}/asm.jar \
	%{_javadir}/asm-commons.jar \
	%{_javadir}/asm-tree.jar \
	%{_javadir}/asm-util.jar \
	%{_javadir}/picocli.jar \
	/usr/lib/java/jansi/jansi.jar \
	%{_javadir}/junit-platform-commons-6.0.3.jar \
	%{_javadir}/junit-platform-engine-6.0.3.jar \
	%{_javadir}/junit-platform-launcher-6.0.3.jar \
	%{_javadir}/junit-platform-testkit-6.0.3.jar \
	%{_javadir}/opentest4j/opentest4j.jar \
	%{_javadir}/hamcrest/hamcrest.jar \
	%{_javadir}/org.jetbrains.annotations.jar \
	%{_javadir}/geantyref.jar \
	%{_javadir}/byte-buddy.jar \
	%{_javadir}/cglib.jar \
	%{_javadir}/objenesis.jar \
	%{_javadir}/mockito.jar \
	%{_javadir}/apiguardian-api.jar \
	%{_javadir}/jspecify.jar \
	%{_javadir}/assertj-core.jar
do
	test -s "$extra"
	CP="$CP:$extra"
done
mkdir -p classes
javac --release 8 -encoding UTF-8 -Xlint:-options -proc:none -cp "$CP" -d classes @java.list
test "$(find classes -name '*.class' | wc -l)" -eq 652
javap -v -classpath classes org.spockframework.runtime.SpockEngine | grep -F -q 'major version: 52'
java -Dgroovy.target.bytecode=11 -cp "$CP:classes" org.codehaus.groovy.tools.FileSystemCompiler \
	--classpath "$CP:classes" -d classes @groovy.list
test "$(find classes -name '*.class' | wc -l)" -eq 747
javap -v -classpath classes spock.util.EmbeddedSpecRunner | grep -F -q 'major version: 55'
cp -a spock-core/src/main/resources/. classes/
sed -i \
	-e 's/@version@/2.4-groovy-4.0/' \
	-e 's/@minGroovyVersion@/4.0.0/' \
	-e 's/@maxGroovyVersion@/4.9.99/' \
	classes/org/spockframework/util/SpockReleaseInfo.properties
printf '\n' >> classes/org/spockframework/util/SpockReleaseInfo.properties
grep -qx 'version=2.4-groovy-4.0' classes/org/spockframework/util/SpockReleaseInfo.properties
grep -qx 'minGroovyVersion=4.0.0' classes/org/spockframework/util/SpockReleaseInfo.properties
grep -qx 'maxGroovyVersion=4.9.99' classes/org/spockframework/util/SpockReleaseInfo.properties
if grep -F -q '@' classes/org/spockframework/util/SpockReleaseInfo.properties; then
	exit 1
fi
test -s classes/META-INF/services/org.junit.platform.engine.TestEngine
grep -qx 'org.spockframework.runtime.SpockEngine' classes/META-INF/services/org.junit.platform.engine.TestEngine
printf '%s\n' 'Manifest-Version: 1.0' 'Automatic-Module-Name: org.spockframework.core' > manifest.mf
jar cfm spock-core.jar manifest.mf -C classes .
jar i spock-core.jar
jar tf spock-core.jar | grep -F -qx 'spock/util/EmbeddedSpecRunner.class'
jar tf spock-core.jar | grep -F -qx 'org/spockframework/util/SpockReleaseInfo.properties'
jar tf spock-core.jar | grep -F -qx 'META-INF/services/org.junit.platform.engine.TestEngine'
desc=$(jar --describe-module --file spock-core.jar)
printf '%s\n' "$desc" | grep -F -q 'org.spockframework.core'
if printf '%s\n' "$desc" | grep -F -q 'Unable'; then
	printf '%s\n' "$desc"
	exit 1
fi

cat > spock-core.pom << 'END'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.spockframework</groupId>
  <artifactId>spock-core</artifactId>
  <version>2.4.groovy.4.0</version>
  <name>Spock Framework - Core Module</name>
  <description>Specification framework for Java and Groovy applications.</description>
  <url>https://spockframework.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.apache.groovy</groupId>
      <artifactId>groovy</artifactId>
      <version>4.0.33</version>
    </dependency>
    <dependency>
      <groupId>org.junit.platform</groupId>
      <artifactId>junit-platform-commons</artifactId>
      <version>6.0.3</version>
    </dependency>
    <dependency>
      <groupId>org.junit.platform</groupId>
      <artifactId>junit-platform-engine</artifactId>
      <version>6.0.3</version>
    </dependency>
    <dependency>
      <groupId>org.junit.platform</groupId>
      <artifactId>junit-platform-launcher</artifactId>
      <version>6.0.3</version>
    </dependency>
    <dependency>
      <groupId>org.junit.platform</groupId>
      <artifactId>junit-platform-testkit</artifactId>
      <version>6.0.3</version>
    </dependency>
    <dependency>
      <groupId>org.opentest4j</groupId>
      <artifactId>opentest4j</artifactId>
      <version>1.3.0</version>
    </dependency>
    <dependency>
      <groupId>org.hamcrest</groupId>
      <artifactId>hamcrest</artifactId>
      <version>3.0</version>
    </dependency>
    <dependency>
      <groupId>io.leangen.geantyref</groupId>
      <artifactId>geantyref</artifactId>
      <version>1.3.16</version>
    </dependency>
    <dependency>
      <groupId>org.ow2.asm</groupId>
      <artifactId>asm</artifactId>
      <version>9.11.1</version>
    </dependency>
    <dependency>
      <groupId>org.ow2.asm</groupId>
      <artifactId>asm-util</artifactId>
      <version>9.11.1</version>
    </dependency>
    <dependency>
      <groupId>net.bytebuddy</groupId>
      <artifactId>byte-buddy</artifactId>
      <version>1.18.17</version>
    </dependency>
    <dependency>
      <groupId>cglib</groupId>
      <artifactId>cglib</artifactId>
      <version>3.3.0</version>
    </dependency>
    <dependency>
      <groupId>org.objenesis</groupId>
      <artifactId>objenesis</artifactId>
      <version>3.6</version>
    </dependency>
    <dependency>
      <groupId>org.mockito</groupId>
      <artifactId>mockito-core</artifactId>
      <version>5.24.0</version>
    </dependency>
  </dependencies>
</project>
END

%install
set -eo pipefail
sysjar install --buildroot %{buildroot} \
	--artifact spock-core.pom:spock-core.jar \
	--file-name spock-core \
	--filelist .mfiles
idx="%{buildroot}/usr/share/sysjar/index/org.spockframework/spock-core.sysjar"
test -s "$idx"
grep -F -q '"version": "%{version}"' "$idx"
grep -F -q '"artifactId": "spock-core"' "$idx"
test -s %{buildroot}%{_javadir}/spock-core.jar

%check
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
JAR=%{buildroot}%{_javadir}/spock-core.jar
test -s "$JAR"
CP=%{_javadir}/apache-groovy.jar
for extra in \
	%{_javadir}/apache-groovy-xml.jar \
	%{_javadir}/apache-groovy-json.jar \
	%{_javadir}/apache-groovy-templates.jar \
	%{_javadir}/antlr4-runtime.jar \
	%{_javadir}/asm.jar \
	%{_javadir}/asm-commons.jar \
	%{_javadir}/asm-tree.jar \
	%{_javadir}/asm-util.jar \
	%{_javadir}/picocli.jar \
	/usr/lib/java/jansi/jansi.jar \
	%{_javadir}/junit-platform-commons-6.0.3.jar \
	%{_javadir}/junit-platform-engine-6.0.3.jar \
	%{_javadir}/junit-platform-launcher-6.0.3.jar \
	%{_javadir}/junit-platform-testkit-6.0.3.jar \
	%{_javadir}/opentest4j/opentest4j.jar \
	%{_javadir}/hamcrest/hamcrest.jar \
	%{_javadir}/org.jetbrains.annotations.jar \
	%{_javadir}/geantyref.jar \
	%{_javadir}/byte-buddy.jar \
	%{_javadir}/cglib.jar \
	%{_javadir}/objenesis.jar \
	%{_javadir}/mockito.jar \
	%{_javadir}/apiguardian-api.jar \
	%{_javadir}/jspecify.jar \
	%{_javadir}/assertj-core.jar
do
	test -s "$extra"
	CP="$CP:$extra"
done
mkdir -p check
cat > check/Smoke.groovy << 'EOF'
import spock.util.EmbeddedSpecRunner

def runner = new EmbeddedSpecRunner()
def results = runner.runSpecBody("def 'adds'() { expect: 1 + 1 == 2 }")
def count = results.testsSucceededCount
if (count != 1L) {
    throw new AssertionError(String.valueOf(count))
}
println "spock_ok ${count}"
EOF
java -Dgroovy.target.bytecode=11 -cp "$CP" org.codehaus.groovy.tools.FileSystemCompiler \
	--classpath "$JAR:$CP" -d check check/Smoke.groovy
"$JAVA_HOME/bin/java" -cp "check:$JAR:$CP" Smoke > check/out.txt
cat check/out.txt
grep -F -qx 'spock_ok 1' check/out.txt

%files -f .mfiles
%doc README.adoc
%license LICENSE NOTICE
