CYBERSTAR — Android APK build package

The goal is a normal Android APK: install Cyberstar and run it directly,
without Pydroid 3.

IMPORTANT:
This ZIP is a build project, not itself an APK. Android packaging requires
a build environment. The included GitHub Actions workflow builds the APK
automatically in the cloud.

FASTEST ROUTE
1. Create/sign in to a GitHub account.
2. Create a new repository.
3. Upload all files in this folder.
4. Push them to the main branch.
5. Open GitHub -> Actions -> Build Cyberstar APK.
6. Run the workflow.
7. Download the "Cyberstar-APK" artifact.
8. Extract the APK and install it on the phone.

LOCAL BUILD (computer)
Install Buildozer and run:
    buildozer android debug

The resulting APK will be in:
    bin/

The app requests INTERNET permission because Cyberstar performs public-web
searches. It does not bypass private accounts or access controls.

If you only have an Android phone, the included GitHub Actions route avoids
installing Pydroid 3 as the runtime for the finished app.
