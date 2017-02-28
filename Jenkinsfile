// vim: ft=groovy
node {
    stage('Preparation') {
        // Get some code from the GitHub repository
        git 'https://github.com/UMBC-CMSC447-Spring2017-Team5/college-JUMP.git'
        // Prepare the virtual environment
        sh "make env"
    }

    stage('Distribution') {
        // Build the source package
        def fullname = sh "python3 setup.py --fullname"
        sh "make dist"
        archiveArtifacts 'dist/${fullname}.tar.gz'
    }
}
