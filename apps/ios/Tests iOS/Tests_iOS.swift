//
//  Tests_iOS.swift
//  Tests iOS
//
//  Created by Evgeny Poberezkin on 17/01/2022.
//

import XCTest
import CryptoKit
import Darwin

class Tests_iOS: XCTestCase {

    override func setUpWithError() throws {
        // Put setup code here. This method is called before the invocation of each test method in the class.

        // In UI tests it is usually best to stop immediately when a failure occurs.
        continueAfterFailure = false

        // In UI tests it’s important to set the initial state - such as interface orientation - required for your tests before they run. The setUp method is a good place to do this.
    }

    override func tearDownWithError() throws {
        // Put teardown code here. This method is called after the invocation of each test method in the class.
    }

    func testExample() throws {
        // UI tests must launch the application that they test.
        let session = try TavernaUITestSession()
        try session.launch()

        // Use recording to get started writing UI tests.
        // Use XCTAssert and related functions to verify your tests produce the correct results.
    }

    func testLaunchPerformance() throws {
        if #available(macOS 10.15, iOS 13.0, tvOS 13.0, watchOS 7.0, *) {
            // This measures how long it takes to launch your application.
            let session = try TavernaUITestSession()
            measure(metrics: [XCTApplicationLaunchMetric()]) {
                do {
                    try session.launch()
                } catch {
                    XCTFail("Guarded launch failed: \(error)")
                }
            }
        }
    }

    func testFirstBuildOnboarding() throws {
        let session = try TavernaUITestSession()
        let app = session.app
        app.launchArguments += ["-AppleLanguages", "(en)", "-AppleLocale", "en_US"]
        let launchedAt = Date()
        try session.launch()
        let getStarted = app.buttons["Get started"]
        XCTAssertTrue(getStarted.waitForExistence(timeout: max(0, 30 - Date().timeIntervalSince(launchedAt))))
        XCTAssertTrue(getStarted.isHittable, "Get started must be visible")
        XCTAssertTrue(getStarted.isEnabled)
        XCTAssertLessThanOrEqual(Date().timeIntervalSince(launchedAt), 30)
        let initial = XCTAttachment(screenshot: app.screenshot())
        initial.name = "Get started"
        initial.lifetime = .keepAlways
        add(initial)

        let tappedAt = Date()
        getStarted.tap()
        let profile = app.staticTexts["Your profile"]
        XCTAssertTrue(profile.waitForExistence(timeout: max(0, 30 - Date().timeIntervalSince(tappedAt))))
        for _ in 0..<5 {
            if profile.isHittable || Date().timeIntervalSince(tappedAt) >= 30 { break }
            app.scrollViews.firstMatch.swipeDown()
        }
        XCTAssertTrue(profile.isHittable, "Your profile must be visible")
        XCTAssertLessThanOrEqual(Date().timeIntervalSince(tappedAt), 30)
        let destination = XCTAttachment(screenshot: app.screenshot())
        destination.name = "Your profile, without submitting"
        destination.lifetime = .keepAlways
        add(destination)
    }
}
