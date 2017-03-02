// vim: ft=groovy
node {
    stage('Preparation') {
        // Get some code from the GitHub repository
        git 'https://github.com/UMBC-CMSC447-Spring2017-Team5/college-JUMP.git'
        // Prepare the virtual environment
        sh "make env"

        // Set the build name
        currentBuild.displayName = sh "env/bin/python3 setup.py --version"
    }

    stage('Distribution') {
        // Build the source package
        sh "make clean-dist dist"
        archiveArtifacts 'dist/**.tar.gz'
    }

    stage('Testing') {
        sh "make test"
    }
}
