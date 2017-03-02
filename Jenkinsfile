// vim: ft=groovy
node {
    stage('Preparation') {
        // Get some code from the GitHub repository
        git 'https://github.com/UMBC-CMSC447-Spring2017-Team5/college-JUMP.git'
        // Prepare the virtual environment
        sh "make env"

        // Set the build name
        def pkgVersion = sh (
            script: "env/bin/python3 setup.py --version",
            returnStdout: true
        ).trim()
        def pkgFullname = sh (
            script: "env/bin/python3 setup.py --fullname",
            returnStdout: true
        ).trim()

        currentBuild.displayName = pkgVersion
    }

    stage('Distribution') {
        // Build the source package
        sh "make dist"
        archiveArtifacts "dist/${pkgFullname}.tar.gz"
    }

    stage('Testing') {
        try {
            sh "make test"
        } catch (Exception e) {
            currentBuild.result = 'UNSTABLE'
        }
    }

    stage('Deployment') {
        sh '''
            sudo pip3 -H install contrib/${pkgFullname}tar.gz
            sudo systemctl restart collegejump
        '''
    }
}
