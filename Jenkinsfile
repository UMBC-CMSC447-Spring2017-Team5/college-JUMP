// vim: ft=groovy
node {
    def pkgVersion
    def pkgFullname

    stage('Preparation') {
        // Get some code from the GitHub repository
        git 'https://github.com/UMBC-CMSC447-Spring2017-Team5/college-JUMP.git'
        // Prepare the virtual environment
        sh "make env"

        // Set the build name
        pkgVersion = sh (
            script: "env/bin/python3 setup.py --version",
            returnStdout: true
        ).trim()
        pkgFullname = sh (
            script: "env/bin/python3 setup.py --fullname",
            returnStdout: true
        ).trim()

        currentBuild.displayName = pkgVersion
    }

    stage('Packaging') {
        // Build the source package
        sh "make dist"
        archiveArtifacts "dist/${pkgFullname}.tar.gz"
    }

    stage('Testing') {
        try {
            sh "make test"
            currentBuild.result = 'SUCCESS'
            currentBuild.buildstatus_message = "Tests passing"
        } catch (Exception e) {
            currentBuild.result = 'UNSTABLE'
            currentBuild.buildstatus_message = "Tests failing"
        }
        junit 'coverage.xml'

        setBuildStatus(currentBuild.buildstatus_message, currentBuild.result)
    }

    stage('Deployment') {
        sh """
            sudo -H pip3 install --upgrade \"dist/${pkgFullname}.tar.gz\"
            sudo -H systemctl restart collegejump
        """
    }
}

void setBuildStatus(String message, String state) {
  step([
      $class: "GitHubCommitStatusSetter",
      reposSource: [
        $class: "ManuallyEnteredRepositorySource",
        url: "https://github.com/UMBC-CMSC447-Spring2017-Team5/college-JUMP"
      ],
      contextSource: [
        $class: "ManuallyEnteredCommitContextSource",
        context: "ci/jenkins/build-status"
      ],
      errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
      statusResultSource: [
        $class: "ConditionalStatusResultSource",
        results: [[$class: "AnyBuildResult", message: message, state: state]]
      ]
  ]);
}
