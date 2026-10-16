//
//  Tests_iOSLaunchTests.swift
//  Tests iOS
//
//  Created by Evgeny Poberezkin on 17/01/2022.
//

import XCTest

class Tests_iOSLaunchTests: XCTestCase {

    override class var runsForEachTargetApplicationUIConfiguration: Bool {
        // Preserve the upstream matrix unless the owner-approved first-build profile is explicit.
        ProcessInfo.processInfo.environment["TAVERNA_UI_PROFILE"] != "first-build"
    }

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testLaunch() throws {
        let session = try TavernaUITestSession()
        let app = session.app
        try session.launch()

        // Insert steps here to perform after app launch but before taking a screenshot,
        // such as logging into a test account or navigating somewhere in the app

        let attachment = XCTAttachment(screenshot: app.screenshot())
        attachment.name = "Launch Screen"
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
