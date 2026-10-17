import XCTest

// A separate qualification, without filtering or changing the first-build suite.
final class TavernaShareTests: XCTestCase {
    func testSystemShareExtension() throws {
        continueAfterFailure = false
        let session = try TavernaUITestSession()
        let app = session.app
        app.launchEnvironment["TAVERNA_SHARE_HOST"] = "1"
        try session.launch()
        let button = app.buttons["Share qualification"]
        XCTAssertTrue(button.waitForExistence(timeout: 15))
        button.tap()
        let apps = app.cells.matching(identifier: "shareCell")
        var share = apps.matching(NSPredicate(format: "label == %@", "SimpleX")).firstMatch
        if !share.waitForExistence(timeout: 5) || !share.isHittable {
            let more = apps.matching(NSPredicate(format: "label IN %@", ["More", "Mais"])).firstMatch
            XCTAssertTrue(more.waitForExistence(timeout: 5), app.debugDescription)
            XCTAssertTrue(more.isHittable, app.debugDescription)
            more.tap()
            let hierarchy = XCTAttachment(string: app.debugDescription)
            hierarchy.name = "System activities after More"
            hierarchy.lifetime = .keepAlways
            add(hierarchy)
            // The More sheet uses unlabeled table cells; select the visible
            // activityTitleLabel rather than the carousel behind the sheet.
            let row = app.staticTexts.matching(identifier: "activityTitleLabel").matching(NSPredicate(format: "label == %@", "SimpleX")).firstMatch
            XCTAssertTrue(row.waitForExistence(timeout: 10), app.debugDescription)
            XCTAssertTrue(row.isHittable, app.debugDescription)
            row.tap()
        } else {
            share.tap()
        }
        let path = try XCTUnwrap(ProcessInfo.processInfo.environment["TAVERNA_SHARE_CONFIG"])
        let receipt = URL(fileURLWithPath: path).deletingLastPathComponent().appendingPathComponent("share-result.json")
        let deadline = Date().addingTimeInterval(90)
        while !FileManager.default.fileExists(atPath: receipt.path) && Date() < deadline {
            Thread.sleep(forTimeInterval: 0.2)
        }
        XCTAssertTrue(FileManager.default.fileExists(atPath: receipt.path), app.debugDescription)
        let result = try JSONSerialization.jsonObject(with: Data(contentsOf: receipt)) as! [String: Any]
        XCTAssertEqual(result["status"] as? String, "PASS", String(describing: result["failure"]))
        XCTAssertEqual(result["process"] as? String, "SimpleX SE")
        let attachment = XCTAttachment(screenshot: app.screenshot())
        attachment.name = "System Share Extension qualification"
        attachment.lifetime = .keepAlways
        add(attachment)
        app.terminate()
    }
}
