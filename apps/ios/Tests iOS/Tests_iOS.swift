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

// Local first-build instrumentation; never linked into the distributed app.
struct TavernaUITestSession {
    let app = XCUIApplication()
    private let root: URL
    private let files: [String: String]
    private let log: URL

    private enum PreparationError: Error {
        case invalid(String)
    }

    private struct GuardEvent: Decodable {
        let pid: Int
        let executable: String
        let phase: String
        let ipv4_errno: Int
        let ipv6_errno: Int
        let loopback: Bool
    }

    init() throws {
        let env = ProcessInfo.processInfo.environment
        let profile = env["TAVERNA_UI_PROFILE"] ?? "full-matrix"
        guard ["first-build", "full-matrix"].contains(profile) else {
            throw PreparationError.invalid("Unknown UI profile: \(profile)")
        }
        if profile == "first-build" {
            XCUIDevice.shared.orientation = .portrait
            XCTAssertEqual(XCUIDevice.shared.orientation, .portrait)
            app.launchArguments += ["-AppleLanguages", "(en)", "-AppleLocale", "en_US", "-AppleInterfaceStyle", "Light"]
        }
        func required(_ key: String) throws -> String {
            guard let value = env[key], !value.isEmpty else {
                throw PreparationError.invalid("Missing \(key); use the isolated first-build procedure")
            }
            return value
        }
        let checkout = URL(fileURLWithPath: try required("TAVERNA_UI_ROOT")).resolvingSymlinksInPath()
        let compiledCheckout = URL(fileURLWithPath: #filePath)
            .deletingLastPathComponent().deletingLastPathComponent()
            .deletingLastPathComponent().deletingLastPathComponent().resolvingSymlinksInPath()
        guard checkout == compiledCheckout else {
            throw PreparationError.invalid("Test environment belongs to another worktree")
        }
        root = checkout
        let manifestURL = URL(fileURLWithPath: try required("TAVERNA_GUARD_MANIFEST"))
        try Self.requireOwned(manifestURL, root: checkout)
        files = try JSONDecoder().decode([String: String].self, from: Data(contentsOf: manifestURL))
        let names = Set(files.keys.map { URL(fileURLWithPath: $0).lastPathComponent })
        guard files.count == 4, names == Set(["host-sandbox.c", "process-guard.c", "host-sandbox", "process-guard.dylib"]) else {
            throw PreparationError.invalid("Incomplete or ambiguous guard manifest")
        }
        for name in ["host-sandbox.c", "process-guard.c"] {
            guard files[checkout.appendingPathComponent("tools/taverna/ios/\(name)").path] != nil else {
                throw PreparationError.invalid("Guard source does not belong to this checkout")
            }
        }
        let directory = URL(fileURLWithPath: try required("TAVERNA_UI_ATTEMPT")).appendingPathComponent("guard-events")
        try Self.requireOwned(directory, root: checkout)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        log = directory.appendingPathComponent("app-\(UUID().uuidString).jsonl")
        guard !FileManager.default.fileExists(atPath: log.path) else {
            throw PreparationError.invalid("Existing guard evidence must be preserved")
        }
        try validateFiles()
        let library = try component("process-guard.dylib")
        let host = try component("host-sandbox")
        app.launchEnvironment["DYLD_INSERT_LIBRARIES"] = library.path
        app.launchEnvironment["TAVERNA_HOST_GUARD"] = host.path
        app.launchEnvironment["TAVERNA_GUARD_LOG"] = log.path
    }

    private static func requireOwned(_ url: URL, root: URL) throws {
        guard url.resolvingSymlinksInPath().path.hasPrefix(root.path + "/") else {
            throw PreparationError.invalid("Instrumentation path outside worktree: \(url.path)")
        }
    }

    private func component(_ name: String) throws -> URL {
        let matches = files.keys.filter { URL(fileURLWithPath: $0).lastPathComponent == name }
        guard matches.count == 1 else { throw PreparationError.invalid("Missing \(name)") }
        return URL(fileURLWithPath: matches[0])
    }

    private func validateFiles() throws {
        for (path, expected) in files {
            let url = URL(fileURLWithPath: path)
            try Self.requireOwned(url, root: root)
            let digest = SHA256.hash(data: try Data(contentsOf: url))
                .map { String(format: "%02x", $0) }.joined()
            guard digest == expected else {
                throw PreparationError.invalid("Guard hash mismatch: \(path)")
            }
        }
    }

    func launch() throws {
        try validateFiles()
        let previous = FileManager.default.fileExists(atPath: log.path) ? try Data(contentsOf: log).count : 0
        app.launch()
        let deadline = Date().addingTimeInterval(5)
        while Date() < deadline {
            if FileManager.default.fileExists(atPath: log.path) {
                let data = try Data(contentsOf: log)
                for line in data.dropFirst(previous).split(separator: 10) {
                    let proof = Data(line)
                    let event = try JSONDecoder().decode(GuardEvent.self, from: proof)
                    guard event.pid > 0, event.executable == "SimpleX", event.phase == "before_main",
                          [Int(EPERM), Int(EACCES)].contains(event.ipv4_errno),
                          [Int(EPERM), Int(EACCES)].contains(event.ipv6_errno), event.loopback else {
                        throw PreparationError.invalid("Invalid before-main containment proof")
                    }
                    XCTContext.runActivity(named: "Before-main network containment") { activity in
                        let attachment = XCTAttachment(data: proof, uniformTypeIdentifier: "public.json")
                        attachment.name = "app-before-main-\(event.pid)"
                        attachment.lifetime = .keepAlways
                        activity.add(attachment)
                    }
                    return
                }
            }
            Thread.sleep(forTimeInterval: 0.05)
        }
        throw PreparationError.invalid("No new before-main containment proof for this launch")
    }
}
